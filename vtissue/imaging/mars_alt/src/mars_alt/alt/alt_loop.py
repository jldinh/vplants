# -*- python -*-
#
#       vplants.mars_alt.alt.mapping
#
#       Copyright 2006-2011 INRIA - CIRAD - INRA
#
#       File author(s): Daniel BARBEAU <daniel.barbeau@inria.fr>
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#       http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
#
#       OpenAlea WebSite : http://openalea.gforge.inria.fr
#
################################################################################


__license__ = "CeCILL v2"
__revision__ = " $Id: alt_loop.py 12060 2012-05-15 13:33:09Z chakkrit $ "



import os
import os.path
import numpy
from openalea.misc.temp import temp_name
from openalea.image.spatial_image import SpatialImage

from vplants.mars_alt.alt.mapping import mapping as lineage_mapping
from vplants.mars_alt.alt.candidate_lineaging import candidate_lineaging, equal_lineages, candidate_contains_expert
from vplants.mars_alt.alt.optimal_lineage import optimal_lineage
from vplants.mars_alt.alt.update_lineages import update_lineage
from vplants.mars_alt.alt.deformation_field import deformation_field

from vplants.mars_alt.mars.reconstruction import automatic_non_linear_parameters
from vplants.mars_alt.mars.reconstruction import reconstruction_task
from vplants.mars_alt.mars.reconstruction import reconstruct
from vplants.mars_alt.mars.fusion import fusion
from vplants.mars_alt.mars.fusion import fusion_task

from vplants.asclepios.vt_exec.superbaloo import superbaloo

from vplants.mars_alt.alt.alt_disk_memoize import alt_intermediate

REASON_MAXITER = "MAX_ITER" # ALT stopped because it iterated the maximum number of times
REASON_STABLE  = "STABLE"   # ALT stopped because it reached a stable mapping.
REASON_CANDIDATE_TEST_FAILED = "CANDIDATE_TEST_FAILED" # ALT stopped because the candidate_contains_expert test returned False.

def alt_loop(imgSeg0, imgSeg1, expert_map, tissue0, tissue1,
             imgFus0=None, imgFus1=None, mat_init=None, max_iter = 20,
             field_sigma = 5.0, non_linear_registration_params = None,
             mapping_dist=8.0, mapping_ndiv=8,
             mapping_candidate_method="cell_shape", mapping_flow_method="rf_flow",
             filter_params=[],
             strict_candidate_test = False,
             intermediate_data = None,
             ):
    """ The full lineaging loop.

    Given two segmented images and an expert (high confidence) lineage,
    this function will iteratively try to find the best lineage.

    .. note:: Image labels are expected to start from 2 (1 being the background and 0 reserved by segmentation)

    At each iteration the algorithm will :
     - [Optionally] Register imgSeg0 on imgSeg1 using expert lineage.
       This is important because the candidate lineages will be determined
       using spatial proximity of labels. Between two time steps the organ will
       have grown and this deformation must be accounted for.
     - Compute the candidate lineage in two steps :
       - Spatial neighboorhood estimation with cost
       - Optimization of costs using flow graphs algorithms.
     - Filtering of results by using biological lineage filtering rules.
     - Loop again : final lineage becomes expert lineage.

    The algorithm stops if the lineage at iteration N is equal to the lineage at iteration N-1
    or when `max_iter` iterations have been done.


    .. note ::

        If (imgFus0 and imgFus1 and non_linear_registration_params) and/or mat_init is provided,
        imgSeg0 is registered into imgSeg1 space. If only mat_init is provided then no non-linear
        registration will be operated. If imgFus0, imgFus1 and non_linear_registration_params are
        provided a non-linear registration will be done at each iteration and mat_init may serve
        to initialise this registration (usually obtained with `vplants.mars_alt.alt.alt_preparation`).
        The registration will be refined at each lineaging iteration as invalid lineages are removed.

        If none of these means to compute a non-linear registration are provided, the two images are
        considered to be already registered and the registration will **NOT** be optimized in the iterative
        process using the new high-confidence mappings.

    .. note::
        The order of filters in `filter_params` is not important.

    :Parameters:
     - `imgSeg0` (|SpatialImage|) - Segmented image of the organ at time 0
     - `imgSeg1` (|SpatialImage|) - Segmented image of the organ at time 1
     - `expert_map` (dict [of int: list [of int]]) - Segmented image of the organ at time 1
     - `tissue0` (openalea.celltissue.TissueDB) - Tissue representing organ at T0
     - `tissue1` (openalea.celltissue.TissueDB) - Tissue representing organ at T1
     - `imgFus0` (|SpatialImage|) - [Fused] image of the organ at time 0
     - `imgFus1` (|SpatialImage|) - [Fused] image of the organ at time 1
     - `mat_init` (numpy.ndarray) - 4x4 resampling matrix to register or initialise registration of
                                    imgSeg0 on imgSeg1
     - `max_iter` (int) - maximum number of iterations to do (prevent algorithm from never ending)
     - `field_sigma` (int) - if registration is to be done, size of the gaussian interpolation to smooth
                             initial vector field.
     - `non_linear_registration_params` (vplants.mars_alt.mars.reconstruction.automatic_non_linear_parameters) -
                             parameters for the non-linear registration, if any.
     - `mapping_dist` (float) - maximum distance from mother-to-child beyond which childs are disregarded.
     - `mapping_ndiv` (float) - maximum number of cell divisions between T0 and T1.
     - `mapping_candidate_method` (str) - Method to estimate candidate lineage : "cell_shape" or "cell_as_box".
     - `mapping_flow_method` (str) - Flow graph method : "rf_flow" or "nx_simplex".
     - `filter_params` (list [of vplants.mars_alt.alt.update_lineages.LineageFilterer) - Filter list to clean estimated lineage.

    """

    assert len(imgSeg0.shape) == len(imgSeg1.shape) == 3

    if max_iter == -1:
        max_iter = float("inf")

    mapping   = expert_map.copy()
    iteration = 0
    reason = REASON_MAXITER
    iter_scores = {}


    while( iteration < max_iter ):
        if intermediate_data:
            intermediate_data.set_iteration(iteration)

        optimal_filt, scores = __optimal_filtered_lineage(imgSeg0 = imgSeg0,
                                                          imgSeg1 = imgSeg1,
                                                          expert_map = expert_map,
                                                          tissue0 = tissue0,
                                                          tissue1 = tissue1,
                                                          imgFus0 = imgFus0,
                                                          imgFus1 = imgFus1,
                                                          mat_init = mat_init,
                                                          field_sigma = field_sigma,
                                                          non_linear_registration_params = non_linear_registration_params,
                                                          mapping_dist = mapping_dist,
                                                          mapping_ndiv = mapping_ndiv,
                                                          mapping_candidate_method = mapping_candidate_method,
                                                          mapping_flow_method = mapping_flow_method,
                                                          filter_params = filter_params,
                                                          strict_candidate_test = strict_candidate_test,
                                                          intermediate_data = intermediate_data)

        iter_scores[iteration] = scores

        print "alt_loop iteration", iteration

        if equal_lineages(optimal_filt, mapping):
            mapping = optimal_filt
            reason  = REASON_STABLE
            break
        else:
            mapping = optimal_filt
            iteration += 1

    return reason, mapping, iter_scores



################################################################################
# The above function relies on the following sort-of-memoizing functions.      #
# They use the "intermediate_data" to recover data from previous calculations. #
# They are implemented in a cascading way where the top call requests data     #
# from memozing subcalls, and so on...                                         #
################################################################################
@alt_intermediate("alt_loop", ("optimal_filtered", "lineage"), ("scores", "picklable"))
def __optimal_filtered_lineage(**kw):
    optimal, = __optimal_lineage(**kw)
    return update_lineage(optimal, kw["mapping"], kw["tissue0"], kw["tissue1"], kw["filter_params"], kw["start_label"]),


@alt_intermediate("alt_loop", ("optimal_raw", "lineage"))
def __optimal_lineage(**kw):
    candy, = __candidate_lineage(**kw)
    return optimal_lineage(kw["imgSeg0"].max(), kw["imgSeg1"].max(), candy, kw["expert_map"],
                           kw["mapping_ndiv"], kw["mapping_flow_method"]),


@alt_intermediate("alt_loop", ("candidate", "clineage"))
def __candidate_lineage(**kw):
    imgSeg0_homo, imgSeg1_homo = __register_resample_and_resize_images(**kw)

    candy =  candidate_lineaging(imgSeg0_homo, imgSeg1_homo, dist = float(kw["mapping_dist"]),
                                 ndiv = kw["mapping_ndiv"], bkgdLabel = 1,
                                 candidate_method = kw["mapping_candidate_method"])

    test_passed, missed_mothers, missed_kids = candidate_contains_expert(kw["expert_map"], candy)
    if not test_passed:
        idata = kw["intermediate_data"]
        idata.log("missed these mothers " + str(missed_mothers) )
        idata.log("missed these kids " + str(missed_kids) )
        if kw["strict_candidate_test"]:
            raise Exception(REASON_CANDIDATE_TEST_FAILED)
    return candy,

@alt_intermediate("alt_loop", ("imgSeg0_homo", "image"), ("imgSeg1_homo", "image"))
def __register_resample_and_resize_images(**kw):
    mat_init, imgSeg0, imgSeg1 = kw["mat_init"], kw["imgSeg0"], kw["imgSeg1"]
    field, deformation = __register_images(**kw)

    # NOTE : For segmented image, use nearest neighbour instead of linear interpolation (or you will create wrong labels)
    if deformation is not None:
        # NOTE : ideally there would be only one resampling using only T_inv. However we currently don't have the tools
        # to compose vector fields and actually this implementation of the resampling is probably more efficient
        # in terms of memory and speed as composing vector fields can itself be a memory hole. However, the quality
        # of the images given by this version (which is similar to the implementation used by R. Fernandez) should be
        # compared to that of the resampling using a precomposed T_inv.
        fuse_task = fusion_task(imgSeg0, [], deformation if deformation is not None else None)
        imgSeg0_prime = SpatialImage(fusion(fuse_task, min_vs = imgSeg1.voxelsize[0], interpolation="nearest"), resolution=imgSeg1.voxelsize[0])
        fuse_task = fusion_task(imgSeg0_prime, [mat_init], field)
        imgSeg0_prime = SpatialImage(fusion(fuse_task, min_vs = imgSeg1.voxelsize[0], interpolation="nearest"), resolution=imgSeg1.voxelsize[0])
    else:
        # resample anyway to have both images with same voxelsizes as some parts of the lineage mapping
        # require it in some conditions.

        # create an identity transform in voxel space if neeeded.
        mat_init = mat_init if mat_init is not None else identity(imgSeg0.voxelsize, imgSeg1.voxelsize)
        fuse_task = fusion_task(imgSeg0, [mat_init], None)
        imgSeg0_prime = SpatialImage(fusion(fuse_task, min_vs = imgSeg1.voxelsize[0], interpolation="nearest"), resolution=(imgSeg1.voxelsize[0],)*3)

    # -- images must have the same dimension --
    print type(imgSeg0_prime)
    common_shape = (max(imgSeg0_prime.shape[0], imgSeg1.shape[0]),
                    max(imgSeg0_prime.shape[1], imgSeg1.shape[1]),
                    max(imgSeg0_prime.shape[2], imgSeg1.shape[2]))
    common_dtype = max( (imgSeg0_prime.dtype, imgSeg1.dtype), key = lambda x: numpy.iinfo(x).max)
    imgSeg0_homo = SpatialImage(numpy.zeros(common_shape, dtype = common_dtype), imgSeg0_prime.voxelsize)
    imgSeg1_homo = SpatialImage(numpy.zeros(common_shape, dtype = common_dtype), imgSeg1.voxelsize)
    #print imgSeg0_prime.resolution, imgSeg1.resolution
    #print "-------------------------"
    #print "-------------------------"
    #print "-------------------------"
    #print imgSeg0_prime[:,:,:]
    imgSeg0_homo[:imgSeg0_prime.shape[0], :imgSeg0_prime.shape[1], :imgSeg0_prime.shape[2]] = imgSeg0_prime[:,:,:]
    imgSeg1_homo[:imgSeg1.shape[0], :imgSeg1.shape[1], :imgSeg1.shape[2]] = imgSeg1[:,:,:]
    #print "-------------------------"
    #print "-------------------------"
    #print "-------------------------"
    print imgSeg0_homo.resolution, imgSeg1_homo.resolution
    return imgSeg0_homo, imgSeg1_homo


@alt_intermediate("alt_loop", ("field", "image"), ("deformation", "image"))
def __register_images(**kw):

    mat_init         = kw["mat_init"]
    imgFus0, imgFus1 = kw["imgFus0"], kw["imgFus1"]
    deformation = None
    field       = None

    if imgFus0 is not None and imgFus1 is not None:

        # ABOUT REGISTRATIONS AND RESAMPLING :
        # 1) We want to register imgSeg0 over imgSeg1
        #    ( == imgSeg1 is the reference image). However these are labeled images. So we use
        #    imgFusX instead to compute the registrations.
        # 2) The transform that places imgFus0 over imgFus1 is called T. It will be computed in
        #    3 steps :
        #      - a rigid registration Tr
        #      - a rough vector field Td0
        #      - a finer vector field Td1
        #    So T = Td1 o Td0 o Tr
        # 3) However, what we want to do is to resample imgSeg0 into imgSeg1 space. To do this
        #    we actually need T_inv = Tr_inv o Td0_inv o Td1_inv ~= mat_init o field o deformation.
        #    This explains the order of the resampling.

        # if mat_init exists it is the resampling matrix that
        # resamples the fus0 image into the fus1 image space.
        # (it 'goes' from fus1 space to fus0 space to fetch pixel values)
        # deformation_field expects the opposite:
        if mat_init is not None:
            direct_mat = numpy.linalg.inv(mat_init)

        field, = __deformation_field(direct_mat, **kw)

        deformation, = __nonlinear_registration(field, **kw)

    return field, deformation


@alt_intermediate("alt_loop", ("field", "image"))
def __deformation_field(direct_mat, **kw):
    tissue0, tissue1 = kw["tissue0"], kw["tissue1"]
    imgFus0          = kw["imgFus0"]
    mapping          = kw["expert_map"]
    field_sigma      = kw["field_sigma"]
    res0, res1       = kw["imgSeg0"].voxelsize, kw["imgSeg1"].voxelsize
    # NOTE: the asclepios tools require the field to be in float32
    return deformation_field(tissue0, tissue1, imgFus0, mapping, field_sigma,
                             direct_mat, res0 = res0, res1 = res1, inv = True, dtype = numpy.float32),


@alt_intermediate("alt_loop", ("deformation", "image"))
def __nonlinear_registration(field, **kw):
    imgFus0, imgFus1               = kw["imgFus0"], kw["imgFus1"]
    mat_init                       = kw["mat_init"]
    non_linear_registration_params = kw["non_linear_registration_params"]
    # -- non_linear registration. imgFus1 (t+1 time step) is the reference image
    # on which imgFus0 (t+0 time step) image will be registered. --
    recon_task = reconstruction_task(imgFus1, imgFus0, initialisation = mat_init,
                                     auto_non_linear_params = non_linear_registration_params,
                                     initial_field = field)

    # -- compute transforms and take only things useful for resampling
    # (there is only one result in registration list) --
    return reconstruct(recon_task)[1][0].deformation,
