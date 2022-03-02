################################################################################
# -*- python -*-
#
#       baladin
#
#       Copyright 2006-2009 INRIA - CIRAD - INRA
#
#       File author(s): Eric Moscardi <eric.moscardi@sophia.inria.fr>
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
#
#       OpenAlea WebSite : http://openalea.gforge.inria.fr
#
################################################################################

__license__= "Cecill-C"
__revision__ = " $Id$ "

from ctypes import *
import numpy as np
from openalea.core.ctypes_ext import find_library

from openalea.image.spatial_image import SpatialImage

from openalea.core import logger
mylogger = logger.get_logger(__name__)

#Loading dynamic link libraries
baladin_lib = cdll.LoadLibrary(find_library('baladin'))

#################################################################################
#                               Enumerations
#################################################################################

class VOXELTYPE:
    """
    Definition of VOXELTYPE enumeration
    """
    VT_UNSIGNED_CHAR = 0    # Unsigned 8 bits
    VT_UNSIGNED_SHORT = 1   # Unsigned 16 bits
    VT_SIGNED_SHORT = 2     # Signed 16 bits
    VT_UNSIGNED_INT = 3     # Unsigned 32 bits
    VT_SIGNED_INT = 4       # Signed 32 bits
    VT_UNSIGNED_LONG = 5    # Unsigned 64 bits
    VT_SIGNED_LONG = 6      # Signed 64 bits
    VT_FLOAT = 7            # Float 32 bits
    VT_DOUBLE = 8           # Float 64 bits


class  enumTransformClass:
    """
    Definition of enumTransformClass enumeration used to
    distinguish the affine and the spline transformation
    """
    MATRIX = 0
    BSPLINE = 1


class enumTypeTransfo:
    """
    Definition of enumTypeTransfo enumeration
    about the different types of transformation
    """
    RIGIDE = 0
    SIMILITUDE = 1
    AFFINE = 2
    SPLINE = 3


class enumTypeEstimator:
    """
    Definition of enumTypeTransfo enumeration
    about the different types of estimator
    """
    TYPE_LS = 0
    TYPE_LSSW = 1


class enumTypeMesure:
    """
    Definition of enumTypeTransfo enumeration
    about the different types of mesures
    """
    MESURE_CC = 0
    MESURE_EXT_CC = 1
    MESURE_CR = 2
    MESURE_CC_GRAD = 3
    MESURE_CR_GRAD = 4
    MESURE_OM = 5


#################################################################################
#                               Structures
#################################################################################

class _MATRIX(Structure):
    """
    Definition of _MATRIX structure derived from the Structure class which is defined in the ctypes module
    """
    _fields_ = [("l", c_int),       # Number of row
                ("c", c_int),       # Number of column
                ("m", POINTER(c_double))
                ]


class _TRANSFORM(Structure):
    """
    Definition of _TRANSFORM structure
    """
    _fields_ = [("type", c_int),           # _enumTransformClass used to store the information about "is it SPLINE or MATRIX"
                ("transform_real_to_real", c_void_p),    # to store the transformation (as SPLINE or MATRIX) that is estimated using the BM-algorithm
                ("matrix_voxel_to_voxel", c_void_p),
                ("matrix_voxel_to_real_Ref", POINTER(_MATRIX)), # to transform an image given in voxel measures to an image in real measures
                ("matrix_real_to_voxel_Ref", POINTER(_MATRIX))  # to transform an image given in real measures to an image in voxel measures
                ]


class _PARAM(Structure):
    """
    Definition of _PARAM structure
    """
    _fields_ = [ # thresholds on images
                ("seuil_bas_flo", c_int),
                ("seuil_haut_flo", c_int),
                ("seuil_bas_ref", c_int),
                ("seuil_haut_ref", c_int),

                # percentage about thresholds
                ("seuil_pourcent_ref", c_double),
                ("seuil_pourcent_flo", c_double),

                # Transformation, estimator, similarity mesure
                ("transfo", c_int),  #_enumTypeTransfo

                ("estimateur", c_int), #_enumTypeEstimator
                ("use_lts", c_int),
                ("lts_cut", c_double),

                ("mesure", c_int), #_enumTypeMesure

                # threshold on similarity mesure
                ("seuil_mesure", c_double),

                # number of iterations by step
                ("nbiter", c_int),

                # blocs parameters :
                # bloc dimensions
                ("bl_dx", c_int),
                ("bl_dy", c_int),
                ("bl_dz", c_int),

                # bloc border to add in order to compute the first order statistics :
                # so bloc dimensions will be bl_d[x,y,z]+ 2 * bl_border_[x,y,z]
                ("bl_border_x", c_int),
                ("bl_border_y", c_int),
                ("bl_border_z", c_int),

                # progress step of bloc in the fixed image ( eg. image_floating here)
                ("bl_next_x", c_int),
                ("bl_next_y", c_int),
                ("bl_next_z", c_int),

                # parameters to the browsing of neighborhood of done block
                # progress step of bloc during the browsing of neighborhood
                ("bl_next_neigh_x", c_int),
                ("bl_next_neigh_y", c_int),
                ("bl_next_neigh_z", c_int),

                # dimensions of neighborhood browsing
                ("bl_size_neigh_x", c_int),
                ("bl_size_neigh_y", c_int),
                ("bl_size_neigh_z", c_int),

                # variance percentage and variance minimum in blocs
                ("bl_pourcent_var", c_double),
                ("bl_pourcent_var_min", c_double),
                ("bl_pourcent_var_dec", c_double),

                # pyramid parameters
                # number of pyramid steps
                ("pyn", c_int),

                # minimal steps, e.g 0 = resolution of image_ref, 1, 2... stop before
                ("pys", c_int),

                # sub-resolution registration
                ("sub", c_int),

                # informations about execution (display, save or nothing)
                ("verbosef", c_void_p),

                # minimal informations about execution
                ("verbose", c_int),

                # save on disk the pairing fields
                ("write_def", c_int),

                # visually check the process with intermediate images saved on disk
                ("vischeck", c_int),

                # root median squares for step change
                ("rms", c_int),

                # pyramid computed by gaussian filtering
                ("py_filt", c_int),

                # angle for PHISCALE transformation
                ("phi", c_double)
                ]


class _BAL_IMAGE(Structure):
    """
    Definition of BAL_IMAGE structure
    """
    _fields_ = [("ncols", c_int),       # Number of columns (X dimension)
                ("nrows", c_int),       # Number of rows (Y dimension)
                ("nplanes", c_int),     # Number of planes (Z dimension)
                ("vdim", c_int),        # Vector size
                ("type", c_int),        # VOXELTYPE = The different size of words for a 3D image
                ("data", c_void_p),     # Generic pointer on image data buffer
                ("array", c_void_p),    # Generic 3D array pointing on each image element
                ("vx", c_double),       # Real voxel size in X dimension
                ("vy", c_double),       # Real voxel size in Y dimension
                ("vz", c_double),       # Real voxel size in Z dimension
                ("name", c_char_p)
                ]

def matrixToAscii( mat ):

   for i in range(0,16,4):
       print "[", mat.m[i], "\t",
       print  mat.m[i+1], "\t",
       print  mat.m[i+2], "\t",
       print  mat.m[i+3], "]\n"


#################################################################################
#                               Objects
#################################################################################

class Matrix(object):
    """
    Definition of Matrix object
    """
    def __init__(self,img_ref,img_flo,numpy_matrix=None):
        """
        initialization of _MATRIX() object
        """
        self.img_ref = img_ref
        self.img_flo = img_flo
        self._matrix = _MATRIX()
        baladin_lib._alloc_mat( pointer(self._matrix), 4, 4 )

        if numpy_matrix is not None:
            self._from_numpy(numpy_matrix)
        else:
            _vrx,_vry,_vrz = self.img_ref.resolution
            _xrdim,_yrdim,_zrdim = self.img_ref.shape
            _vfx,_vfy,_vfz = self.img_flo.resolution
            _xfdim,_yfdim,_zfdim = self.img_flo.shape

            baladin_lib.ChangeGeometry(pointer(self._matrix),
		           _xrdim,_yrdim,_zrdim,c_double(_vrx),c_double(_vry),c_double(_vrz),
                           _xfdim,_yfdim,_zfdim,c_double(_vfx),c_double(_vfy),c_double(_vfz))


    def _from_numpy(self,numpy_matrix):
        """
        used to convert numpy matrix to balimage matrix
        """
        self._matrix.m[0] = numpy_matrix[0,0]
        self._matrix.m[1] = numpy_matrix[0,1]
        self._matrix.m[2] = numpy_matrix[0,2]
        self._matrix.m[3] = numpy_matrix[0,3]
        self._matrix.m[4] = numpy_matrix[1,0]
        self._matrix.m[5] = numpy_matrix[1,1]
        self._matrix.m[6] = numpy_matrix[1,2]
        self._matrix.m[7] = numpy_matrix[1,3]
        self._matrix.m[8] = numpy_matrix[2,0]
        self._matrix.m[9] = numpy_matrix[2,1]
        self._matrix.m[10] = numpy_matrix[2,2]
        self._matrix.m[11] = numpy_matrix[2,3]
        self._matrix.m[12] = numpy_matrix[3,0]
        self._matrix.m[13] = numpy_matrix[3,1]
        self._matrix.m[14] = numpy_matrix[3,2]
        self._matrix.m[15] = numpy_matrix[3,3]
        #matrixToAscii(self._matrix)


    def _get_matrix(self):
        """
        return an instance of _MATRIX object
        """
        return self._matrix

    def real2voxel(self):
        """
        Convert the matrix from voxel world to real
        """
        vrx,vry,vrz = self.img_ref.resolution
        vfx,vfy,vfz = self.img_flo.resolution

        # for the diagonal
        self._matrix.m[0]  = self._matrix.m[0]  *  vfx /  vrx
        self._matrix.m[5]  = self._matrix.m[5]  *  vfy /  vry
        self._matrix.m[10] = self._matrix.m[10] *  vfz /  vrz

        # for the rotation matrix
        self._matrix.m[1] = self._matrix.m[1] *  vfy /  vrx
        self._matrix.m[2] = self._matrix.m[2] *  vfz /  vrx
        self._matrix.m[4] = self._matrix.m[4] *  vfx /  vry
        self._matrix.m[6] = self._matrix.m[6] *  vfz /  vry
        self._matrix.m[8] = self._matrix.m[8] *  vfx /  vrz
        self._matrix.m[9] = self._matrix.m[9] *  vfy /  vrz

        # for the translation vector
        self._matrix.m[3] = self._matrix.m[3]   /  vrx
        self._matrix.m[7] = self._matrix.m[7]   /  vry
        self._matrix.m[11] = self._matrix.m[11] /  vrz

        self._matrix.m[12] = self._matrix.m[13] = self._matrix.m[14] = 0.0
        self._matrix.m[15] = 1.0

        return self._matrix

class Param(object):
    """
    Definition of Param object
    """
    def __init__(self):
        """
        """
        self._param = _PARAM()

    def _set_default(self):
        """
        used to set parameters to default
        """
        baladin_lib.BAL_SetParametersToDefault(pointer(self._param))

    def _set_auto(self):
        """
        used to set parameters to auto
        """
        baladin_lib.BAL_SetParametersToAuto(pointer(self._param))

    def _get_parameters(self):
        return self._param

    def _from_dict(self,parameters):
        """
        used to set parameters from a dictionnary
        """
        for k,v in parameters.iteritems():
            if hasattr(self._param, k):
                setattr(self._param,k,v)
            else:
                print "%s is not a valid parameter..." %k
                continue

class BalImage(object):
    """
    Definition of BalImage object
    """
    def __init__(self,image):
        """
        Initialization :

        :Parameters:
        - `image` (array) - image to convert
        """
        if image.ndim == 2 :
            xdim,ydim,zdim = image.shape + (1,)
            vx,vy,vz = image.resolution + (1.,)
            image.shape = (xdim,ydim,zdim)
            image.resolution = (vx,vy,vz)

        self._data = image
        self.bal_image = None

    def _from_dtype(self):
        """
        used to get information from numpy array
        """
        if self._data.dtype == np.uint8 :
            _vtype = VOXELTYPE.VT_UNSIGNED_CHAR
            _cdtype = c_ubyte
        elif self._data.dtype == np.uint16 :
            _vtype = VOXELTYPE.VT_UNSIGNED_SHORT
            _cdtype = c_ushort
        elif self._data.dtype == np.int16 :
            _vtype = VOXELTYPE.VT_SIGNED_SHORT
            _cdtype = c_short
        elif self._data.dtype == np.uint32 :
            _vtype = VOXELTYPE.VT_UNSIGNED_INT
            _cdtype = c_uint
        elif self._data.dtype == np.int32 :
            _vtype = VOXELTYPE.VT_SIGNED_INT
            _cdtype = c_int
        elif self._data.dtype == np.uint64 :
            _vtype = VOXELTYPE.VT_UNSIGNED_LONG
            _cdtype = c_ulong
        elif self._data.dtype == np.int64 :
            _vtype = VOXELTYPE.VT_SIGNED_LONG
            _cdtype = c_long
        elif self._data.dtype == np.float32 :
            _vtype = VOXELTYPE.VT_FLOAT
            _cdtype = c_float
        elif self._data.dtype == np.float64 :
            _vtype = VOXELTYPE.VT_DOUBLE
            _cdtype = c_double
        #elif self._data.dtype == np.float128 :
        #    _vtype = VOXELTYPE.
        #    _cdtype = c_longdouble
        else :
            raise UserWarning("unable to write that type of datas : %s" % str(mat.dtype) )
        return _vtype, _cdtype

    def _get_bal_image(self):
        """
        used to set attributes of BAL_IMAGE structure
        """
        _vx,_vy,_vz = self._data.resolution

        _xdim,_ydim,_zdim = self._data.shape
        _vdim = 1
        _vtype,_cdtype = self._from_dtype()

        # Data pointer cast to a particular c-types object
        _data = self._data.ctypes.data_as(c_void_p)
        _array = 0

        # initialization of BAL_IMAGE structure
        bal_image = _BAL_IMAGE(_xdim,_ydim,_zdim,_vdim,_vtype,_data,_array,
                                _vx,_vy,_vz)

        baladin_lib.BAL_AllocImageArray( pointer(bal_image) )
        baladin_lib.BAL_BuildImageArray( pointer(bal_image) )

        self.bal_image = bal_image
        return self.bal_image

    def get_spatial_image(self) :
        """
        """
        _vtype,_cdtype = self._from_dtype()
        _ct_array = (_cdtype * self._data.size).from_address(self.bal_image.data)
        _np_array = np.ctypeslib.as_array(_ct_array)
        x,y,z = self._data.shape
        arr =  np.array(_np_array.reshape(z,x,y).transpose(2,1,0))
        return SpatialImage(arr, self._data.resolution)


def baladin( ref, flo, inivox=None, inireel=None, vsf=None, vsr=None, ltf=None, htf=None,
             ltr=None, htr=None, fbr=None, fbf=None, transformation=None,
             estimator=None, ltscut=None, similarity_measure=None, tsi=None,
             nbiter=None, rms=None, bld=None, blp=None, blb=None, bldv=None, blpv=None,
             v=None, vd=None, vs=None, nov=None, pyn=None, pys=None, pyfilt=None,
             auto=None, inv=None, stop=None, only_register=False) :
    """
    It processes to an automated linear registration method using a block-matching based method.

    The principle of this method is to pair sub-images (or blocks) between both images to be registered
    and then to compute a transformation that explains the obtained pairings.
    Pairing is achieved by maximizing the correlation coefficient between blocks of the two images,
    while the rigid transformation that best superimposes them is computed by minimizing the squared distances between the paired blocks centers.
    This is iterated until convergence, and embedded into a multi-scale strategy.

    :Controling the output:
    By default an image is resampled (either the floating or the reference depending on the inv. If you just want only
    to compute the transformation, pass only_register=True. (The returned value will still be a tuple, but the first element
    will be None instead of an image).

    By default too the returned matrix is inverted - from (floating_image)' to floating_image. This is undesired if you want to
    use the matrix in a matrix composition. If you want the direct matrix pass direct_matrix=True.

    :Parameters:

    - `ref` (|SpatialImage|) - reference image

    - `flo` (|SpatialImage|) - floating image

    - `inivox` (numpy.ndarray) - initial matrix : name of the initial transformation (voxel coordinates) from reference to floating

    - `inireel` (numpy.ndarray) - initial real matrix : name of the initial transformation (coordinates of the 'real world')

    - `vsf` (float,float,float) - voxel size of the floating image overrides the one given in the image header (if any)

    - `vsr` (float,float,float) - voxel size of the reference image overrides the one given in the image header (if any)

    - `ltf` (int) - low threshold for the floating image

    - `htf` (int) - high threshold for the floating image
                    points of the floating image that will be considered have a value strictly
                    superior to the low threshold and strictly inferior to the high threshold

    - `ltr` (int) - low threshold for the reference image
                    points of the reference image that will be considered have a value strictly
                    superior to the low threshold and strictly inferior to the high threshold

    - `htr` (int) - high threshold for the reference image

    - `fbr` (float) - fraction block reference : A block of the reference image will be considered if it contains at least
                     this fraction of voxels with an intensity between the low and the high threshold (default is 0.5)

    - `fbf` (float) - fraction block floating : A block of the floating image will be considered if it contains at least
                      this fraction of voxels with an intensity between the low and the high threshold

    - `transformation` (str) - type of transformation, choices are :
                               * rigi[d],
                               * simi[litude],
                               * affi[ne

    - `estimator` (str) -  type of estimator, choices are :
                           * ltsw: Weighted Least Trimmed Squares
                           * lts:  Least Trimmed Squares
                           * lsw:  Weighted Least Squares
                           * ls:   Least Squares

    - `ltscut` (float) - cutting value for (weighted) least trimmed squares

    - `similarity_measure` (str) - type of similarity measure, choices are
                                   * cc: correlation coefficient
                                   * ecc: extended correlation coefficient

    - `tsi` (float) - threshold on the similarity measure : pairings below that threshold will not be considered

    - `nbiter` (int) - maximum number of iterations at one level of the pyramid

    - `rms` (bool) - use the RMS as an end condition at each pyramid level

    - `bld` (int,int,int) - block sizes : sizes of the blocks along X, Y, Z

    - `blp` (int,int,int) - block-spacing : block spacing in the floating image

    - `blb` (int,int,int) - blocks borders: to be added twice at each dimension for statistics computation

    - `bldv` (int,int,int) - block neighborhood sizes : sizes of the exploration neighborhood around a block

    - `blpv` (int,int,int) - block-steps : progression-step in the exploration neighborhood

    - `v` (float) - fraction variance blocks : consider only a fraction of all the blocks (the ones with the highest variance) at the coarser
                    level of the pyramid

    - `vd` (float) - decrement fraction variance blocks : the decrement of this fraction from one level of the pyramid to the next (default is 0.2)

    - `vs` (float) - minimum fraction variance blocks : the minimum admissible value of this fraction

    - `nov` (bool) - no fraction variance blocks : do not decrease the initial value of this fraction.
                     The constant value of the fraction is set to 1.0 but can be changed afterwards with '-fraction-variance-blocks'

    - `pyn` (int) - pyramid levels : number of levels of the pyramid (default is 3)

    - `pys` (int) - pyramid finest level : stop at the level "pys" of the pyramid (default is 0, ie stop at the finest level)

    - `pyfilt` (int) - pyramid built by Gaussian (recursive) filtering

    - `auto` (bool) - automated version : set parameters to standard for automated version
                      warning : override the parameters already set by previous options

    - `inv` (bool) - after matching, resample reference image instead of floating one

    - `stop`(bool) - just resample : do not match the images. Just compute the transformation matrix from voxel sizes (and eventually input matrices)

    - `only_register` - does not create a resampled image, only computes the transformation. The returned image will be None

    :Returns:

    - im_res (|SpatialImage|) - result image

    - mat (numpy.ndarray) - result matrix

    """

    if not isinstance(ref,SpatialImage) :
	ref = SpatialImage(ref)
    if vsr is not None:
        print "vsr",vsr
        ref.resolution = vsr

    if not isinstance(flo,SpatialImage) :
	flo = SpatialImage(flo)
    if vsf is not None:
        print "vsf",vsf
        flo.resolution = vsf

    # instance of _BALIMAGE
    _balimage_reference = BalImage(ref)
    balimage_reference = _balimage_reference._get_bal_image()

    # instance of _BALIMAGE
    _balimage_float = BalImage(flo)
    balimage_float = _balimage_float._get_bal_image()

    # instance of _MATRIX
    if inivox is not None:
        # -- baladin wants a direct transform
        # not a resampling transform --
        mat = np.linalg.inv(inivox)
        _matrix_init = Matrix(ref,flo,mat)
        matrix_init = _matrix_init._get_matrix()
    elif inireel is not None :
        mat = np.linalg.inv(inireel)
        _matrix_init = Matrix(ref,flo,mat)
        matrix_init = _matrix_init.real2voxel()
    else:
        mat = np.identity(4)
        _matrix_init = Matrix(ref,flo,mat)
        matrix_init = _matrix_init.real2voxel()

    # instance of _MATRIX
    _matrix_result = Matrix(ref,flo,np.zeros((4,4)))
    matrix_result = _matrix_result.real2voxel()

    # instance of _PARAM
    _bal_param = Param()
    _bal_param._set_default()

    parameters = {}
    if ltf is not None:
        parameters["seuil_bas_flo"] = ltf
    if htf is not None:
        parameters["seuil_haut_flo"] = htf
    if ltr is not None:
        parameters["seuil_bas_ref"] = ltr
    if htr is not None:
        parameters["seuil_haut_ref"] = htr
    if fbr is not None:
        parameters["seuil_pourcent_ref"] = fbr
    if fbf is not None:
        parameters["seuil_pourcent_flo"] = fbf

    if transformation == "rigi":
        parameters["transfo"] = enumTypeTransfo.RIGIDE
    elif transformation == "simi":
        parameters["transfo"] = enumTypeTransfo.SIMILITUDE
    elif transformation == "affi":
        parameters["transfo"] = enumTypeTransfo.AFFINE

    if estimator == "ltsw":
        parameters["use_lts"] = 1
        parameters["estimateur"] = enumTypeEstimator.TYPE_LSSW
    elif estimator == "lts":
        parameters["use_lts"] = 1
        parameters["estimateur"] = enumTypeEstimator.TYPE_LS
    elif estimator == "lsw":
        parameters["use_lts"] = 0
        parameters["estimateur"] = enumTypeEstimator.TYPE_LSSW
    elif estimator == "ls":
        parameters["use_lts"] = 0
        parameters["estimateur"] = enumTypeEstimator.TYPE_LS

    if ltscut is not None:
        parameters["lts_cut"] = ltscut

    if similarity_measure == "cc":
        parameters["mesure"] = enumTypeMesure.MESURE_CC
    elif similarity_measure == "ecc":
        parameters["mesure"] = enumTypeMesure.MESURE_EXT_CC

    if tsi is not None:
        parameters["seuil_mesure"] = tsi

    if nbiter is not None:
        parameters["nbiter"] = nbiter

    if bld is not None:
        bl_dx, bl_dy, bl_dz = bld
        parameters["bl_dx"] = bl_dx
        parameters["bl_dy"] = bl_dy
        parameters["bl_dz"] = bl_dz

    if blp is not None:
        bl_next_x, bl_next_y, bl_next_z = blp
        parameters["bl_next_x"] = bl_next_x
        parameters["bl_next_y"] = bl_next_y
        parameters["bl_next_z"] = bl_next_z

    if blb is not None:
        bl_border_x, bl_border_y, bl_border_z = blb
        parameters["bl_border_x"] = bl_border_x
        parameters["bl_border_y"] = bl_border_y
        parameters["bl_border_z"] = bl_border_z

    if bldv is not None:
        bl_size_neigh_x, bl_size_neigh_y, bl_size_neigh_z = bldv
        parameters["bl_size_neigh_x"] = bl_size_neigh_x
        parameters["bl_size_neigh_y"] = bl_size_neigh_y
        parameters["bl_size_neigh_z"] = bl_size_neigh_z

    if blpv is not None:
        bl_next_neigh_x, bl_next_neigh_y, bl_next_neigh_z = blpv
        parameters["bl_next_neigh_x"] = bl_next_neigh_x
        parameters["bl_next_neigh_y"] = bl_next_neigh_y
        parameters["bl_next_neigh_z"] = bl_next_neigh_z

    if v is not None:
        parameters["bl_pourcent_var"] = v
    if vs is not None:
        parameters["bl_pourcent_var_min"] = vs
    if vd is not None:
        parameters["bl_pourcent_var_dec"] = vd
    if pyn is not None:
        parameters["pyn"] = pyn
    if pys is not None:
        parameters["pys"] = pys
    if pyfilt is not None:
        parameters["py_filt"] = pyfilt
    if rms is not None:
        parameters["rms"] = rms

    if nov is not None:
      parameters["bl_pourcent_var"] = 1.0
      parameters["bl_pourcent_var_min"] = 1.0
      parameters["bl_pourcent_var_dec"] = 0.0

    if auto :
        _bal_param._set_auto()

    _bal_param._from_dict(parameters)
    bal_param = _bal_param._get_parameters()

    # numpy array correspondant to the Block Matching Registration
    numpy_matrix = np.zeros((4,4))
    #print "matrix result:", matrix_result

    if not stop :
        # calling Pyramidal_Block_Matching function using ctypes
        # The result matrix in in voxels and in flo->ref direction
        baladin_lib.Pyramidal_Block_Matching(pointer(balimage_reference),
                                             pointer(balimage_float),
                                             pointer(matrix_init),
                                             pointer(matrix_result),
                                             pointer(bal_param))


    numpy_matrix[0,0] = matrix_result.m[0]
    numpy_matrix[0,1] = matrix_result.m[1]
    numpy_matrix[0,2] = matrix_result.m[2]
    numpy_matrix[0,3] = matrix_result.m[3]
    numpy_matrix[1,0] = matrix_result.m[4]
    numpy_matrix[1,1] = matrix_result.m[5]
    numpy_matrix[1,2] = matrix_result.m[6]
    numpy_matrix[1,3] = matrix_result.m[7]
    numpy_matrix[2,0] = matrix_result.m[8]
    numpy_matrix[2,1] = matrix_result.m[9]
    numpy_matrix[2,2] = matrix_result.m[10]
    numpy_matrix[2,3] = matrix_result.m[11]
    numpy_matrix[3,0] = matrix_result.m[12]
    numpy_matrix[3,1] = matrix_result.m[13]
    numpy_matrix[3,2] = matrix_result.m[14]
    numpy_matrix[3,3] = matrix_result.m[15]



    if not only_register:
        image_result = SpatialImage(np.zeros_like(ref),ref.resolution)
        _balimage_result = BalImage(image_result)
        balimage_result = _balimage_result._get_bal_image()

        if inv :
            _mat = Matrix(ref,flo,numpy_matrix)
            mat = _mat._get_matrix()
            if (baladin_lib.BAL_Reech3DTriLin4x4( pointer(balimage_reference), pointer(balimage_result), mat_inv.m ) != 1) :
                mylogger.error("unable to compute result image")
                return -1

        else:
            _mat_inv = Matrix(ref,flo,np.linalg.inv(numpy_matrix))
            mat_inv = _mat_inv._get_matrix()
            if ( baladin_lib.BAL_Reech3DTriLin4x4( pointer(balimage_float), pointer(balimage_result), mat_inv.m ) != 1 ) :
                mylogger.error("unable to compute result image")
                return -1


    im_res  = None if only_register else _balimage_result.get_spatial_image()
    mat_ret = np.linalg.inv(numpy_matrix)
    return im_res, mat_ret
