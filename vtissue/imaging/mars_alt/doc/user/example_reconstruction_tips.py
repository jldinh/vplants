# !!!!!!! DO NOT CHANGE THE FORMATTING OR YOU'LL HAVE TO UPDATE reconstruction_tips.rst!!!!!!!!!

# MOST IMPORTANT : DO NOT INSERT OR DELETE LINES
# OR ELSE THE NUMBERING IN reconstruction_tips.rst!!!!!!!!!
# WILL BE WRONG



# used by the documentation
import numpy as np
from openalea.image.serial.all import imread
from openalea.image.gui.all import display, point_selection
from vplants.mars_alt.mars.all import im2surface, surface2im
import vtissuedata

# -- Load the reference image --

im0_pth = vtissuedata.get_shared_data("t1_1.lsm")
im0 = imread(im0_pth)

# -- Project the image to 2D and recover the altitude map --

threshold = 45 # only consider voxels of intensity higher than this (depends on image dynamic range)
mip0, altitude0 = im2surface(im0, threshold_value=threshold)

# -- Load the floating image --

im1_pth = vtissuedata.get_shared_data("t1_2.lsm")
im1 = imread(im1_pth)

# -- Project it --

mip1, altitude1 = im2surface(im1, threshold_value=threshold)


# -- Place landmarks on the projected images --

ps0  = point_selection(mip0)
ps1  = point_selection(mip1)

# -- Recover REAL coordinates of the points --

pts0_3D = surface2im(ps0.get_points(), altitude0)
pts1_3D = surface2im(ps1.get_points(), altitude1)

# -- save them --

np.savetxt("im0_pts3D.txt", pts0_3D)
np.savetxt("im1_pts3D.txt", pts1_3D)

# -- use in the reconstruction pipeline. The imports --
from vplants.mars_alt.mars.reconstruction import (reconstruct, reconstruction_task,
                                                  surface_landmark_matching_parameters)

# -- reconstruction parameters --
ldmark_params = surface_landmark_matching_parameters(pts0_3D, pts1_3D)

# -- reconstruction association (task) --
recon_task0_1 = reconstruction_task(im0, im1, initialisation = ldmark_params)

# -- Computing the registration --
recons_task, recon_results = reconstruct(recon_task0_1)
