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

#################################################################################
#                               Constants
#################################################################################

STRINGLENGTH = 256

s8 = c_char
u8 = c_ubyte
s16 = c_short
u16 = c_ushort
i32 = c_int
s32 = c_int
u64 = c_ulong
r32 = c_float
r64 = c_double

#################################################################################
#                               Enumerations
#################################################################################


class DimType :
    """
    Definition of DimType enumeration
    """
    VT_1D = 1
    VT_2D = 2
    VT_3D = 3
    VT_4D = 4
    OneD = 1
    TwoD = 2
    ThreeD = 3

# Differents type coding for images
#
class ImageType :
    """
    Definition of ImageType enumeration
    """
    TYPE_UNKNOWN = 0    # unknown type
    UCHAR = 1           # unsigned char
    SCHAR = 2           # signed char
    USHORT = 3          # unsigned short int
    SSHORT = 4          # signed short int
    UINT = 5            # unsigned int
    INT = 6             # signed int
    ULINT = 7           # unsigned long int
    FLOAT = 8           # float
    DOUBLE = 9          # double

class BufferType :
    """
    Definition of BufferType enumeration
    """
    TYPE_UNKNOWN = 0    # unknown type
    UCHAR = 1           # unsigned char
    SCHAR = 2           # signed char
    USHORT = 3          # unsigned short int
    SSHORT = 4          # signed short int
    UINT = 5            # unsigned int
    INT = 6             # signed int
    ULINT = 7           # unsigned long int
    FLOAT = 8           # float
    DOUBLE = 9          # double

class typeBoolean :
    """
    Definition of typeBoolean enumeration
    """
    False = 0
    True = 1

#################################################################################
#                               Structures
#################################################################################

class vt_ipt(Structure):
    """
    Definition of vt_ipt structure
    Point with 3 integers (x,y,z)
    """
    _fields_ = [("x", c_int),
                ("y", c_int),
                ("z", c_int)
                ]

class vt_4vpt(Structure):
    """
    Definition of vt_4vpt structure
    Point with 4 integers (v,x,y,z)
    """
    _fields_ = [("v", c_int),
                ("x", c_int),
                ("y", c_int),
                ("z", c_int)
                ]

class vt_fpt(Structure):
    """
    Definition of vt_fpt structure
    Point with 3 floats (x,y,z)
    """
    _fields_ = [("x", c_float),
                ("y", c_float),
                ("z", c_float)
                ]


def get_type(image):
    """
    used to get information from numpy array
    """
    if image.dtype == np.uint8 :
        _type = ImageType.UCHAR
    elif image.dtype == np.int8 :
        _type = ImageType.SCHAR
    elif image.dtype == np.int16 :
        _type = ImageType.SSHORT
    elif image.dtype == np.uint16 :
        _type = ImageType.USHORT
    elif image.dtype == np.int32 :
        _type = ImageType.INT
    elif image.dtype == np.uint64 :
        _type = ImageType.ULINT
    elif image.dtype == np.int64 :
        _type = ImageType.VT_SIGNED_LONG
    elif image.dtype == np.float32 :
        _type = ImageType.FLOAT
    elif image.dtype == np.float64 :
        _type = ImageType.DOUBLE
    #elif image.dtype == np.float128 :
    #    _type = VOXELTYPE.
    else :
        _type = ImageType.TYPE_UNKNOWN
    return _type

