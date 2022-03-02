# -*- python -*-
# -*- coding: latin-1 -*-
#
#       vplants.mars_alt.alt.alt_preparation
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

import numpy as np
import scipy.ndimage as ndimage

from openalea.image.registration.all import pts2transfo
from openalea.image.registration.matrix import matrix_real2voxels
from openalea.image.serial.basics import lazy_image_or_path
from openalea.image.algo.analysis import SpatialImageAnalysis
from openalea.tissueshape import create_graph_tissue
from vplants.asclepios.vt_exec.reech3d import reech3d


# Apply the transformation to the segmented and fusioned images
def alt_preparation (mapping, imgSeg0, imgSeg1, resampled=False, imgFus0=None):
    """
    convert the initial set of cell lineages to voxel correspondances.

    :Parameters:
    - `mapping` (dictionnary) - initial set of cell lineages
    - `imgFus0` (|SpatialImage|) - parent fusion image (not used if resampled == False)
    - `imgSeg0` (|SpatialImage|) - 4parent segmented image
    - `imgSeg1` (|SpatialImage|) - daughter segmented image

    :Return:
    - `imgFusResampled` (|SpatialImage|) - resampled fused image
    - `imgSegResampled` (|SpatialImage|) - resampled segmented image
    - `transform`       (numpy.ndarray 4x4) - the resampling matrix (from floating space to
                         reference space : serves to resample images of parent cells).
    """

    imgSeg0, was_path = lazy_image_or_path(imgSeg0)
    imgSeg1, was_path = lazy_image_or_path(imgSeg1)

    # -- results --    
#tissue0 = create_graph_tissue(imgSeg0)
    #tissue1 = create_graph_tissue(imgSeg1)

    ImgFusReech = None
    ImgSegReech = None
    T_vox       = None

    points0, points1 = mapping2barycenter(imgSeg0, imgSeg1, mapping)

    # -- T is in real coordinates since mapping2barycenter
    # also works in real coordinates if available. As such,
    # T is NOT a resampling matrix. And it also considers
    # that the points from imgSeg1 are the reference and the
    # image to resample is imgSeg0. This is described in
    # Fernandez PhD 2010, §5.4.1 (T is actually Tr^(-1) in the PhD) --
    T=pts2transfo(points1,points0)
    # -- T_vox IS the resampling matrix --
    T_vox = matrix_real2voxels(T, imgSeg0.resolution, imgSeg1.resolution)

    if resampled:
        imgFus0, was_path = lazy_image_or_path(imgFus0)
        # -- this uses the original version of reech3D which takes a real-to-real matrix and converts it to voxel-to-voxel.
        # alternate version (reech3d_voxels) directly take voxel-to-voxel which is consistent with what other
        # registration-related algorithms take --
        ImgFusReech = reech3d (imgFus0 , mat=T, vin=imgFus0.resolution,vout=imgFus0.resolution, output_shape= imgFus0.shape )
        ImgSegReech = reech3d (imgSeg0 , mat=T, vin=imgSeg0.resolution,vout=imgSeg0.resolution, output_shape= imgSeg0.shape,
                               interpolation="nearest")
        ImgSegReech[ImgSegReech==0]=1
    return T_vox
    #return ImgFusReech,ImgSegReech, tissue0, tissue1, T_vox


def applyPalette(im, base_dict):
    palette=np.ones(np.max(im)+1, dtype=np.uint16)
    for i in base_dict.keys():
        palette[i]=base_dict[i]
    return palette[im] 


# Get the transformation matrix
def mapping2barycenter (imgSeg0, imgSeg1, mapping ):
    """
    convert the initial set of cell lineages to voxel correspondances.

    :Parameters:
    - `tissue0` (|SpatialImage|) - graph of fusion image T0
    - `tissue1` (|SpatialImage|) - graph of fusion image T1
    - `mapping` (dictionnary) - initial set of cell lineages

    :Return:
    - `points0` (list) - barycenters of the parent cells
    - `points1` (list) - barycenters of the daughter cells
    """
    
    if mapping.has_key(1):
        mapping.pop(1)
    reverse_map = {}
    for mother, children in mapping.iteritems():
        for child in children:
            reverse_map[child]=mother

    newSeg1 = applyPalette(imgSeg1, reverse_map)
    newSeg0 = applyPalette(imgSeg0, dict([(mother, mother) for mother in mapping.keys()]))
    
    an0 = SpatialImageAnalysis(newSeg0)
    an1 = SpatialImageAnalysis(newSeg1)
    
    points0 = an0.center_of_mass(labels = an0.labels()[1:], real = False)
    points1 = an1.center_of_mass(labels = an1.labels()[1:], real = False)
    
    return points0, points1

