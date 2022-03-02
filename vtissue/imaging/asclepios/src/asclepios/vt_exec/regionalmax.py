# -*- python -*-
# -*- coding: latin-1 -*-
#
#       vplants.asclepios.vt_exec.regionalmax
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

from ctypes import *
from openalea.core.ctypes_ext import find_library
import numpy as np

#Loading dynamic link libraries
libbasic = cdll.LoadLibrary(find_library('basic'))

from vplants.asclepios.vt.vt_typedefs import get_type
from openalea.image.spatial_image    import SpatialImage

def regionalmax (image, h_minima, hm=1.0, inv=False ) :
    """
    Extraction of local minima of the input image.

    :Parameters:
      - `image` (|SpatialImage|) - input image
      - `h_minima` (int) - minima height
      - `hm` (float, optional) - coefficient multiplicateur
                        actif uniquement pour type UCHAR et USHORT
                        la recherche du maximum se fait en dilatant MIN( distance*hm , distance-h )
                        'en-dessous' de l'image originale, puis en soutrayant.
      - `inv` (bool, optional) - inverse of the image (default = False)
      - `swap : swap 'image-in' (si elle est codee sur 2 octets)\n\
      
    :Returns:
        ALERT TODO!      
    """
    _h = c_int( h_minima )
    _multiplier = c_double( hm )

    #parsing of image
    _x,_y,_z = image.shape
    __dims = c_int * 3
    _dims = __dims ( _x,_y,_z )

    if inv == True :
        print "inverse of the input image"
        image = -image

    _data = image.ctypes.data_as(POINTER(c_void_p))
    _type = get_type(image)

    #init of result image
    _imres = np.zeros_like( image )
    imres = _imres.ctypes.data_as(POINTER(c_void_p))

    libbasic.regionalmax( _data, imres, _type, _dims, _h, _multiplier )
    return SpatialImage(_imres, image.resolution)

