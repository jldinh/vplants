# -*- python -*-
# -*- coding: latin-1 -*-
#
#       vplants.asclepios.vt_exec.watershed
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

import sys
from ctypes import *
from openalea.core.ctypes_ext import find_library

#Loading dynamic link libraries
libbasic = cdll.LoadLibrary(find_library('basic'))

import numpy as np
from vplants.asclepios.vt.vt_image import _VT_IMAGE, VT_Image
from openalea.image.spatial_image import SpatialImage


# premier 6-voisin rencontre lors de la mise dans la liste
_FIRST_ENCOUNTERED_NEIGHBOR_ = 0
# plus petit label
_MIN_LABEL_ = 1
# label avec plus de representants
_MOST_REPRESENTED_ = 2


def _get_buffer(image):
    dt = image._to_c_type()
    size = image.dim.x * image.dim.y * image.dim.z
    return (dt * size).from_address(image.buf)


def watershed( image_markers, image_gradient, labelchoice= "first", memory=-1 , iterations=0, verbose=False) :
    """
    Applies the Watershed algorithm

    :Parameters:
      - `image_markers` (|SpatialImage|) - labeled markers image
      - `image_gradient` (|SpatialImage|) - gradient image (unsigned char or unsigned short int)
      - `labelchoice` (str, optional) - method to choose the label in case of conflicts ("first", "min", "most")
                                * "first" : the label of the point that puts the actual point in the list
                                (historical (and default) behavior)
                                * "min" : the label of smallest value
                                * "most" : the label that is the most represented in the neighborhood
      - `memory` (int, optional) - size of the bunch of points to be allocated when required
                                   setting it low allows a better memory management (at the detriment of speed)
                                   setting it high allows a better computational times (at the detriment of speed)

      - `iterations` (int, optional) - maximal number of iterations to be performed
    """

    # parsing ogf args
    if labelchoice == "first" :
        choice = _FIRST_ENCOUNTERED_NEIGHBOR_
    elif labelchoice == "min" :
        choice = _MIN_LABEL_
    elif labelchoice == "most" :
        choice = _MOST_REPRESENTED_
    else:
        print "wrong labelchoice parameter"
        return -1

    theDim = c_int * 3
    theDim = theDim(*image_markers.shape)

    if iterations > 0 :
        libbasic.watershed_setMaxNumberOfIterations( m )


    # reading of input images
    if not isinstance(image_markers, SpatialImage) :
        image_markers = SpatialImage(image_markers)
    vt_image = VT_Image(image_markers)
    image = vt_image.get_vt_image()

    if not isinstance(image_gradient, SpatialImage) :
        image_gradient = SpatialImage(image_gradient)
    vt_imgrad = VT_Image(image_gradient)
    imgrad = vt_imgrad.get_vt_image()

    # initialization ot result image
    vt_res = VT_Image(SpatialImage(np.zeros((image_markers.shape), dtype=image_markers.dtype), image_gradient.resolution))
    imres = vt_res.get_vt_image()

    if ( memory > 0 ) :
        libbasic.watershed_setNumberOfPointsForAllocation( memory )

    else :
        # rule of thumb
        # nb voxels / (nb gradient levels * 50)

        m = (int)( reduce(lambda x,y:x*y,image_gradient.shape) / (256*50) )

    if ( m > libbasic.watershed_getNumberOfPointsForAllocation() ) :
        if ( verbose ) :
            sys.stderr.write( "bunch of allocated points, change %d for %d\n"%(libbasic.watershed_getNumberOfPointsForAllocation(),m) )

        libbasic.watershed_setNumberOfPointsForAllocation( m )

    libbasic.watershed_setlabelchoice( choice )
    if (libbasic.watershed( _get_buffer(imgrad), imgrad.type, _get_buffer(image), _get_buffer(imres), image.type, theDim ) == -1):
        raise Exception("Watershed failed: maybe too many seeds, please review your seed image and reduce number")

    # return result image
    return vt_res.get_spatial_image()
