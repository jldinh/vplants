#-*- python -*-
# -*- coding: latin-1 -*-
#
#       vplants.mars_alt.analysis.structural_analysis
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
from scipy.ndimage import binary_dilation
from openalea.image.spatial_image import SpatialImage
from analysis import extract_L1

def draw_walls(image, dilation=False):
    """
    Draw walls from a segmented image

    :Parameters:
        - `image` (|SpatialImage|) - segmented image
        - `dilation` (bool, optional) - Apply a dilation after extraction

    :Returns:
        - `walls` (|SpatialImage|)
    """

    if not isinstance(image,SpatialImage):
        image = SpatialImage(image)

    walls = np.zeros_like(image)

    dx,dy,dz = np.gradient(image,2)
    mask = ((dx==0)&(dy==0)&(dz==0))
    walls = np.where(mask,0,1)
    if dilation:
        return SpatialImage(binary_dilation(walls),image.resolution)
    else:
        return SpatialImage(walls,image.resolution)

def draw_L1(image):
    """
    Draw cells in the layer 1 from a segmented image

    :Parameters:
        - `image` (|SpatialImage|) - segmented image

    :Returns:
        - `L1` (|SpatialImage|)
    """
    if not isinstance(image,SpatialImage):
        image = SpatialImage(image)
    imL1 = np.copy(image)

    print "extract cells in the L1"
    L1 = extract_L1(image)

    print "draw the result image"
    for cell in xrange(1,image.max()+1) :
        if cell not in L1 :
            imL1[imL1==cell]=1
    return SpatialImage(imL1,image.resolution)
