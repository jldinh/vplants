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

import numpy as np

from vt_typedefs import *

from openalea.image.spatial_image import SpatialImage

#################################################################################
#                               Enumerations
#################################################################################

# Differents architecture types
#
class CpuType :
    """
    Definition of CpuType enumeration
    """
    CPU_UNKNOWN = 0
    LITTLEENDIAN = 1
    BIGENDIAN = 2


MY_CPU = CpuType.LITTLEENDIAN

#################################################################################
#                               Structures
#################################################################################

class _VT_IMAGE(Structure) :
    """
    Definition of vt_image structure
    """
    _fields_ = [("name", c_char * STRINGLENGTH),
                ("type", c_uint),
                ("dim", vt_4vpt),       # dimension of image
                ("siz", vt_fpt),        # voxel size
                ("off", vt_fpt),        # translation or offset
                ("rot", vt_fpt),        # rotation
                ("ctr", vt_ipt),
                ("cpu", c_uint),
                ("array", c_void_p),
                ("buf", c_void_p),
                ("user", c_char_p),     # User defined strings array. The user can use any internal purpose string.
                                        # Each string is written at then end of header after a '#' character.
                ("nuser", c_uint)       # Number of user defined strings
                ]

    def _to_c_type(self):
        """
        used to get information from numpy array
        """
        if self.type == ImageType.UCHAR :
            return c_ubyte
        elif self.type == ImageType.SCHAR :
            return c_byte
        elif self.type == ImageType.SSHORT :
            return c_short
        elif self.type == ImageType.USHORT :
            return c_ushort
        elif self.type == ImageType.UINT :
            return c_uint
        elif self.type == ImageType.INT :
            return c_int
        elif self.type == ImageType.ULINT :
            return c_int
        elif self.type == ImageType.FLOAT :
            return c_float
        elif self.type == ImageType.DOUBLE :
            return c_double
        #elif self.type == VOXELTYPE. :
        #    self._data.dtype == np.float128
        else :
            print "TYPE_UNKNOWN"
            return -1

#################################################################################
#                               Objects
#################################################################################


class VT_Image(object):
    """
    Definition of VT_Image object
    """
    def __init__(self,image):
        """
        Initialization :
        """
        self._data = image
        self.vt_image = None

    @classmethod
    def from_spatial_image(cls, spa_img):
        assert isinstance(spa_img, SpatialImage)
        vt_im = VT_Image(spa_img)
        return vt_im.get_vt_image()

    def _from_dtype(self):
        """
        used to get information from numpy array
        """
        if self._data.dtype == np.uint8 :
            _type = ImageType.UCHAR
        elif self._data.dtype == np.int8 :
            _type = ImageType.SCHAR
        elif self._data.dtype == np.int16 :
            _type = ImageType.SSHORT
        elif self._data.dtype == np.uint16 :
            _type = ImageType.USHORT
        elif self._data.dtype == np.uint32 :
            _type = ImageType.UINT
        elif self._data.dtype == np.int32 :
            _type = ImageType.INT
        elif self._data.dtype == np.uint64 :
            _type = ImageType.ULINT
        elif self._data.dtype == np.float32 :
            _type = ImageType.FLOAT
        elif self._data.dtype == np.float64 :
            _type = ImageType.DOUBLE
        #elif self._data.dtype == np.float128 :
        #    _type = VOXELTYPE.
        else :
            _type = ImageType.TYPE_UNKNOWN
        return _type

    def _to_dtype(self):
        """
        used to get information from numpy array
        """
        if self.vt_image.type == ImageType.UCHAR :
            return np.uint8
        elif self.vt_image.type == ImageType.SCHAR :
            return np.int8
        elif image_type == ImageType.SSHORT :
            return np.int16
        elif self.vt_image.type == ImageType.UINT :
            return np.uint32
        elif self.vt_image.type == ImageType.USHORT :
            return np.uint16
        elif self.vt_image.type == ImageType.INT :
            return np.int32
        elif self.vt_image.type == ImageType.ULINT :
            return np.uint64
        elif self.vt_image.type == ImageType.FLOAT :
            return np.float32
        elif self.vt_image.type == ImageType.DOUBLE :
            return np.float64
        #elif self.vt_image.type == VOXELTYPE. :
        #    self._data.dtype == np.float128
        else :
            print "TYPE_UNKNOWN"
            return -1


    def _to_c_type(self):
        """
        used to get information from numpy array
        """
        return self.vt_image._to_c_type()

    def get_vt_image(self) :
        """
        used to set attributes of VT_Image structure
        """
        if self.vt_image is not None:
            print "Double call to buggy get_vt_image"
            import traceback
            traceback.print_stack()
            return self.vt_image

        _name = '\0'
        _type = self._from_dtype()
        _v = 1
        _x, _y, _z = self._data.shape
        _dim = vt_4vpt( _v, _x, _y, _z )
        _vx,_vy,_vz = self._data.resolution
        _siz = vt_fpt( _vx, _vy, _vz )
        _off = vt_fpt( 0.0, 0.0, 0.0 )
        _rot = vt_fpt( 0.0, 0.0, 0.0 )
        _ctr = vt_ipt( 0, 0, 0 )
        _cpu = MY_CPU

        # Data pointer cast to a particular c-types object
        _array = c_void_p()
        _buf =  self._data.ctypes.data_as(c_void_p)
        _user = c_char_p()
        _nuser = 0

        # initialization of VT_Image structure
        self.vt_image = _VT_IMAGE(_name,_type,_dim,_siz,_off,_rot,_ctr,_cpu,
                                  _array,_buf,_user,_nuser)
        libvt.VT_AllocArray( pointer(self.vt_image) )

        return self.vt_image


    def get_spatial_image(self) :
        """
        """
        dt = self._to_c_type()
        _ct_array = (dt * self._data.size).from_address(self.vt_image.buf)
        _np_array = np.ctypeslib.as_array(_ct_array)
        x,y,z = self._data.shape
        # -- This used to be  arr =  np.array(_np_array.reshape(z,x,y).transpose(2,1,0)).
        # but that is wrong. first the shape is x,y,z. Then the transposition
        # doesn't fix the byte ordering which for some reason must be read in Fortran order --
        arr =  np.array(_np_array.reshape(x,y,z, order="F"))
        return SpatialImage(arr, self._data.resolution)

#################################################################################
#                               Functions
#################################################################################

def free_image( image ) :
    libvt.VT_FreeImage( pointer(image) )
    libvt.VT_Free( pointer(image) )
    print "unable to read matrice"
