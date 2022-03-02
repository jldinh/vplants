# -*- python -*-
# -*- coding: latin-1 -*-
#
#       vplants.mars_alt.mars.reconstruction
#
#       Copyright 2006 - 2011 INRIA - CIRAD - INRA
#
#       File author(s): Eric MOSCARDI <eric.moscardi@gmail.com>
#                       Daniel BARBEAU <daniel.barbeau@inria.fr>
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#       http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
#
#       OpenAlea WebSite : http://openalea.gforge.inria.fr
################################################################################

__license__= "Cecill-C"
__revision__ = " $Id$ "

from os.path import join
import numpy as np
import scipy.ndimage as ndimage
import types
from openalea.image.algo.basic    import stroke, end_margin
from openalea.image.algo.morpho   import connectivity_4,connectivity_6,connectivity_8, connectivity_26, component_labeling
from openalea.image.registration.matrix  import matrix_real2voxels
from openalea.image.serial.inrimage import write_inrimage
from openalea.image.spatial_image import SpatialImage

# -- imports used for registration --
from vplants.asclepios.vt_exec.baladin    import baladin
from vplants.asclepios.vt_exec.superbaloo import superbaloo, SuperBalooBinWrapper
from vplants.mars_alt.mars.fusion import fusion, fusion_task
from openalea.image.registration.registration  import pts2transfo
from openalea.image.serial.basics import lazy_image_or_path
from collections                  import namedtuple

#####################################################################################################################
# TODO : SPLIT THIS FILE INTO THREE :                                                                               #
#  - reconstruction_basic.py : "im2surface", "surface2im", "spatialise_matrix_points", "surface_landmark_matching", #
#                            "automatic_linear_registration", "automatic_non_linear_registration"                   #
#  - reconstruction_task.py (from reconstruction_basic import *): "reconstruction_task",                            #
#                           "surface_landmark_matching_parameters", "automatic_linear_parameters",                  #
#                           "automatic_non_linear_parameters", "reconstruct", "fuse_reconstruction".                #
#  - reconstruction.py (from reconstruction_basic import *; from reconstruction_task import *)                      #
#                                                                                                                   #
# This will make documentation a lot easier and will clearly separate concerns?                                     #
#####################################################################################################################

__all__ = ["im2surface", "surface2im", "spatialise_matrix_points", "surface_landmark_matching",
           "automatic_linear_registration", "automatic_non_linear_registration", "reconstruction_task",
           "surface_landmark_matching_parameters", "automatic_linear_parameters", "automatic_non_linear_parameters",
           "reconstruct", "fuse_reconstruction"]

def im2surface(image, threshold_value=45, only_altitude=False, front_half_only=False):
    """
    This function computes a surfacic view of the meristem, according to a revisited version
    of the method described in Barbier de Reuille and al. in Plant Journal.

    :Parameters:
        - `image` (|SpatialImage|) - image to be masked
        - `threshold_value` (int, float) - consider intensities superior to threshold.
        - `only_altitude` (bool) - only return altitude map, not maximum intensity projection
        - `front_half_only` (bool) - only consider the first half of all slices in the Z direction.

    :Returns:
        - `mip_img` (|SpatialImage|) - maximum intensity projection. *None* if only_altitude in True
        - `alt_img` (|SpatialImage|) - altitude of maximum intensity projection
    """
    image, was_path = lazy_image_or_path(image)
    resolution = image.resolution

    threshold = image >= threshold_value

    labeling, n = component_labeling(threshold, connectivity_26, number_labels=1)

    iterations = 15
    dilation1 = ndimage.binary_dilation(labeling, connectivity_8, iterations)
    del labeling

    iterations = 10
    erosion1 =  ndimage.binary_erosion(dilation1, connectivity_8, iterations, border_value=1)
    del dilation1

    iterations = 15
    dilation2 = ndimage.binary_dilation(erosion1, connectivity_8, iterations)
    del erosion1

    iterations = 4
    erosion2 =  ndimage.binary_erosion(dilation2, connectivity_4, iterations, border_value=1)
    del dilation2

    iterations = 15
    erosion3 =  ndimage.binary_erosion(erosion2, connectivity_8, iterations, border_value=1)
    del erosion2

    iterations = 1
    erosion4 =  ndimage.binary_erosion(erosion3, connectivity_6, iterations, border_value=1)

    #CONDITIONNER_POUR_ISOSURFACE
    mat1 = stroke(erosion4, 1)

    iterations = 3
    erosion5 =  ndimage.binary_erosion(mat1, connectivity_6, iterations, border_value=1)
    del mat1

    iterations = 9
    erosion6 =  ndimage.binary_erosion(erosion5, connectivity_8, iterations, border_value=1)
    del erosion5

    m_xor = np.logical_xor(erosion3, erosion6)
    del erosion3
    del erosion6

    #METTRE_A_ZERO_LES_DERNIERES_COUPES
    mat2 = end_margin(m_xor,10,2)
    del m_xor

    mat2 = np.ubyte(mat2)
    m_and = np.where(mat2 == 1, image, 0)
    del mat2

    if front_half_only:
        m_and[:,:,m_and.shape[2]/2:] = 0

    #ALTITUDE_DU_MIP_DANS_MASQUE_BINAIRE
    x,y,z = m_and.shape
    m_alt = m_and.argmax(2).reshape(x,y,1)

    del image
    if not only_altitude:
        m_mip = m_and.max(2).reshape(x,y,1)
        return SpatialImage(m_mip,resolution), SpatialImage(m_alt,resolution)
    else:
        return None, SpatialImage(m_alt,resolution)


def surface2im(points,altitude):
    """
    This function is used to convert points from maximum intensity projection
    to the real world.

    :Parameters:
        - `points` (list) - list of points from the maximum intensity projection
        - `altitude` (|SpatialImage|) - altitude of maximum intensity projection

    :Returns:
        - `coord` (list) - list of points in the real world
    """
    assert isinstance(altitude, SpatialImage)
    coord = list()

    vx = altitude.resolution[0]
    vy = altitude.resolution[1]
    vz = altitude.resolution[2]

    for pt in points:
        c = (pt[0]*vx, pt[1]*vy, (altitude[pt[0],pt[1],0])*vz)
        coord.append(c)
    return coord


def spatialise_matrix_points(points, image, mip_thresh=45):
    """
    Given a list of points in matrix coordinates (i.e. i,j,k - but k is ignored anyway),
    and a spatial image, returns a list of points in real space (x,y,z) with the Z coordinate
    recomputed from an altitude map extracted from image. This implies that `points` were placed
    on the mip/altitude map result of `im2surface` applied to `image` with `mip_thresh`.

    :Parameters:
        - `points` (list[ of tuple[of float,float,float], file) - 2D points to spatialise. Can also
                    be a filename pointing to a numpy-compatible list of points.
        - `image` (|SpatialImage|, str) - image or path to image to use to spatialise the points.
        - `mip_thresh` (int, float) - threshold used to compute the original altitude map for points.

    :Returns:
        - `points3d` (list [of tuple [of float, float, float]]) - 3D points in REAL coordinates.
    """
    image, was_path = lazy_image_or_path(image)
    if isinstance(points, (str, unicode)):
        points = np.loadtxt(points)
    return surface2im( points, im2surface(image, threshold_value=mip_thresh, only_altitude=True)[1] )


def surface_landmark_matching(ref, ref_pts, flo,  flo_pts,
                              ref_pts_already_spatialised=False,
                              flo_pts_already_spatialised=False,
                              mip_thresh=45):
    """ Computes the registration of "flo" to "ref" by minimizing distances between ref_pts and flo_pts.

    .. note::

    If `ref_pts_already_spatialised` and `flo_pts_already_spatialised` are True and `ref_pts` and
    `flo_pts` are indeed in real 3D coordinates, then this is exactly a landmark matching registration

    This function is implemented on top of
    :func:`~openalea.image.registration.registration.pts2transfo` .

    :Parameters:
     - `ref` (|SpatialImage|, str) - image or path to image to use to reference image.
     - `ref_pts` (list) - ordered sequence of 2D/3D points to use as reference landmarks.
     - `flo` (|SpatialImage|, str) - image or path to image to use to floating image
     - `flo_pts` (list) - ordered sequence of 2D/3D points to use as floating landmarks.
     - `ref_pts_already_spatialised` (bool) - If True, consider reference points are already in REAL 3D space.
     - `flo_pts_already_spatialised` (bool) - If True, consider floating points are already in REAL 3D space.
     - `mip_thresh` (int, float) - used to recompute altitude map to project points in 3D if they aren't spatialised.

    :Result:
     - `trs` (numpy.ndarray) - The result is a 4x4 **resampling voxel matrix**
                               (*i.e.* from ref to flo, from ref_space to flo_space
                               and NOT from real_space to real_space).
    """
    ref, was_path = lazy_image_or_path(ref)
    flo, was_path = lazy_image_or_path(flo)

    if isinstance(ref_pts, (str, unicode)):
        ref_pts = np.loadtxt(ref_pts)

    if isinstance(flo_pts, (str, unicode)):
        flo_pts = np.loadtxt(flo_pts)

    if not ref_pts_already_spatialised:
        print "spatialising reference"
        ref_spa_pts = spatialise_matrix_points(ref_pts, ref, mip_thresh=mip_thresh)
    else:
        print "not spatialising reference"
        ref_spa_pts = ref_pts

    if not flo_pts_already_spatialised:
        print "spatialising floating"
        flo_spa_pts = spatialise_matrix_points(flo_pts, flo, mip_thresh=mip_thresh)
    else:
        print "not spatialising floating"
        flo_spa_pts = flo_pts

    trs = pts2transfo(ref_spa_pts, flo_spa_pts)

    # -- trs is from ref to flo, in other words it is T-1,
    # a resampling matrix to put flo into ref space. ref_pts and
    # flo_pts are in real coordinates so the matrix is also in
    # real coordinates and must be converted to voxels --
    trs_vox = matrix_real2voxels(trs, flo.resolution, ref.resolution)
    return trs_vox


def automatic_linear_registration(ref, flo,
                                 initial_matrix           = None,
                                 transformation           = "rigid",
                                 estimator                = "ltsw",
                                 pyramid_levels           = 6,
                                 finest_level             = 0,
                                 least_trimmed_sq_cut = 0.55,
                                 variance_fraction        = 1.
                                 ):
    """ A registration that yields a linear registration matrix.

    Computes the registration of "flo" to "ref"
    using a pyramidal block matching strategy.
    The result is a resampling voxel matrix
    (from ref to flo, from ref_space to flo_space
    and NOT from real_space to real_space.

    This is an easy-to-use version of
    :func:`~vplants.asclepios.vt_exec.baladin.baladin`

    initial_matrix must be provided in
    ref_space -> flo_space direction and spaces, not real -> real.

    The result is a resampling 4x4 matrix (ref_space->flo_space direction and space).
    """
    assert isinstance(ref, SpatialImage)
    assert isinstance(flo, SpatialImage)

    # -- since we ask baladin to only compute the transform
    # (only_register = True), im will be None --
    im, trs = baladin(ref, flo,
                      inivox=initial_matrix,
                      transformation=transformation,
                      estimator=estimator,
                      auto=True,
                      rms=True,
                      #nbiter = 100,
                      pyn=pyramid_levels,
                      pys=finest_level,
                      ltscut=least_trimmed_sq_cut,
                      v=variance_fraction,
                      bld  = [10,10,10],
                      bldv = [10,10,10],
                      only_register = True)
    return trs


def automatic_non_linear_registration(ref, flo, initial_matrix,
                                      defo_field       = None,
                                      start_level      = 3,
                                      end_level        = 1,
                                      max_iterations   = 10,
                                      highest_fraction = 0.5,
                                      minimal_variance = 0.0,
                                      blockSize        = None,
                                      neighborhood     = None,
                                      similarity       = "cc",
                                      outlier_sigma    = 3,
                                      threads          = 1):
    """ A registration that yields a dense deformation field.

    Computes the registration of "flo" to "ref" also using a
    pyramidal block matching strategy
    but it returns a deformation field.

    .. warning::

        This function only works if Asclepios' SuperBaloo
        binary is installed on your computer (in the *PATH*).

    `initial_matrix` must be provided in ref_space -> flo_space
    direction and spaces, not real -> real.

    This is an easy-to-use wrapper of
    :func:`~vplants.asclepios.vt_exec.superbaloo.superbaloo`.

    """
    if not SuperBalooBinWrapper.available:
        raise Exception("Baloo unavailable")

    assert isinstance(ref, SpatialImage)
    assert isinstance(flo, SpatialImage)

    if initial_matrix is None and defo_field is None:
        initial_trsfs = None
    elif initial_matrix is None and defo_field is not None:
        initial_trsfs=[defo_field]
    elif initial_matrix is not None and defo_field is None:
        initial_trsfs=[initial_matrix]
    else:
        initial_trsfs=[initial_matrix, defo_field]

    return superbaloo(ref,
                      flo,
                      initial_trsfs=initial_trsfs,
                      start_level = start_level,
                      end_level   = end_level,
                      max_iterations = max_iterations,
                      highest_fraction = highest_fraction,
                      minimal_variance = minimal_variance,
                      blockSize = blockSize,
                      neighborhood = neighborhood,
                      similarity = similarity,
                      outlier_sigma = outlier_sigma,
                      threads = threads,
                      use_binary=True)





#############################
# A function to chew it all #
#############################
ImageReconstructTask   = namedtuple("ImageReconstructTask"  , "ref flo initialisation baladin_pars baloo_pars init_field")
ImageReconstructResult = namedtuple("ImageReconstructResult", "init_mat auto_linear_mat deformation")


def reconstruction_task(reference, floating, initialisation=None, auto_linear_params=None, auto_non_linear_params=None, initial_field=None):
    """Creates a task to be fed as input for the fusion function.

    A reconstruction task is the association of a reference image, a floating image to register on the reference image
    and parameters for the registration algorithms. This function simply creates this association. To actually execute
    the registration, the reconstruction task needs to be passed to `reconstruct`. First the initialisation step will
    be executed, then, if *auto_[...]_params* parameters are not *None*, they will be operated (first linear, then non
    linear)

    :Parameters:
     - `reference` (|SpatialImage|, str) - Image or path to image to use as the reference.
     - `floating` (|SpatialImage|, str) - Image or path to image to use as the floating.
     - `initialisation` (surface_landmark_matching_parameters, numpy.ndarray) - a set of parameters to compute an initial
                        matrix, or a 4x4 resampling (ref_space to flo_space) matrix. Will be used as an initialisation
                        of the automatic registration algorithms). Can be None if no initialisation is needed.
     - `auto_linear_params` (automatic_linear_parameters) - parameters to run an automated linear registration. Can be
                        *None* if no automatic linear registration is to be done.
     - `auto_non_linear_params` (automatic_non_linear_parameters) - parameters to run an automated non linear registration.
                        Can be  *None* if no automatic non linear registration is to be done.
     - `initial_field` (|SpatialImage|) - A vector field to initialise the non-linear registration (cumulates on top of any linear registration), or None.

    :Returns:
     - task (:class:`~vplants.mars_alt.mars.reconstruction.ImageReconstructTask`) - an association of reference image, floating image and parameters to register floating
                                     on reference.


    .. warning ::

        The auto_non_linear_params will only be taken into account
        if Asclepios' *SuperBaloo* executale is available.

    """
    assert initialisation is None or isinstance(initialisation, (np.ndarray, __RegistrationParams))
    assert auto_linear_params is None or isinstance(auto_linear_params, __RegistrationParams)
    assert auto_non_linear_params is None or isinstance(auto_non_linear_params, __RegistrationParams)
    assert initial_field is None or isinstance(initial_field, SpatialImage,)
    return ImageReconstructTask(reference, floating, initialisation, auto_linear_params, auto_non_linear_params,
                                initial_field)

class __RegistrationParams(object):
    """ A class used to store registration parameters. """
    pass

def surface_landmark_matching_parameters(ref_pts, flo_pts, spatialise_points=False, mip_threshold=45):
    """Create a landmark registration parameter set.

    See :func:`~vplants.mars_alt.mars.reconstruction.surface_landmark_matching`.

    :Parameters:
     - `flo_pts` (list) - Sequence of points on the floating image
     - `ref_pts` (list) - Sequence of points on the reference image
     - `spatialise_points` (bool) - If True, the given point lists are considered to be 2D, voxel-coordinate points.
                                    If False, the given points are considered to be 3D, in real coordinates.
     - `mip_threshold` (int, float) - Threshold to compute the altitude map if `spatialise_points` is True.
    """
    pars = __RegistrationParams()
    pars.ref_pts = ref_pts
    pars.flo_pts = flo_pts
    pars.spa_pts = spatialise_points
    pars.mip_thr = mip_threshold
    return pars

def automatic_linear_parameters(transfo_type="rigid", estimator="ltsw", pyramid_levels=6,
                                finest_level=0, lts_cut=0.55, variance_fraction=1.0):
    """Create an automatic linear registration parameter set.

    See :func:`~vplants.mars_alt.mars.reconstruction.automatic_linear_registration`.
    """
    pars = __RegistrationParams()
    pars.transformation        = transfo_type
    pars.estimator             = estimator
    pars.pyramid_levels        = pyramid_levels
    pars.finest_level          = finest_level
    pars.least_trimmed_sq_cut  = lts_cut
    pars.variance_fraction     = variance_fraction
    return pars

def automatic_non_linear_parameters(start_level      = 3,
                                    end_level        = 1,
                                    max_iterations   = 10,
                                    highest_fraction = 0.5,
                                    minimal_variance = 0.0,
                                    blockSize        = None,
                                    neighborhood     = None,
                                    similarity       = "cc",
                                    outlier_sigma    = 3,
                                    threads          = 1):
    """Create an automatic linear registration parameter set.

    See :func:`~vplants.mars_alt.mars.reconstruction.automatic_non_linear_registration`.
    """

    pars = __RegistrationParams()
    pars.start_level      = start_level
    pars.end_level        = end_level
    pars.max_iterations   = max_iterations
    pars.highest_fraction = highest_fraction
    pars.minimal_variance = minimal_variance
    pars.blockSize        = blockSize
    pars.neighborhood     = neighborhood
    pars.similarity       = similarity
    pars.outlier_sigma    = outlier_sigma
    pars.threads          = threads
    return pars

def reconstruct( tasks, fuse_kwargs=None, 
                 mean_reg_init=None, mean_reg_lin=None, 
                 mean_reg_non_lin=None, mean_reg_field=None,
                 multi_thread=False,
                 return_values=None
                 ):
    """ Given a list of reconstruction tasks, computes different registrations
    for each and returns a list of :class:`~vplants.mars_alt.mars.reconstruction.ImageReconstructResult`.

    If all tasks have the same reference image, you can directly pass the result of this
    function to `fuse_reconstruction` to obtain the fused, super-resolution image.

    :Warning:
      The current version skips one step by default. In fact, once we have the 
      transforms for each image, we should fuse them and register all images 
      (reference and floatings) to the fused (mean) image. To enableb this, pass
      a `fuse_kwargs` and at least one of the `mean_reg*`optional parameters.
    
    :Parameters:
     - `tasks` (:class:`~vplants.mars_alt.mars.reconstruction.ImageReconstructTask`, list [of :class:`~vplants.mars_alt.mars.reconstruction.ImageReconstructTask`]) - list of registrations to operate.
     - `fuse_kwargs` See: :func:`~vplants.mars_alt.mars.fusion.fusion` keyword args.
     - `mean_reg_init` (surface_landmark_matching_parameters, numpy.ndarray) - a set of parameters to compute an initial
                        matrix, or a 4x4 resampling (ref_space to flo_space) matrix. Will be used as an initialisation
                        of the automatic registration algorithms). Can be None if no initialisation is needed.
     - `mean_reg_lin` (automatic_linear_parameters) - parameters to run an automated linear registration. Can be
                        *None* if no automatic linear registration is to be done.
     - `mean_reg_non_lin` (automatic_non_linear_parameters) - parameters to run an automated non linear registration.
                        Can be  *None* if no automatic non linear registration is to be done.
     - `mean_reg_field` (|SpatialImage|) - A vector field to initialise the non-linear registration (cumulates on top of any linear registration), or None.
     
    See :func:`~vplants.mars_alt.mars.reconstruction.reconstruction_task`.

    :Returns:
     - `tasks` (:class:`~vplants.mars_alt.mars.reconstruction.ImageReconstructTask`, list [of :class:`~vplants.mars_alt.mars.reconstruction.ImageReconstructTask`]) - list of registrations used to operate.
     - `recon_results` (list [of :class:`~vplants.mars_alt.mars.reconstruction.ImageReconstructResult`]) - ordered list of results for each task. This contains
                                                             matrices, deformation fields etc...
    """

    # -- In visualea, tasks can be an ImageReconstructTask instead of a list
    # fortunately, we're type-paranoid and we can test this! --
    if isinstance(tasks, ImageReconstructTask):
        tasks = [tasks]
    else:
        assert isinstance(tasks, (list, tuple))
        assert_list_types(tasks, ImageReconstructTask)
 
    results = []
    reference_spatial_pts_cache = {}

    # ideally all tasks should have same reference image
    # might need an equality test! Comparing pointers is
    # not enough!
    common_ref = None
    
    for task in tasks:
        auto_lin_trs = None
        auto_field   = None
        init_mat     = None

        ref = task.ref
        flo = task.flo

        # -- ref and flo can be paths: this is useful to pass simply the path, let this
        # function allocate the memory and release it when done. However, if there is only
        # an initialisation matrix we don't load them --
        if not( task.initialisation is not None and isinstance(task.initialisation, np.ndarray) and \
                task.baladin_pars is None and task.baloo_pars is None):
            ref, was_path = lazy_image_or_path(ref)
            flo, was_path = lazy_image_or_path(flo)
            
        common_ref = ref

        if task.initialisation is not None:
            if isinstance(task.initialisation, __RegistrationParams):
                p = task.initialisation

                # -- The surface_landmark_matching can spatialise the points if needed. However
                # spatialisation is costly (compute the projection and altitude)
                # so we do it ourselve here and cache the results here --
                mip_thres = p.mip_thr
                if p.spa_pts is True:
                    ref_pts = reference_spatial_pts_cache.setdefault( ref, spatialise_matrix_points(p.ref_pts, ref,
                                                                                                    mip_thresh=mip_thres) )
                else:
                    ref_pts=p.ref_pts

                init_mat = surface_landmark_matching(ref, ref_pts, flo, p.flo_pts,
                                                     ref_pts_already_spatialised=True,
                                                     flo_pts_already_spatialised=not p.spa_pts)
                print "init_mat obtained by landmark matching"
            elif isinstance(task.initialisation, np.ndarray):
                init_mat = task.initialisation
                print "using provided init_mat"

        if task.baladin_pars is not None:
            p = task.baladin_pars
            auto_lin_trs = automatic_linear_registration(ref, flo,
                                                         initial_matrix           = init_mat,
                                                         transformation           = p.transformation,
                                                         estimator                = p.estimator,
                                                         pyramid_levels           = p.pyramid_levels,
                                                         finest_level             = p.finest_level,
                                                         least_trimmed_sq_cut     = p.least_trimmed_sq_cut,
                                                         variance_fraction        = p.variance_fraction
                                                         )

        if task.baloo_pars is not None:

            if not SuperBalooBinWrapper.available:
                print "skipping non-linear registration, SuperBaloo executable is missing"
            else:
                p = task.baloo_pars
                init_field = task.init_field
                if auto_lin_trs is not None:
                    print "initialising non-linear registration with auto-linear mat"
                    baloo_init_mat = auto_lin_trs
                else:
                    print "initialising non-linear registration with provided (or landmark-obtained) mat"
                    baloo_init_mat = init_mat
                auto_field = automatic_non_linear_registration(ref, flo,
                                                               baloo_init_mat,
                                                               defo_field = init_field,
                                                               start_level = p.start_level,
                                                               end_level = p.end_level,
                                                               max_iterations = p.max_iterations,
                                                               highest_fraction = p.highest_fraction,
                                                               minimal_variance = p.minimal_variance,
                                                               blockSize = p.blockSize,
                                                               neighborhood = p.neighborhood,
                                                               similarity = p.similarity,
                                                               outlier_sigma = p.outlier_sigma,
                                                               threads = p.threads
                                                               )

        results.append(ImageReconstructResult(init_mat, auto_lin_trs, auto_field))

        del ref
        del flo

    ###############################################################
    # MEAN INTENSITY & GEOMETRY REGISTRATION. REVIEW THIS PLEASE  #
    ###############################################################
    if (mean_reg_init is not None or \
        mean_reg_lin  is not None or \
        mean_reg_non_lin is not None or \
        mean_reg_field is not None) and fuse_kwargs:
        
        print "doing mean intensity registration"
        print "not doing mean geometry registration, at least I don't think so"
        fused, interm = fuse_reconstruction(tasks, results, **fuse_kwargs)
        
        new_tasks = []
        # -- first we create a new task to register the reference image of the previous
        # step to the new mean. See comment on common_ref--
        new_tasks.append( reconstruction_task( fused, common_ref, mean_reg_init, 
                                                mean_reg_lin, mean_reg_non_lin, mean_reg_field) )
    
        # Then we add the floating images.
        for t in tasks:
            new_tasks.append( reconstruction_task( fused, t.flo, t.initialisation, 
                                                   t.baladin_pars, t.baloo_pars, t.init_field) )
                                                   
        return reconstruct(new_tasks)
    else:
        print "Warning, didn't do registration to mean intensity and geometry image."
        print "This step is critical for non-linear registrations."
    if multi_thread:
        return_values[0] = tasks
        return_values[1] = results
    return tasks, results




def fuse_reconstruction( recon_tasks, recon_results, min_vs=None, cast="auto", output_intermediate=False, z_att_f=None, attenuation=False, 
                         interpolation="linear", use_ref_canvas = True, use_ref_im=True,
                         # THIS ONE SHOULD NOT STAY HERE VERY LONG, JUST FOR TESTING!
                         __use_alternate_m = False ):
    """ Given the output of `reconstruct`, will fuse the images into a super-resolution one.

    :Parameters:
     - `recon_tasks` (:class:`~vplants.mars_alt.mars.reconstruction.ImageReconstructTask`, list [of :class:`~vplants.mars_alt.mars.reconstruction.ImageReconstructTask`]) - list of registrations used to operate.
     - `recon_results` (list [of :class:`~vplants.mars_alt.mars.reconstruction.ImageReconstructResult`]) - ordered list of results for each task. This contains
                                                             matrices, deformation fields etc...
     - `cast` (str, :class:`~numpy.dtype`, :class:`~types.NoneType`) - "auto", a numpy.dtype or None. Output type of the image.
                                                                       "auto" will take the type with the minimum byte size that correcly encodes the image.
     - `output_intermediate` (bool) - output resampled images (source images with transforms applied).
     - `z_att_f` (function) - a function that evaluates in the [0,1] interval and whose images are also in that interval.
                              If not None, it will be used as a decay function to diminish the contribution of slices of
                              higher depth to the final image. See :class:`~vplants.mars_alt.mars.fusion.attenuation` for
                              some ready-to-use functions.
     See :func:`~vplants.mars_alt.mars.fusion.fusion` for details.

    :Returns:
     - `fused` (|SpatialImage|) - The super-resolution image.
     - `interm` (list [of |SpatialImage|) - None if output_intermediate is False else
                                                         list of unfused resampled images.
    """
    fuse_tasks = []
    if use_ref_im:
        ref_im = recon_tasks[0].ref
        for t in recon_tasks:
            if id(t.ref) != id(ref_im):
                raise Exception("All reconstruction tasks must have the same reference image to be fused")
        fuse_tasks.append( fusion_task(ref_im) )
        
    for t, res in zip(recon_tasks, recon_results):
        lm  = res.init_mat
        ar  = res.auto_linear_mat
        de  = res.deformation
        mats = []
        if ar is not None: #if we have a baladin matrix, use it, it includes init_mat
            mats.append(ar)
        elif lm is not None: #if we only have a landmark manual matrix then use it.
            mats.append(lm)
        else: # no matrix, that's no bug, we just resample the image to higher resolution.
            pass
        fuse_tasks.append(fusion_task(t.flo, mats, res.deformation))

    return fusion(fuse_tasks, min_vs=min_vs, cast=cast, 
                  output_intermediate=output_intermediate, z_att_f=z_att_f,
                  interpolation=interpolation, use_ref_canvas = use_ref_canvas, use_ref_im=True, __use_alternate_m = __use_alternate_m, attenuation=attenuation
                  )



def write_reconstruction_result(directory, radix, recon_res):
    if recon_res is not None:
        if recon_res.init_mat is not None:
            numpy.savetxt(pj(directory, radix+"_init_mat.txt"), recon_res.init_mat)
        if recon_res.auto_linear_mat is not None:
            numpy.savetxt(pj(directory, radix+"_auto_linear_mat.txt"), recon_res.auto_linear_mat)
        if recon_res.deformation is not None:
            write_inrimage(pj(directory, radix+"_deformation.inr.gz"), recon_res.deformation)




#############
# Utilities #
#############
def assert_list_types(theList, Type):
    for t in theList:
        assert isinstance(t, Type)

