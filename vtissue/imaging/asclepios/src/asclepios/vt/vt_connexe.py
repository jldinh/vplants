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
import numpy as np

from vt_typedefs import *
from vt_neighborhood import *

VT_BINAIRE = 1
VT_GREY = 2
VT_SIZE = 3

#################################################################################
#                               Structures
#################################################################################

class _VT_CONNEXE(Structure) :
    """
    Definition of vt_connexe structure
    """
    _fields_ = [("min_size", c_int),                # minimum size of connected components
                ("max_nbcc", c_int),                # maximum number of connected components
                ("type_connexite", c_int),          # connectivity
                ("type_output", c_int),             # output: binary image or label image
                ("dim", c_int),                     # if 2D, slice by slice computation
                ("verbose", c_int)
                # for compatibility with vt_slconnexe.c
                #("threshold", c_int)
                ]


#################################################################################
#                               Objects
#################################################################################


class VT_Connexe (object):
    """
    Definition of VT_Connexe object
    """
    def __init__(self):
        """
        Initialization :
        """

    def set_default(self):
        """
        used to set parameters to default
        """
	_min_size = 1
        _max_nbcc = -1
        _type_connexite = Neighborhood.N06
        _type_output = VT_BINAIRE
        _dim = DimType.VT_3D
        _verbose = 0

        vt_connexe = _VT_CONNEXE(_min_size, _max_nbcc, _type_connexite, _type_output, _dim, _verbose)
        return vt_connexe
