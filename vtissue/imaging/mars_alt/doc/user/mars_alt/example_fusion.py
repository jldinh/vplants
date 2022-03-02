# !!!!!!! DO NOT CHANGE THE FORMATTING OR YOU'LL HAVE TO UPDATE fusion.rst !!!!!!!!!!!!!
###############################################################################
# A simple reconstruction example :                                           #
# Three acquisitions of the same organ at different angles are fused together #
# into one super resolution image.                                            #
###############################################################################
################
# Get the data #
################

# -- import everything --

import numpy
from openalea.image.all import imread, imsave, point_selection, display
from vplants.mars_alt.mars.all import reconstruct, reconstruction_task, surface_landmark_matching_parameters
from vplants.mars_alt.mars.all import automatic_linear_parameters, automatic_non_linear_parameters
from vplants.mars_alt.mars.all import fuse_reconstruction
import vtissuedata


# -- Get the data paths --

# -- image paths --
im0_path_t0 = vtissuedata.get_shared_data("t1_1.lsm")
im1_path_t0 = vtissuedata.get_shared_data("t1_2.lsm")
im2_path_t0 = vtissuedata.get_shared_data("t1_3.lsm")

# -- Point set paths --
pt_set_names = "t1_p12-1-3D.txt", "t1_p12-2-3D.txt", "t1_p13-1-3D.txt", "t1_p13-3-3D.txt",
pt_set_paths = [vtissuedata.get_shared_data(pt_set) for pt_set in pt_set_names]

# -- Read the data --

# -- read images --
im0_t0 = imread(im0_path_t0)
im1_t0 = imread(im1_path_t0)
im2_t0 = imread(im2_path_t0)

# -- read point sets --
pts01_0_3D, pts01_1_3D, pts02_0_3D, pts02_2_3D = [numpy.loadtxt(f) for f in pt_set_paths]

###################################
# Image 1 on image 0 registration #
###################################

# -- Parametrise the landmark registration --

ldmark_params_01 = surface_landmark_matching_parameters(pts01_0_3D, pts01_1_3D)

# -- Parametrise the auto-linear registration --

auto_lin_params = automatic_linear_parameters(transfo_type='rigid', estimator='ltsw',
                                              pyramid_levels=6, finest_level=2)

# -- Parametrise the auto-non-linear registration --

auto_nonlin_params = automatic_non_linear_parameters(start_level=3, end_level=1)

# -- Create the reconstruction task that registers image 1 on image 0 --

recon_task0_1 = reconstruction_task(im0_t0, im1_t0, initialisation = ldmark_params_01,
                                    auto_linear_params=auto_lin_params,
                                    auto_non_linear_params=auto_nonlin_params)

###################################
# Image 2 on image 0 registration #
###################################

# -- Parametrise the landmark registration --

ldmark_params_02 = surface_landmark_matching_parameters(pts02_0_3D, pts02_2_3D)

# -- Create the reconstruction task that registers image 2 on image 0 --

recon_task0_2 = reconstruction_task(im0_t0, im2_t0, initialisation = ldmark_params_02,
                                    auto_linear_params=auto_lin_params,
                                    auto_non_linear_params=auto_nonlin_params)

##################
# Reconstruction #
##################

# -- This will take quite more time! --
recons_task, recons_results = reconstruct([recon_task0_1, recon_task0_2])

##########
# Fusion #
##########

fused_im_0_1_2, interm = fuse_reconstruction(recons_task, recons_results)

# -- save! --
imsave("~/fused_t0_0_1_2.inr.gz", fused_im_0_1_2)

#NOT TO APPEAR IN DOCUMENTATION:
from PyQt4.QtGui import QApplication
if QApplication.instance() is None:
    app=QApplication([])

# -- display --
display(fused_im_0_1_2)


#######################################
# THIS IS NOT PART OF THE EXAMPLE     #
# BUT IS USEFUL FOR THE DOCUMENTATION #
# AS IT CREATES THE FIGURES.          #
#######################################

def do_doc_images():
    from openalea.image.all import SpatialImage
    from vplants.asclepios.vt_exec.reech3d import reech3d_voxels

    # redo the resampling but with intermediate data please
    fused_im_0_1_2, interm = fuse_reconstruction(recons_task, recons_results, output_intermediate=True)

    ######################################################################
    # The original reference image is cross-sectionned in all directions #
    ######################################################################
    # anisotropic image needs resampling.
    vs = im0_t0.voxelsize
    min_vs = min(vs)
    im = reech3d_voxels(im0_t0,  vin=vs, vout=(min_vs,min_vs,min_vs), output_shape=numpy.divide( numpy.multiply(im0_t0.shape, vs), (min_vs,min_vs,min_vs) ))
    # resize all images to same dimension for concatenation
    sz = im.shape
    sections = [im[sz[0]/2.,:,:].copy("F"), im[:,sz[1]/2.,:].copy("F"), im[:,:,sz[2]/2.].copy("F") ]
    max_sz = max( sec.shape[1] for sec in sections )
    [sec.resize((sec.shape[0], max_sz), refcheck=False) for sec in sections]
    # save (concatenate too)
    imsave("original_cross_sections.png", SpatialImage( numpy.concatenate(sections, axis=0).T))

    #####################################################################
    # All three original images are cross-sectionned in XY at mid-depth #
    #####################################################################
    imsave("original_images.png", SpatialImage(numpy.concatenate( [im[:,:,im.shape[2]/2.] for im in [im0_t0,im1_t0,im2_t0] ], axis=0).T))

    ####################################################################################
    # All three intermediate registered images are cross-sectionned in XY at mid-depth #
    ####################################################################################
    imsave("registered_images.png", SpatialImage(numpy.concatenate( [im[:,:,im.shape[2]/2.] for im in interm ], axis=0).T))

    ####################################################################################
    # All three intermediate registered images are cross-sectionned in XY at mid-depth #
    ####################################################################################
    # imsave("fused_image.png", SpatialImage(fused_im_0_1_2[:,:,fused_im_0_1_2.shape[2]/2.].T))

    ##############################################################
    # save x, y, and z cross sections of fused (isotropic) image #
    ##############################################################
    im = fused_im_0_1_2
    sz = im.shape
    sections = [im[sz[0]/2.,:,:].copy("F"), im[:,sz[1]/2.,:].copy("F"), im[:,:,sz[2]/2.].copy("F") ]
    max_sz = max( sec.shape[1] for sec in sections )
    [sec.resize((sec.shape[0], max_sz), refcheck=False) for sec in sections]
    imsave("result_cross_sections.png", SpatialImage(numpy.concatenate(sections, axis=0).T))
