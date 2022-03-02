# -*- python -*-
#
#       vplants.mars_alt.mars.fusion
#
#       Copyright 2006-2011 INRIA - CIRAD - INRA
#
#       File author(s): Eric Moscardi <eric.moscardi@gmail.com>
#                       Daniel BARBEAU <daniel.barbeau@inria.fr>
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#       http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
#
#       OpenAlea WebSite : http://openalea.gforge.inria.fr
#
################################################################################

__license__= "Cecill-C"
__revision__ = " $Id$ "


import numpy as np
import platform
from math import ceil
from collections import namedtuple
from openalea.image.registration.matrix import identity
from openalea.image.spatial_image       import SpatialImage
from openalea.image.serial.basics       import lazy_image_or_path
from openalea.image.algo.basic          import color2grey
from vplants.asclepios.vt_exec.reech3d  import reech3d, resample, reech3d_voxels
from openalea.image.serial.basics import imread, imsave


__all__ = ["fusion", "fusion_task", "original_fusion", "attenuation"]
from openalea.core.logger import get_logger
mylogger = get_logger(__name__)


####################################################################
# What comes is the reimplementation of the fusion algorithm to be #
# iterative, and to load images lazily and release them as soon    #
# as possible. It also provides a trick to compute masks           #
# faster, except it does have a small flaw.                        #
####################################################################


def histogram(image, nbins=256):
    """Return histogram of image.
        
        Unlike `np.histogram`, this function returns the centers of bins and
        does not rebin integer arrays. For integer arrays, each integer value has
        its own bin, which improves speed and intensity-resolution.
        
        Parameters
        ----------
        image : array
        Input image.
        nbins : int
        Number of bins used to calculate histogram. This value is ignored for
        integer arrays.
        
        Returns
        -------
        hist : array
        The values of the histogram.
        bin_centers : array
        The values at the center of the bins.
        """
    
    # For integer types, histogramming with bincount is more efficient.
    if np.issubdtype(image.dtype, np.integer):
        offset = 0
        if np.min(image) < 0:
            offset = np.min(image)
        hist = np.bincount(image.ravel() - offset)
        bin_centers = np.arange(len(hist)) + offset
        
        # clip histogram to start with a non-zero bin
        idx = np.nonzero(hist)[0][0]
        return hist[idx:], bin_centers[idx:]
    else:
        hist, bin_edges = np.histogram(image.flat, nbins)
        bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2.
        return hist, bin_centers


def threshold_otsu(image, nbins=256):
    """Return threshold value based on Otsu's method.
        
        Parameters
        ----------
        image : array
        Input image.
        nbins : int
        Number of bins used to calculate histogram. This value is ignored for
        integer arrays.
        
        Returns
        -------
        threshold : float
        Threshold value.
        
        References
        ----------
        .. [1] Wikipedia, http://en.wikipedia.org/wiki/Otsu's_Method
        
        Examples
        --------
        >>> from skimage.data import camera
        >>> image = camera()
        >>> thresh = threshold_otsu(image)
        >>> binary = image > thresh
        """
    hist, bin_centers = histogram(image, nbins)
    hist = hist.astype(float)
    
    # class probabilities for all possible thresholds
    weight1 = np.cumsum(hist)
    weight2 = np.cumsum(hist[::-1])[::-1]
    # class means for all possible thresholds
    mean1 = np.cumsum(hist * bin_centers) / weight1
    mean2 = (np.cumsum((hist * bin_centers)[::-1]) / weight2[::-1])[::-1]
    
    # Clip ends to align class 1 and class 2 variables:
    # The last value of `weight1`/`mean1` should pair with zero values in
    # `weight2`/`mean2`, which do not exist.
    variance12 = weight1[:-1] * weight2[1:] * (mean1[:-1] - mean2[1:])**2
    
    idx = np.argmax(variance12)
    threshold = bin_centers[:-1][idx]
    return threshold

def logit(x, length, m=.5, s=.1, max_val=1):
    return max_val*(1 - (np.exp((np.float32(x)/length-m)/s)/(np.exp((np.float32(x)/length-m)/s)+1)))

def exp_sqrt_func(x, length, speed=2):
    return 1.1-np.exp(-((np.float32(x)*speed/length)**2))

def exp_func(x, length=1000, speed=10):
    return 1.1-np.exp(-((np.float32(x)*speed/length)))

def calc_coeffs(im, th=None):
    if th==None:
        th = threshold_otsu(im)
    im_th=np.zeros_like(im)
    im_th[im>th]=1
    # -- Along 1st light sheet
    im_th_sum=np.zeros_like(im, dtype=np.float32)
    #for s in range(1, im_th.shape[1]):
    #    im_th_sum[:,s,:] = im_th_sum[:,s-1,:] + im_th[:,s,:]
    # -- Along 2nd light sheet    
    #im_th_sum_tmp=np.zeros_like(im)
    #for s in range(1, im_th.shape[1]):
    #    im_th_sum_tmp[:,-s-1,:] = im_th_sum_tmp[:,-s,:] + im_th[:,-s-1,:]
    #im_th_sum=im_th_sum_tmp+im_th_sum
    # -- Along Camera axis
    im_th_sum_tmp=np.zeros_like(im)
    for s in range(1, im_th.shape[2]):
        im_th_sum_tmp[:,:,s] = im_th_sum_tmp[:,:,s-1] + im_th[:,:,s]
    im_th_sum=im_th_sum_tmp+im_th_sum
    
    del im_th_sum_tmp
    mask = exp_func(im_th_sum, np.max(im_th_sum))
    return mask


def fusion_task(image, matrices=[], deformation=None):
    """Creates a task to be fed as input for the `fusion` function.

    This function only creates the association between an image and the resampling
    transforms that must be applied to it to fuse it with others. The actual resampling
    is done by `fusion`.

    :Parameters:
     - `image` (|SpatialImage|, str) - the image (or path to it) to resample.
     - `matrices` (np.ndarray, list [of np.ndarray]) - single 4*4 resampling matrix
                  or chain of resampling matrices to apply to the image. The matrices are
                  composed from left to right. MAT=matrices[0] o matrices[1] ...
     - `deformation` (|SpatialImage|) - a vector field.

    :Returns:
     - `fuse_task` (ImageFuseTask) - an association of the image and its transformations.
    """
     # -- In visualea, matrices can be None or a single matrix instead of a list.
    # fortunately, we're type-paranoid and we can test this! --
    if matrices is None:
        matrices = []
    elif isinstance(matrices, np.ndarray) and matrices.shape == (4,4):
        matrices = [matrices]
    else:
        assert isinstance(matrices, (list, tuple))
        matrices = assert_matrix_list_types(matrices)
    return ImageFuseTask(image, matrices[:], deformation)


def fusion( tasks, care_for_memory=True, cast="auto", min_vs=None, 
            output_intermediate=False, z_att_f=None, interpolation="linear",
            use_ref_canvas = True, use_ref_im=True, attenuation=False,
            # THIS ONE SHOULD NOT STAY HERE VERY LONG, JUST FOR TESTING!
            __use_alternate_m = False) :
    """ Fuses n (0<n<256) images into one single high resolution image.

    The final isotropic voxel size is obtained by finding the finest voxel size (min_vs) of all dimensions
    of each image in each task. The final resolution is obtained by dividing the real domain of the reference image
    by min_vs (TODO: update this when optimial canvas size computation in implemented).

    :Parameters:
     - `tasks` (ImageFuseTask, list [of ImageFuseTask]) - Resampling parameters of each image to fuse
                                                          (construct them with fusion_task).
     - `care_for_memory` (bool) - Trigger a strategy to only load one image at a time if the images in the tasks are paths.
     - `cast` (str, :class:`~np.dtype`, :class:`~types.NoneType`) - "auto", a np.dtype or None. Output type of the image.
                                          "auto" will take the type with the minimum byte size that correcly encodes the image.
                                          This clamps the value's bits to the destination bit size.
     - `min_vs` (float) - if not None, defines the isotropic voxelsize for the result image (how refined it will be). If None
                          it is deduced automatically.
     - `output_intermediate` (bool) - output resampled images (source images with transforms applied).
     - `z_att_f` (function) - a function that evaluates in the [0,1] interval and whose images are also in that interval.
                              If not None, it will be used as a decay function to diminish the contribution of slices of
                              higher depth to the final image. See :class:`~vplants.mars_alt.mars.fusion.attenuation` for
                              some ready-to-use functions.
     - `interpolation` (str) - Resampling interpolation method: "linear", "nearest".
     - `use_ref_canvas` (bool) - Don't compute the optimal canvas size, use canvas of same real size and reference image.
    :Returns:
     - `fused` (|SpatialImage|) - The super-resolution image.
     - `interm` (list [of |SpatialImage|]) - resampled images if output_intermediate is True, else or None

    :Details:

    We are fusing together images that are in different spaces, voxelsizes and resolutions
    into one single image of higher resolution and isotropic voxelsizes.
    We have one reference image and several floating images to "overlay" upon the
    reference image. The final resolution is superior to the original resolution of each image.

    For each task we have the reference image (image_1) and the floating image (image_2).
    The registration process computed the transformation T that registers image_2 (floating)
    on image 1 (reference). T is an application from B2 (the basis of image 2 defined by its voxelsizes)
    to B1 (the basis of image 1 defined by its voxelsizes). For computational reasons we do not consider
    T but T_inv and we call T_inv a **resampling transformation (matrix, deformation field)**.

    Also, the application P1 lets us move from B1 to B_Real. It is diag([vs_1_x, vs_1_y, vs_1_z, 1.0]).
    Its inverse, P1_inv, lets us move from B_Real to B1. Similarly, the application P2 lets us move
    from B2 to B_Real. It is diag([vs_2_x, vs_2_y, vs_2_z, 1.0]) and its inverse, P2_inv, lets us move
    from B_Real to B2.

    Matrices given through the tasks are 4*4 **T_inv resampling matrices**.

    Deformation fields given through the tasks are **T_inv resampling fields**.
    For the deformation field to be correcly applied during the resampling
    it needs to be "corrected" by a homothety matrix that converts voxel indices
    of the final image to voxel indices in the vector field. This matrix is P_res
    and is diag([vs_flo_x/vs_fin_x, vs_flo_y/vs_fin_y, vs_flo_z/vs_fin_z, 1]) and is the inverse
    of P_res_inv. Since this is a resampling process, we actually use P_res_inv.

    .. note::

        Of all the matrices named above, fusion only actually uses `P_res_inv`.


    :See:
     - :func:`~vplants.asclepios.vt_exec.reech3d.reech3d_voxels`

    """
    # -- In visualea, tasks can be an ImageFuseTask instead of a list
    # fortunately, we're type-paranoid and we can test this! --
    if isinstance(tasks, ImageFuseTask):
        tasks = [tasks]
    else:
        assert isinstance(tasks, (list, tuple))
        assert_task_list_types(tasks)

    ref_index = 0 #const! : index of the reference image data in different tables
    n_tasks = len(tasks)
    
    # get meta info from tasks and load task's images if necessary.
    # wci = worst case intensity = highest intensity possible in intensity-normalized image    
    shapes, voxelsizes, wci, common_dtype, tasks = get_images_metainfos_from_tasks(tasks, care_for_memory)
    
    # The return type is determined once and for all!
    optimal_dt = minimum_size_dtype_for_required_capacity(base_dt=common_dtype, max_=wci)
    print optimal_dt
    # -- find out the finest voxel size of all images and the dimension that bears it --
    if not min_vs:
        min_vs_and_dim = min( (res[i],i) for i in range(3) for res in voxelsizes )
        min_vs = min_vs_and_dim[0]

    # -- retreive the reference image vsize and shape info --
    ref_vs  = voxelsizes[ref_index]
    ref_sha = shapes[ref_index]

    # -- the final image has homogeneous vsizes --
    fin_vs = (min_vs,)*3
    ref_fin_sha = [ ceil(ref_sha[i]*ref_vs[i]/min_vs) for i in range(3) ]
    offset = None
    if not use_ref_canvas:
        # Compute the optimal canvas size. Apply the matrices to each bounding box
        # and take the bounding box of all bounding boxes.
        fin_sha, offset = optimal_canvas_size(shapes, voxelsizes, tasks, fin_vs)
        # we need a resampling offset so:
        offset = -offset
    
    
    # check that we can allocate this size, or fix it to something allocatable.
    if use_ref_canvas:
        fin_sha = ref_fin_sha
    elif platform.architecture()[0].startswith("32"):
        n_vox = fin_sha[0] * fin_sha[1] * fin_sha[2]
        vx_bytes = n_vox * optimal_dt().itemsize
        n_images = 2 if care_for_memory else n_tasks + 1
        req_mem  = vx_bytes * n_images
        # if required memory exceeds 2 gigabytes, 
        # use canvas with same bbox as reference image.
        if req_mem > 1.5e9:
            # compute the optimal super-resolution using reference image space.
            # For each dimension it is equal to s_d * vs_d / min_vs, 
            # where s_d is the pixel size of the dimension and vs_d is the
            # voxel size in that dimension.
            fin_sha = ref_fin_sha
    else:
        print "ugh?"
    print "using %s canvas size."%(fin_sha)
    
    # uint8 is enough : you wont add up more than 256 images! 
    # You wont have the memory for it! Or you will die before it finishes.
    

    # store intermediate data
    interm = None
    if output_intermediate:
        interm = []

    # -- resample images into new orientation and resolution --
    res_im      = None #the resampled result
    deformation = None #the deformation field if any
    if not use_ref_im:
        tasks.pop(0)
        n_tasks-=1
    if n_tasks>1 :
        if attenuation:
            mask = np.zeros(fin_sha, dtype=np.float32)
            im_tmp, im_was_path = lazy_image_or_path(tasks[0].image)
            th = threshold_otsu(im_tmp)
            if im_was_path:
                del im_tmp
        else:
            mask = np.zeros(fin_sha, dtype=np.uint8)
        print "Begining of the precomputation of the mask"  
        # --- Computation of the sum of weights for the result image.
        for i, task in enumerate(tasks):
            cur_im, im_was_path = lazy_image_or_path(task.image)
            if attenuation:
                cur_mask = calc_coeffs(cur_im, th)
            else :
                cur_mask = np.ones_like(cur_im, dtype=np.uint8)
            vs = cur_im.voxelsize
            im_min_vs, min_dim = min( (vs[i],i) for i in range(3) )
            # reduce all matrices to a single one.
            # TODO : compose_task_matrices currently doesn't use init_trans, make it use it
            mat = compose_task_matrices(task, src_space=ref_vs, target_space=vs, init_trans=offset)
            # -- the vector field --
            deformation = task.deformation
            # -- deformation can also be a path to an image, isn't this beautifully consistent? ;) --
            if deformation is not None:
                deformation, def_was_path = lazy_image_or_path(deformation)
    
            p_res = np.diag( np.array(cur_im.voxelsize+(1,))/np.array(fin_vs+(1,)) ) # :scale
            trans_res   = (0.5, 0.5, 0.5, 1.0) # centering
            p_res[:,3]  = np.multiply( p_res.diagonal(), trans_res)
            p_res_inv   = np.linalg.inv(p_res)
            # -- ok, all that could be condensed but at least the maths are explicit --

            if deformation is None and mat is not None:
                # -- we must correct the matrix as it is in voxels and that reech3d doesn't
                # use homothety matrix if no vector field is given --
                mat = np.dot(mat, p_res_inv)
            res_mask = reech3d_voxels(cur_mask,
                                    mat          = mat,
                                    deformation  = deformation,
                                    mat_before   = p_res_inv,
                                    output_shape = fin_sha,
                                    vout         = fin_vs,
                                    vin          = cur_im.voxelsize,
                                    interpolation = interpolation)
            mask+=res_mask
            imsave("mask_"+str(i)+".inr", res_mask)
            del res_mask
            if im_was_path:
                del cur_im
    
    imsave("test.inr", SpatialImage(mask))
    print "mask saved"
    # -- the resampled results will be summed into these buffers.
    # We create the final image by summing the intensities and dividing by the number
    # of contributions per pixel. This is done by summing masks of the images.
    # The masks are made out of the resampled images: whatever is not zero becomes one.
    # The highest intensity is *wci*. An optimal dtype for wci has already been obtained
    # TODO :  check undeflow risk!    
    if attenuation:
        result = np.zeros(fin_sha, dtype=np.float32)
    else:
        result = np.zeros(fin_sha, dtype=optimal_dt)
    
    print "Start processing fusion"
    for i, task in enumerate(tasks):
        # -- like we said, task.image can still be a path if care_for_memory is False --
        cur_im, im_was_path = lazy_image_or_path(task.image)

        # -- if z_att_f is not none, use it to create an attenuation function in Z --
#        if attenuation:
#            cur_mask = imread("mask_"+str(i)+".inr")
#            cur_im = SpatialImage(cur_im*cur_mask, voxelsize=cur_im.voxelsize, dtype=cur_im.dtype)
#        else :
#            cur_mask = np.ones_like(cur_im)

        vs = cur_im.voxelsize
        im_min_vs, min_dim = min( (vs[i],i) for i in range(3) )

        # reduce all matrices to a single one.
        # TODO : compose_task_matrices currently doesn't use init_trans, make it use it
        mat = compose_task_matrices(task, src_space=ref_vs, target_space=vs, init_trans=offset)
        # -- the vector field --
        deformation = task.deformation
        # -- deformation can also be a path to an image, isn't this beautifully consistent? ;) --
        if deformation is not None:
            deformation, def_was_path = lazy_image_or_path(deformation)
        # -- create a homothety matrix used to pass from final image indices
        # to [vector field indices and] floating image indices. This matrix also
        # puts the points in the center of voxels. We first compute the float-to-resampled
        # matrix and then invert --
        p_res = np.diag( np.array(cur_im.voxelsize+(1,))/np.array(fin_vs+(1,)) ) # :scale
        trans_res   = (0.5, 0.5, 0.5, 1.0) # centering
        p_res[:,3]  = np.multiply( p_res.diagonal(), trans_res)
        p_res_inv   = np.linalg.inv(p_res)
        # -- ok, all that could be condensed but at least the maths are explicit --

        if deformation is None and mat is not None:
            # -- we must correct the matrix as it is in voxels and that reech3d doesn't
            # use homothety matrix if no vector field is given --
            mat = np.dot(mat, p_res_inv)

        res_im = reech3d_voxels(cur_im,
                                mat          = mat,
                                deformation  = deformation,
                                mat_before   = p_res_inv,
                                output_shape = fin_sha,
                                vout         = fin_vs,
                                vin          = cur_im.voxelsize,
                                interpolation = interpolation)

        if output_intermediate:
            interm.append(res_im)

        # in place addition of pre-normalised image
        # this way there is no overflow, and later
        # we compensate. Memory efficient, type-preservation
        if n_tasks > 1:
            mask_res = imread("mask_"+str(i)+".inr")
            result += (res_im*mask_res) / mask
        else :
            result = res_im
        # -- cleanup --
        if im_was_path:
            del cur_im
        if deformation is not None and def_was_path:
            del deformation
        del res_im

    # -- convert the image to the desired output --
    if cast == "auto":
        return result
    elif issubclass(cast, np.number):
        result = cast(result)
    else:
        pass
    final = optimal_dt(result)
    final = SpatialImage(optimal_dt(final), resolution=fin_vs, dtype=optimal_dt)
    return final, interm



#############
# Utilities #
#############
def as_uint8(arr):
    """Doesn't cast, just modifies dtype -- really?"""
    return np.uint8(arr)

ImageFuseTask = namedtuple("ImageFuseTask", "image matrices deformation")

def numeric_base(dtype):    
    base = dtype.type.__base__
    while(base.__base__ != np.number):
        base = base.__base__
    return base
        
def assert_task_list_types(tasks):
    """Checks that all elements of tasks are ImageFuseTask,
    and that all task images are either paths or |SpatialImage|s"""
    for t in tasks:
        assert isinstance(t, ImageFuseTask)
        assert isinstance(t.image, (str, unicode, SpatialImage))

def assert_matrix_list_types(matrices):
    """Checks that all elements of matrices are np.ndarrays"""
    mats = []
    for m in matrices:
        if m is None:
            continue
        assert isinstance(m, np.ndarray)
        mats.append(m)
    return mats

def minimum_size_dtype_for_required_capacity(base_dt, max_ = None):
    max_ = max_ or float(image.max())
    base = base_dt.type.__base__
    if issubclass(base, (np.integer,)):
        info = np.iinfo
    elif issubclass(base, (np.core.numeric.inexact,)):
        info = np.finfo
    else:
        raise Exception("unhandled base type")
    types = [(info(t).max,t) for t in np.typeDict.itervalues() if
              issubclass(t, base)]
    types.sort()
    for t in types:
        if t[0] >= max_:
            return t[1]
        else:
            continue

def compose_task_matrices(task, src_space=None, target_space=None, init_trans=None):
    # -- all matrices given by task.matrices are VOXEL matrices --
    
    matrices = task.matrices
    mat = None
    if matrices is None or len(matrices)==0:
        print "no mat"
        mat = None
        if src_space is not None and target_space is not None:
            mat = identity(target_space, src_space)
    elif len(matrices)==1:
        print "one mat"
        mat = matrices[0]
    else:
        print "multi mat"
        # -- multiply all matrices for this task in order
        # because matrices are RESAMPLING matrices
        # (from reference space to floating space) --
        mat = reduce( np.dot, matrices)
    
    init_mat = None
    if init_trans is not None:
        print "TODO: Fix the init translation composition!"
        init_mat = np.identity(4)
        init_mat[:3,3] = init_trans
        print init_mat, init_trans
    return mat if init_mat is None else np.dot(mat, init_mat)
            
def get_images_metainfos_from_tasks(tasks, care_for_memory):
    shapes = []
    voxelsizes = []
    new_tasks = []
    wci = np.uint64(0) # worst case intensity
    dtype = None
    # -- To find out the final resolution + shape we
    # need to get that info from all images --
    for ta in tasks:
        # -- task images can be paths: this is useful to pass simply the path, let this
        # function allocate the memory and release it when done. --
        ta_im, was_path = lazy_image_or_path(ta.image)
        # if we had a SpatialImage or we care for memory, don't modify the task
        unchanged = not was_path or care_for_memory        
        shapes.append(ta_im.shape)
        voxelsizes.append(ta_im.voxelsize)
        wci   += ta_im.max()
        assert dtype == None or numeric_base(dtype) == numeric_base(ta_im.dtype)
        dtype  = ta_im.dtype        
        if unchanged:            
            new_tasks.append(ta)
        else:
            # -- if we don't care for memory and want speed, just store the image for later reuse--
            new_tasks.append( fusion_task(ta_im, ta.matrices, ta.deformation) )
    wci /= len(tasks)
    return shapes, voxelsizes, wci, dtype, new_tasks
            
def optimal_canvas_size(shapes, voxelsizes, tasks, fin_vs):
    bbox_min = [float("inf")]*3 
    bbox_max = [-float("inf")]*3 
    for shape, res, task in zip(shapes, voxelsizes, tasks):
        # -- all matrices given by task.matrices are VOXEL matrices --
        bbox_vox = (0.,0.,0.,1.), shape+(1,)
        mat = compose_task_matrices(task)
        if mat is not None:  
            bbox_vox = np.dot(mat, bbox_vox[0]), np.dot(mat, bbox_vox[1]),
        else:# (else is equivalent to identity)
            bbox_vox = np.array(bbox_vox[0]), np.array(bbox_vox[1]),        
        bbox_min = np.min( [bbox_vox[0][:3]*res, bbox_min], axis=0 )
        bbox_max = np.max( [bbox_vox[1][:3]*res, bbox_max], axis=0 )
    bbox_dims = bbox_max - bbox_min
    return np.uint32(bbox_dims / fin_vs), -bbox_min
    
#########################
# ATTENUATION FUNCTIONS #
#########################
class attenuation (object):
    @staticmethod
    def erf2(x):
        """ A negative error function for decay """
        from scipy.special import erf
        # erf expresses itself between roughly -3 and 3
        # and is strictly growing. x is between 0 and 1
        X = 3*x
        return np.power(erf(X)[::-1], 2)

    @staticmethod
    def gaussian(x):
        """ A gaussian decay"""
        from scipy.stats import norm
        # norm nears 0 towards 3.5
        X = x*3.5
        return norm.pdf(X)/norm.pdf(0)





###################################
# THE ORIGINAL VERSION COMES NEXT #
###################################


# Legacy implementation of the fusion process
class Fusion (object):
    """
    """
    def __init__(self,img,deformation):
        """
        - `img`(|SpatialImage|) - reference image
        """
        self.images_fusion = []
        self.masks = []

        if not isinstance(img,SpatialImage):
            mylogger.debug("convert to SpatialImage")
            self.img = SpatialImage(np.array(img,np.uint16))

        self.ref_img = img

        if deformation.ndim != 4 :
            mylogger.error("unable to read deformation")
            return -1

        self.ref_deformation = color2grey(deformation)

        vx,vy,vz = img.resolution

        x,y,z = img.shape
        self.output_shape = x,y,ceil((z*vz)/vx)

        h22 = vx/vz
        h23 = -0.5 * (1 - vx/vz)
        self.homothety = np.array([[ 1.,  0.,  0. ,  0.],
                                   [ 0.,  1.,  0. ,  0.],
                                   [ 0.,  0.,  h22, h23],
                                   [ 0.,  0.,  0. ,  1.]])

        self.resolution = vx,vy,h22

        #print "resampling"
        im_reech = reech3d( self.ref_img, deformation=self.ref_deformation, mat_before=self.homothety, output_shape=self.output_shape )
        im_reech.resolution = self.resolution

        #print "compute resampled mask by using the deforrmation"
        mask = SpatialImage(np.ones(self.output_shape, dtype=np.uint8))
        #mask_reech = reech3d( mask, deformation=self.ref_deformation, mat_before=self.homothety, output_shape=self.output_shape, interpolation="nearest" )
        mask.resolution = self.resolution

        # -- avoid overflow --
        if im_reech.dtype != np.uint16 :
            mylogger.debug("cast to 'uint16'")
            im_reech = np.uint16(im_reech)

        # if mask.dtype != np.uint16 :
        #     mylogger.debug("cast to 'uint16'")
        #     mask = np.uint16(mask)


        self.images_fusion.append( im_reech )
        self.masks.append(mask)


    def _resampling(self,img,matrix,deformation):
        """
        - `img`(|SpatialImage|) - image
        - `matrix`(ndarray) - transformation matrix
        - `deformation` (ndarray) - vector field based shape deformation

        :Returns:
            im_reech,
            mask_reech
        """
        if matrix.shape != (4,4) :
            mylogger.error("unable to read matrix")
            return -1

        if deformation.ndim != 4 :
            mylogger.error("unable to read deformation")
            return -1

        mylogger.info("compute the resampled image by using the deforrmation")
        deformation = color2grey(deformation)

        if not isinstance(img,SpatialImage):
            mylogger.debug("convert to SpatialImage")
            img = SpatialImage(img)

        #print "resampling"
        im_reech = reech3d( img, deformation=deformation, mat=matrix, inv=False, mat_before=self.homothety, output_shape=self.output_shape )
        im_reech.resolution = self.resolution

        #print "compute resampled mask by using the deforrmation"
        mask = SpatialImage(np.ones(img.shape, dtype=np.uint8))
        mask_reech = reech3d( mask, deformation=deformation, mat=matrix, inv=False, mat_before=self.homothety, output_shape=self.output_shape, interpolation="nearest" )
        mask_reech.resolution = self.resolution

        return im_reech,mask_reech


    def add_image (self,img,matrix,deformation):
        """
        """
        # if img.dtype != np.uint16 :
        #     mylogger.debug("cast to 'uint16'")
        #     img = np.uint16(img)

        # mask = SpatialImage(np.ones_like(img))
        # if mask.dtype != np.uint16 :
        #     mylogger.debug("cast to 'uint16'")
        #     mask = np.uint16(mask)

        resampled_img, mask = self._resampling(img,matrix,deformation)

        self.images_fusion.append(resampled_img)
        self.masks.append(mask)

    def fuse(self):
        """Adds all the masks, adds all the images, an divides them elementwise.
        Returns a fused image.
        """
        mylogger.info("creating of mask of fusion")
        mask_fusion = sum(self.masks)

        mylogger.info("compute the sum of images")
        image_fusion = sum(self.images_fusion)

        mylogger.info("compute the mean of images")
        fusion = image_fusion / mask_fusion
        #fusion = np.uint8(np.round(fusion))             #Slows down the code but may yet prove necessary

        return fusion

def original_fusion(im_ref,def_ref,images,matrices,deformations):
    """First version of the np+Reech3D image fusion algorithm.

    This function computes a super-resolution image out of
    a set of images and transformations.

    :Note:
    This function is kept for backwards compatibility. It is ressource
    intensive.

    :Parameters:
    - `im_ref` (|SpatialImage|) - the image that served
       as a reference.
    - `def_ref` (|SpatialImage|) - a deformation field
       to apply to the ref image.
    - `images` (list [of |SpatialImage|]]) - a list of images to
       resample and merge with the reference image
    - `matrices` (list-of-4x4-np.ndarray) - list of resampling matrices
       (must have the same length as `images`).
    - `deformations` (list [of |SpatialImage|]) - a list of deformation
       fields  (must have the same length as `images`).


    """
    f = Fusion(im_ref,def_ref)
    for img,mat,deform in zip(images,matrices,deformations):
        f.add_image(img,mat,deform)
    imFus = f.fuse()
    return imFus

