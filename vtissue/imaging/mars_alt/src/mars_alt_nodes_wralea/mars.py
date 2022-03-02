# -*- python -*-
# -*- coding: latin-1 -*-
#
#       mars_alt wralea
#
#       Copyright 2006 - 2010 INRIA - CIRAD - INRA
#
#       File author(s): Eric MOSCARDI <eric.moscardi@gmail.com>
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#        http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
#
#       OpenAlea WebSite : http://openalea.gforge.inria.fr
################################################################################

__license__ = "Cecill-C"
__revision__ = " $Id: $ "

from vplants.mars_alt.mars.reconstruction import spatialise_matrix_points, reconstruction_task, \
     surface_landmark_matching_parameters, automatic_linear_parameters, automatic_non_linear_parameters, \
     reconstruct, fuse_reconstruction, im2surface, surface2im

from vplants.mars_alt.mars.fusion import original_fusion, fusion, fusion_task

from vplants.mars_alt.all import filtering, \
     seed_extraction, remove_small_cells, mostRepresentative_filter, cell_segmentation


def wra_mask_surface(image, threshold_value):
    mip,alt = im2surface(image, threshold_value=threshold_value)
    return mip,alt,

def wra_mask_coordinates(points,altitude):
    coord = surface2im(points,altitude)
    return coord

def wra_fusion(im_ref,def_ref,images,matrices,deformations):
    return original_fusion(im_ref,def_ref,images,matrices,deformations)
wra_fusion.__doc__ = original_fusion.__doc__

def wra_filtering(im,filter_type,filter_value):
    if filter_type == "alternate sequential filter" :
        filter_type = "asf"
        filter_value = int(filter_value)
    else :
        filter_type = "gaussian"
    return filtering (im,filter_type,filter_value)
wra_filtering.__doc__ = filtering.__doc__


def wra_seed_extraction(img,h_minima):
    return seed_extraction (img,h_minima)
wra_seed_extraction.__doc__ = seed_extraction.__doc__

def wra_remove_small_cells(segmented_image,image_markers,volume,real):
    return remove_small_cells (segmented_image,image_markers,volume,real)
wra_remove_small_cells.__doc__ = remove_small_cells.__doc__

def wra_cell_segmentation(image,h_minima,volume,real=False,prefilter=True,filter_type="gaussian",filter_value="0.5"):
    return cell_segmentation (image,h_minima,volume,real=False,prefilter=True,filter_type="gaussian",filter_value="0.5")
wra_cell_segmentation.__doc__ = cell_segmentation.__doc__
