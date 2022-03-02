# -*- python -*-
# -*- coding: latin-1 -*-
#
#       vplants.asclepios.vt_exec.morpho
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
from ctypes import *
from openalea.core.ctypes_ext import find_library
from vplants.asclepios.vt.vt_typedefs import get_type
from openalea.image.spatial_image import SpatialImage

#Loading dynamic link libraries
libbasic = cdll.LoadLibrary(find_library('basic'))


from openalea.core import logger
mylogger = logger.get_logger(__name__)

class _typeMorphoToolsPoint(Structure) :
    """
    Definition of typeMorphoToolsPoint structure
    """
    _fields_ = [("x", c_int),
                ("y", c_int),
                ("z", c_int),
                ("o", c_int)
                ]


class _typeMorphoToolsList(Structure) :
    """
    Definition of typeMorphoToolsList structure
    """
    _fields_ = [("nb", c_int),
                ("list", POINTER(_typeMorphoToolsPoint))
                ]


class _typeStructuringElement(Structure) :
    """
    Definition of typeStructuringElement structure

    Morphology :
        - iterations number
        - connectivity
    """
    _fields_ = [("nbIterations", c_int),
                ("connectivity", c_int),
                ("userDefinedSE", _typeMorphoToolsList),     # structuring element given by the user
                ("radius", c_int),
                ("dimension", c_int)
                ]


#################################################################################
#                               Objects
#################################################################################


class StructuringElement(object):
    """
    Definition of StructuringElement object
    """
    def __init__(self):
        """
        Initialization :
        """
        self.struct_elt = None

    def get_default_elt (self) :
        """
        """
        # initialization of typeStructuringElement structure
        nbIterations = 1
        connectivity = 26

        nb = 0
        _list = pointer(_typeMorphoToolsPoint(0,0,0,0))
        userDefinedSE = _typeMorphoToolsList(nb, _list)

        radius = 0

        self.struct_elt = _typeStructuringElement(nbIterations, connectivity, userDefinedSE, radius)

    def get_struct_elt (self, iterations, connectivity, radius, mode2D) :
        """
        """
        if mode2D is True:
            dimension = 2
            if con == 6 :
	        connectivity = 4
	    elif (con == 10) or (con == 18) or (con == 26) :
                connectivity = 8

        nb = 0
        _list = pointer(_typeMorphoToolsPoint(0,0,0,0))
        userDefinedSE = _typeMorphoToolsList(nb, _list)

        self.struct_elt = _typeStructuringElement(iterations, connectivity, userDefinedSE, radius)

        return self.struct_elt



class Morpho(object):
    """
    """
    def __init__(self,img,iterations=1,connectivity=26,radius=0,mode2D=False) :
        """
        """
        if not isinstance(img,SpatialImage):
            self.img = SpatialImage(img)
            
        self.img = img
        self.iterations = iterations
        self.connectivity = connectivity
        self.radius = radius
        self.mode2D = mode2D

        self._create_elt()

        #parsing of image
        _x,_y,_z = img.shape
        __dims = c_int * 3
        self._dims = __dims ( _x,_y,_z )

        self._data = img.ctypes.data_as(POINTER(c_void_p))
        self._type = get_type(img)

        #init of result image
        self._imres = np.zeros_like( img )
        self.imres = self._imres.ctypes.data_as(POINTER(c_void_p))

    def _create_elt(self):
        """
        defining of the structuring element
        """
        SE = StructuringElement()
        self.struct_elt = SE.get_struct_elt(self.iterations,self.connectivity,self.radius,self.mode2D)

    def dilation (self):
        """
        """
        libbasic.morphologicalDilation(self._data,self.imres,self._type,self._dims, pointer(self.struct_elt))
        return SpatialImage(self._imres,self.img.resolution)

    def erosion (self):
        """
        """
        libbasic.morphologicalErosion(self._data,self.imres,self._type,self._dims, pointer(self.struct_elt))
        return SpatialImage(self._imres,self.img.resolution)

    def closing (self):
        """
        """
        if ( libbasic.morphologicalDilation(self._data,self.imres,self._type,self._dims, pointer(self.struct_elt)) != 1 ) :
	    mylogger.error("error in dilation (closing)")
        if ( libbasic.morphologicalErosion(self._data,self.imres,self._type,self._dims, pointer(self.struct_elt)) != 1 ) :
            mylogger.error("error in erosion (closing)")
        return SpatialImage(self._imres,self.img.resolution)


def dilation(img,iterations=1,connectivity=26,radius=0,mode2D=False):
    """
    """
    morpho = Morpho(img,iterations=1,connectivity=26,radius=0,mode2D=False)
    return morpho.dilation()


def erosion(img,iterations=1,connectivity=26,radius=0,mode2D=False):
    """
    """
    morpho = Morpho(img,iterations=1,connectivity=26,radius=0,mode2D=False)
    return morpho.erosion()
