# -*- python -*-
# -*- coding: latin-1 -*-
#
#       mars : reconstruction
#
#       Copyright 2006 - 2010 INRIA - CIRAD - INRA
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

from ctypes import *
from openalea.core.ctypes_ext import find_library

#Loading dynamic link libraries
libvt = cdll.LoadLibrary(find_library('vt'))
libbasic = cdll.LoadLibrary(find_library('basic'))

import numpy as np
from openalea.image.spatial_image import SpatialImage

from vplants.asclepios.vt.vt_image import VT_Image
from vplants.asclepios.vt.vt_connexe import _VT_CONNEXE, VT_BINAIRE


def hysteresis( image, low_threshold, high_threshold, connectivity=26, tcc=1, ncc=-1):
    """
    Applies a hysteresis thresholding and cast the result image.

    Such a thresholding keeps the connected components, made of points whose value
    is larger or equal to "low_threshold", and which contains at least one (or some, see parameters)
    point whose value is larger or equal to "high_threshold".

    :Parameters:
      - `image` (|SpatialImage|) - input image
      - `low_threshold` (float) - low threshold (to binarize input image)
      - `high_threshold` (float) - high threshold for hysteresis thresholding (binary input)
      - `connectivity` (int, optional) - connectivity (4, 6, 8, 10, 18, 26=default)
      - `tcc` (int, optional) - minimal size of connected components
      - `ncc` (int, optional) - maximal number of connected components
                                if the number of valid connected components is larger than this one
                                the components are sorted with respect to their size, and the
                                largest ones are retained.
    :Returns:
        ALERT TODO!
    """
    # reading of image
    if not isinstance(image,SpatialImage) :
	image = SpatialImage(image)

    # initialization of vt_image
    vt_image = VT_Image(image)
    img = vt_image.get_vt_image()

    imres = SpatialImage(np.zeros((image.shape), dtype=np.ubyte), image.resolution)
    vt_res = VT_Image(imres)
    res = vt_res.get_vt_image()

    # low and high threshold
    lt = c_float(low_threshold)
    ht = c_float(high_threshold)

    # initialization of vt_connexe
    connexity = _VT_CONNEXE()
    libvt.VT_Connexe(pointer(connexity))

    connexity.type_connexite = connectivity
    connexity.type_output = VT_BINAIRE
    connexity.min_size = tcc
    connexity.max_nbcc = ncc

    libvt.VT_Hysteresis( pointer(img), pointer(res), lt, ht, pointer(connexity) )
    return vt_res.get_spatial_image()


def connected_components( image, low_threshold, connectivity=26, tcc=1, ncc=-1 ):
    """
    """
    # reading of image
    if not isinstance(image,SpatialImage) :
	image = SpatialImage(image)

    # initialization of vt_image
    vt_image = VT_Image(image)
    img = vt_image.get_vt_image()

    imres = SpatialImage(np.zeros((image.shape), dtype=np.ushort), image.resolution)
    vt_res = VT_Image(imres)
    res = vt_res.get_vt_image()

    # low and high threshold
    lt = c_float(low_threshold)

    # initialization of vt_connexe
    connexity = _VT_CONNEXE()
    libvt.VT_Connexe(pointer(connexity))

    connexity.type_connexite = connectivity
    connexity.min_size = tcc
    connexity.max_nbcc = ncc

    ret = libvt.VT_ConnectedComponents( pointer(img), pointer(res), lt, pointer(connexity) )
    return vt_res.get_spatial_image()



