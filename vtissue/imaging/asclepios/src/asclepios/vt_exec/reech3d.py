# -*- python -*-
#
#       vplants.asclepios.vt_exec.reech3d
#
#       Copyright 2006-2011 INRIA - CIRAD - INRA
#
#       File author(s): Eric Moscardi <eric.moscardi@sophia.inria.fr>
#                       Daniel BARBEAU <daniel.barbeau@inria.fr>
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

import ctypes
from ctypes import *
from openalea.core.ctypes_ext import find_library

#Loading dynamic link libraries
libvt = cdll.LoadLibrary(find_library('vt'))

from copy import deepcopy
from math import sqrt
import numpy as np

from openalea.image.algo.basic import color2grey
from openalea.image.registration.matrix import compute_rank, inverse_matrix, matrix_real2voxels
from openalea.image.spatial_image import SpatialImage
from vplants.asclepios.vt.vt_image import _VT_IMAGE, VT_Image

MODE_RESIZE    = 0
MODE_MATRICE   = 1
MODE_DEFBACK   = 2
MODE_ISOTROPIC = 3

INTR_LINEAR  = 0
INTR_NEAREST = 1
INTR_CSPLINE = 2

interp_mode = [ "linear",
                "nearest",
                "cspline" ]


def reech3d (img, mat=None, mat_before=None, deformation=None,
                gain=1.0, bias=0.0, interpolation="linear", iso=1.0,
                output_shape=None, vin=None, vout=None,
                inv=False, inv_before=False, swap=False) :
    """
    This function allows 2D or 3D image resampling using a 4x4 matrix.
    The value of a point in the result image is estimated :
        * either by [bi|tri]linear interpolation,
        * or by using the value of the nearest point.

    : Parameters :
    - `image` (numpy.ndarray) - input image

    - `mat` (numpy.ndarray, optional) - Transformation matrix (4x4)
        from 'image-out' to 'image-in' : M(in) = MAT * M(out).

    - `mat_before` (numpy.ndarray, optional) - Other transformation matrix (4x4),
        in case of deformation field which is applied BEFORE the deformation field.

    - `deformation` (numpy.ndarray) - vector field based shape deformation applied before "matrix" :
        M(in) = MAT * ( M(out) + deformation ) and after "matrix_before" :
        M(in) = MAT * ( MATB*M(out) + deformation )

    - `gain` and `bias` (floats, optional) - The intensity is transformed by i*gain*bias
        (only with "deformation" and "linear")

    - `interpolation` (str, optional) - Type of interpolation according to given mode :
        * "linear" (Default),
        * "nearest",
        * "cspline".

    - `output_shape`(tuple, optional) - dimension of output image

    - `iso` (float, optional) - isotropic mode

    - `vin` (tuple, optional) - voxel size of input image

    - `vout` (tuple, optional) - voxel size of output image

    - `inv` (bool, optional) - inverse "matrix"

    - `inv_before` (bool, optional) - inverse "matrix_before"

    """
    ###############################################
    # parse params
    ###############################################
    if not isinstance(img, SpatialImage) :
	img = SpatialImage(img)

    if vin is None :
        vin = (1.,1.,1.)

    if vout is None :
        vout = (1.,1.,1.)

    if output_shape is not None:
        resdim = output_shape
    else:
        resdim = img.shape

    if interpolation not in interp_mode :
        print "Interpolation not supported"
        return -1

    _interp = dict(zip(("linear",    "nearest",    "cspline"),
                        (INTR_LINEAR, INTR_NEAREST, INTR_CSPLINE)))
    interp = _interp[interpolation]

    mode = MODE_RESIZE
    if deformation is not None:
        mode = MODE_DEFBACK
    if mat is not None:
        if mode != MODE_DEFBACK:
            mode = MODE_MATRICE
    if iso != 1.0 :
        mode = MODE_ISOTROPIC

    matrix = deepcopy(mat)
    matrix_before = deepcopy(mat_before)

    bias_gain = False
    if bias != 0.0 : bias_gain = True
    if gain != 1.0 : bias_gain = True

    ###############################################
    # creating of vt_image
    ###############################################

    vt_image = VT_Image(img)
    image = vt_image.get_vt_image()


    ###############################################
    # eventually operations on the image
    ###############################################

    if ( swap ) : libvt.VT_SwapImage( pointer(image) )


    ###############################################
    #       MODE_MATRICE and MODE_DEFBACK
    ###############################################

    if (mode == MODE_MATRICE) or (mode == MODE_DEFBACK) :

        # "matrix"
        if matrix is not None :
            if matrix.shape != (4,4):
	        print "unable to read matrice"
                return -1
	        #libvt.VT_FreeImage( pointer(image) )
	        #libvt.VT_Free( pointer(image) )
            if inv :
	        matrix = inverse_matrix(matrix)
                if compute_rank(matrix) != 4 :
                    print "Warning: The rank of the matrix is different of 4"

        else : # matrix is None
            matrix = np.eye(4)

        matrix = matrix_real2voxels(matrix, vin, vout)

        # "matrix_before"
        if matrix_before is not None:
            if matrix_before.shape != (4,4):
	        #libvt.VT_FreeImage( pointer(image) )
	        #libvt.VT_Free( pointer(image) )
	        print "unable to read *before* matrice"
                return -1
            if inv_before :
                matrix_before = inverse_matrix(matrix_before)
                if compute_rank(matrix) != 4 :
                    print "Warning: The rank of the matrix_before is different of 4"

        else : # matrix_before is None
            matrix_before = np.eye(4)

        # "deformation"
        if deformation is not None :
            if len(deformation) != 3:
                print "unable to read deformation"


    ###############################################
    #       MODE_ISOTROPIC
    ###############################################

    if mode == MODE_ISOTROPIC :
        # on construit une matrice d'homothetie, de rapport resdim.x/image->dim.x.

        #   Si on considere que le point est le centre du voxel, l'image s'etend
        #   alors de -0.5 a dim-1+0.5, un bon reechantillonage est donc donne par
        #   (x+0.5) * resdim.x/image->dim.x - 0.5
        #
        # en fait, on construit la matrice inverse, pour le calcul

        matrix = matrix_before = np.eye(4)

        matrix[0,0] = iso / image.siz.x
        matrix[0,3] = 0.5 * (matrix[0,0] - 1.0)
        matrix[1,1] = iso / image.siz.y
        matrix[1,3] = 0.5 * (matrix[1,1] - 1.0)
        matrix[2,2] = iso / image.siz.z
        matrix[2,3] = 0.5 * (matrix[2,2] - 1.0)

        resdim_x = (int)( (image.dim.x * image.siz.x / iso) + 1 )
        resdim_y = (int)( (image.dim.y * image.siz.y / iso) + 1 )
        resdim_z = (int)( (image.dim.z * image.siz.z / iso) + 1 )


    ###############################################
    #       MODE_RESIZE
    ###############################################

    if mode == MODE_RESIZE :
        #/* on construit une matrice d'homothetie, de rapport resdim.x/image->dim.x.
        #
        #   Si on considere que le point est le centre du voxel, l'image s'etend
        #   alors de -0.5 a dim-1+0.5, un bon reechantillonage est donc donne par
        #   (x+0.5) * resdim.x/image->dim.x - 0.5
        #
        # en fait, on construit la matrice inverse, pour le calcul
        matrix = matrix_before = np.eye(4)

        matrix[0,0] = float (image.dim.x) / float (resdim[0])
        matrix[0,3] = 0.5 * (matrix[0,0] - 1.0)
        matrix[1,1] = float (image.dim.y) / float (resdim[1])
        matrix[1,3] = 0.5 * (matrix[1,1] - 1.0)
        matrix[2,2] = float (image.dim.z) / float (resdim[2])
        matrix[2,3] = 0.5 * (matrix[2,2] - 1.0)


    ###############################################
    #       Creating of vt_image for result image
    ###############################################

    img_res = SpatialImage(np.zeros((resdim),dtype=img.dtype),resolution=vout)
    vt_imres = VT_Image(img_res)
    imres = vt_imres.get_vt_image()

    # instance of MATRIX object
    mat = c_double * 16
    c_matrix = mat( *matrix.flatten().tolist() )

    # instance of MATRIX BEFORE object
    mat_b = c_double * 16
    c_matrix_before = mat_b( *matrix_before.flatten().tolist() )

    ###############################################
    #       Compute Transformation with
    #           MODE_DEFBACK mode
    ###############################################

    if mode == MODE_DEFBACK :
        print "\t mode deformation"
        # deformation.X
        vt_imdef_x = VT_Image( deformation[0] )
        imdef_x = vt_imdef_x.get_vt_image()

        # deformation.Y
        vt_imdef_y = VT_Image( deformation[1] )
        imdef_y = vt_imdef_y.get_vt_image()

        # deformation.Z
        vt_imdef_z = VT_Image( deformation[2] )
        imdef_z = vt_imdef_z.get_vt_image()

        # Deformation Object
        _imdef = POINTER(_VT_IMAGE) * 3
        imdef = _imdef(pointer(imdef_x),pointer(imdef_y),pointer(imdef_z))

        ###############################################
        #       interpolation INTR_NEAREST
        ###############################################

        if interp == INTR_NEAREST :
            print "\t interpolation : nearest"
	    if ( libvt.Reech3DNearestDefBack( pointer(image), pointer(imres), pointer(imdef),
                                                c_matrix, c_matrix_before ) != 1 ) :
	        #libvt.VT_FreeImage( pointer(image) )
	        #libvt.VT_FreeImage( pointer(imres) )
	        #libvt.VT_Free( pointer(image) )
	        #libvt.VT_FreeImage( imdef[0] )
	        #libvt.VT_Free( pointer(imdef[0]) )
	        #libvt.VT_FreeImage( imdef[1] )
	        #libvt.VT_Free( pointer(imdef[1]) )
	        #libvt.VT_FreeImage( imdef[2] )
	        #libvt.VT_Free( pointer(imdef[2]) )
	        #libvt.VT_ErrorParse("unable to compute result\n", 0)
	        print "unable to compute result"
                return -1

        ###############################################
        #       interpolation INTR_LINEAR
        ###############################################

        elif interp == INTR_LINEAR :
            print "\t interpolation : linear"
            if ( libvt.Reech3DTriLinDefBack( pointer(image), pointer(imres), pointer(imdef),
                                                c_matrix, c_matrix_before,
                                                c_double(gain), c_double(bias)) != 1) :
	        #libvt.VT_FreeImage( pointer(image) )
	        #libvt.VT_FreeImage( pointer(imres) )
	        #libvt.VT_Free( pointer(image) )
	        #libvt.VT_FreeImage( imdef[0] )
	        #libvt.VT_Free( pointer(imdef[0]) )
	        #libvt.VT_FreeImage( imdef[1] )
	        #libvt.VT_Free( pointer(imdef[1]) )
	        #libvt.VT_FreeImage( imdef[2] )
	        #libvt.VT_Free( pointer(imdef[2]) )
	        #libvt.VT_ErrorParse("unable to compute result\n", 0)
                print "unable to compute result"
                return -1

        else :
            print "... switch to linear interpolation"
            #libvt.VT_FreeImage( imdef[0] )
            #libvt.VT_Free( pointer(imdef[0]) )
            #libvt.VT_FreeImage( imdef[1])
            #libvt.VT_Free( pointer(imdef[1]) )
            #libvt.VT_FreeImage( imdef[2] )
            #libvt.VT_Free( pointer(imdef[2]) )

    ###############################################
    #       Compute Transformation with
    #           MODE_MATRICE or
    #           MODE_ISOTROPIC or
    #           MODE_RESIZE mode
    ###############################################

    else :
        ###############################################
        #               2D dimension
        ###############################################
        if ( imres.dim.z == 1 and image.dim.z == 1 ) :

            ###############################################
            #       interpolation INTR_NEAREST
            ###############################################

            if interp == INTR_NEAREST :
                print "\t interpolation : nearest"
	        if ( libvt.Reech2DNearest4x4( pointer(image), pointer(imres), c_matrix ) != 1 ) :
                    print "unable to compute result"
                    return -1

            ###############################################
            #       interpolation INTR_CSPLINE
            ###############################################

            if interp == INTR_CSPLINE :
                print "\t interpolation : spline"
	        if ( libvt.Reech3DCSpline4x4( pointer(image), pointer(imres), c_matrix ) != 1 ) :
                    print "unable to compute result"
                    return -1

            ###############################################
            #       interpolation INTR_LINEAR
            ###############################################

            if interp == INTR_LINEAR :
                print "\t interpolation : linear"
	        if bias_gain :
	            if ( libvt.Reech2DTriLin4x4gb( pointer(image), pointer(imres), c_matrix, c_float(gain), c_float(bias) ) != 1 ) :
	                print "unable to compute result"
                        return -1
	        else :
	            if ( libvt.Reech2DTriLin4x4( pointer(image), pointer(imres), c_matrix ) != 1 ) :
                        print "unable to compute result"
                        return -1


        ###############################################
        #               3D dimension
        ###############################################
        else :

            ###############################################
            #       interpolation INTR_NEAREST
            ###############################################

            if interp == INTR_NEAREST :
                print "\t interpolation : nearest"
	        if ( libvt.Reech3DNearest4x4( pointer(image), pointer(imres), c_matrix ) != 1 ) :
                    print "unable to compute result"
                    return -1

            ###############################################
            #       interpolation INTR_CSPLINE
            ###############################################

            if interp == INTR_CSPLINE :
                print "\t interpolation : spline"
                if ( libvt.Reech3DCSpline4x4( pointer(image), pointer(imres), c_matrix ) != 1 ) :
                    print "unable to compute result"
                    return -1

            ###############################################
            #       interpolation INTR_LINEAR
            ###############################################

            if interp == INTR_LINEAR :
                print "\t interpolation : linear"
	        if bias_gain :
	            if ( libvt.Reech3DTriLin4x4gb( pointer(image), pointer(imres), c_matrix, c_float(gain), c_float(bias) ) != 1 ) :
                        print "unable to compute result"
                        return -1
	        else :
	            if ( libvt.Reech3DTriLin4x4( pointer(image), pointer(imres), c_matrix ) != 1 ) :
                        print "unable to compute result"
                        return -1

    #if ( matrice_out[0] != '\0' ) WriteMatrice( par.matrice_out, mat );

    # Try to write an INRIMAGE
    #imres.name = 'outimage.inr.gz'
    #ret = libvt.VT_WriteInrimage( pointer(imres) )

    #/*--- ecriture de l'image resultat ---*/
    #if ( VT_WriteInrimage( &imres ) == -1 ) {
    #VT_FreeImage( image );
    #VT_FreeImage( &imres );
    #VT_Free( (void**)&image );
    #VT_ErrorParse("unable to write output image\n", 0);
    #}

    # free memories
    #_deallocate_images(image,imres)
    return img_res














###############################
# Attempt at simpler function #
###############################
C_MATRIX_T = c_double * 16
DEF_ARRAY_T = POINTER(_VT_IMAGE) * 3

def resample(img, interpolation="linear", matrix=None, deformation=None, homothety=None,
             output_shape=None, vout=None):
    """ This function is an attempt at a simpler implementation of the resampling function.
    It only accepts transforms as resampling, vox_space_ref to vox_space_flo voxel transforms.
    It does not invert or convert any transform.

    It is currently used by mars_alt.mars.fusion.fusion (not fusion_original).
    """
    # -- yes, I'm paranoid --
    assert isinstance(img, SpatialImage) and len(img.shape) == 3
    assert interpolation in ["linear", "nearest"]
    if matrix is not None:
        assert isinstance(matrix,np.ndarray) and matrix.shape == (4,4)
    if deformation is not None:
        assert isinstance(deformation, SpatialImage) and len(deformation.shape) == 4 and deformation.shape[3] == 3
        assert isinstance(homothety, np.ndarray) and matrix.shape == (4,4)
    assert isinstance(output_shape, (tuple, list, np.ndarray)) and len(output_shape) == 3
    # -- ok, should be fine by now --

    gain=1.0
    bias=0.0
    #############################################################################################
    # -- All transforms are given in voxel space AND are resampling transforms, ie: the inverse #
    # of the transforms that moves img to its new position --                                   #
    #############################################################################################

    # -- allocate result image --
    img_res  = SpatialImage(np.zeros((output_shape),dtype=img.dtype),resolution=vout)
    imres    = VT_Image.from_spatial_image(img_res)

    # -- convert input image to vt_image --
    image = VT_Image.from_spatial_image(img)

    # -- convert matrices --
    if matrix is not None:
        c_mat = C_MATRIX_T( *matrix.flatten().tolist() )
    else:
        c_mat = None

    if homothety is not None:
        c_mat_homo = C_MATRIX_T( *homothety.flatten().tolist() )
    else:
        c_mat_homo = None

    # -- ok, ready for resampling party --
    if deformation is not None:
        # -- split deformation image into three scalar images,
        # one per dimension, and pack them in a VT_IMAGE* array --
        deformation = color2grey(deformation)
        vt_defs = map(VT_Image.from_spatial_image, deformation)
        def_arr = DEF_ARRAY_T( *map(pointer, vt_defs) )

        if interpolation=="linear":
            if ( libvt.Reech3DTriLinDefBack( pointer(image), pointer(imres), pointer(def_arr),
                                             c_mat, c_mat_homo,
                                             c_double(gain), c_double(bias)) != 1) :
                raise Exception("Cannot perform deformable linear resampling")
        elif interpolation=="nearest":
            if ( libvt.Reech3DNearestDefBack( pointer(image), pointer(imres), pointer(imdef),
                                              c_mat, c_mat_homo ) != 1 ) :
                raise Exception("Cannot perform deformable nearest resampling")
        else:
            raise Exception("Unknown interpolation method : "+str(interpolation))

    else:
        if matrix is None:
            if homothety is not None:
                print "rescaling"
                # -- no matrix, no deformation, but a homothety ?
                # we probably want to simple rescale the image then! --
                c_mat = c_mat_homo
            else:
                raise Exception("resample got no matrix, no deformation nor homothety, can't decide what to do!")
        else:
             pass

        if interpolation == "linear" :
            if ( libvt.Reech3DTriLin4x4( pointer(image), pointer(imres), c_mat ) != 1 ) :
                raise Exception("Cannot perform affine linear resampling")
        elif interpolation == "nearest" :
            if ( libvt.Reech3DNearest4x4( pointer(image), pointer(imres), c_mat ) != 1 ) :
                raise Exception("Cannot perform affine nearest resampling")
        else:
            raise Exception("Unknown interpolation method : "+str(interpolation))

    return img_res










Float32Ptr = ctypes.POINTER(ctypes.c_float)
def reech3d_voxels (img, mat=None, mat_before=None, deformation=None,
                    gain=1.0, bias=0.0, interpolation="linear", iso=1.0,
                    output_shape=None, vin=None, vout=None,
                    inv=False, inv_before=False, swap=False
                    ) :
    """
    This function allows 2D or 3D image resampling using a 4x4 matrix.
    The value of a point in the result image is estimated :
        * either by [bi|tri]linear interpolation,
        * or by using the value of the nearest point.

    : Parameters :
    - `image` (numpy.ndarray) - input image

    - `mat` (numpy.ndarray, optional) - Transformation matrix (4x4)
        from 'image-out' to 'image-in' : M(in) = MAT * M(out).

    - `mat_before` (numpy.ndarray, optional) - Other transformation matrix (4x4),
        in case of deformation field which is applied BEFORE the deformation field.

    - `deformation` (numpy.ndarray) - vector field based shape deformation applied before "matrix" :
        M(in) = MAT * ( M(out) + deformation ) and after "matrix_before" :
        M(in) = MAT * ( MATB*M(out) + deformation )

    - `gain` and `bias` (floats, optional) - The intensity is transformed by i*gain*bias
        (only with "deformation" and "linear")

    - `interpolation` (str, optional) - Type of interpolation according to given mode :
        * "linear" (Default),
        * "nearest",
        * "cspline".

    - `output_shape`(tuple, optional) - dimension of output image

    - `iso` (float, optional) - isotropic mode

    - `vin` (tuple, optional) - voxel size of input image

    - `vout` (tuple, optional) - voxel size of output image

    - `inv` (bool, optional) - inverse "matrix"

    - `inv_before` (bool, optional) - inverse "matrix_before"

    """
    ###############################################
    # parse params
    ###############################################
    if not isinstance(img, SpatialImage) :
	img = SpatialImage(img)

    if vin is None :
        vin = (1.,1.,1.)

    if vout is None :
        vout = (1.,1.,1.)

    if output_shape is not None:
        resdim = output_shape
    else:
        resdim = img.shape

    if interpolation not in interp_mode :
        print "Interpolation not supported"
        return -1

    _interp = dict(zip(("linear",    "nearest",    "cspline"),
                        (INTR_LINEAR, INTR_NEAREST, INTR_CSPLINE)))
    interp = _interp[interpolation]

    mode = MODE_RESIZE
    if deformation is not None:
        mode = MODE_DEFBACK
    if mat is not None:
        if mode != MODE_DEFBACK:
            mode = MODE_MATRICE
    if iso != 1.0 :
        mode = MODE_ISOTROPIC

    matrix = deepcopy(mat)
    matrix_before = deepcopy(mat_before)

    bias_gain = False
    if bias != 0.0 : bias_gain = True
    if gain != 1.0 : bias_gain = True

    ###############################################
    # creating of vt_image
    ###############################################

    vt_image = VT_Image(img)
    image = vt_image.get_vt_image()


    ###############################################
    # eventually operations on the image
    ###############################################

    if ( swap ) : libvt.VT_SwapImage( pointer(image) )


    ###############################################
    #       MODE_MATRICE and MODE_DEFBACK
    ###############################################

    if (mode == MODE_MATRICE) or (mode == MODE_DEFBACK) :

        # "matrix"
        if matrix is not None :
            if matrix.shape != (4,4):
	        print "unable to read matrice"
                return -1
	        #libvt.VT_FreeImage( pointer(image) )
	        #libvt.VT_Free( pointer(image) )
            if inv :
	        matrix = inverse_matrix(matrix)
                if compute_rank(matrix) != 4 :
                    print "Warning: The rank of the matrix is different of 4"

        else : # matrix is None
            matrix = np.eye(4)


        # "matrix_before"
        if matrix_before is not None:
            if matrix_before.shape != (4,4):
	        #libvt.VT_FreeImage( pointer(image) )
	        #libvt.VT_Free( pointer(image) )
	        print "unable to read *before* matrice"
                return -1
            if inv_before :
                matrix_before = inverse_matrix(matrix_before)
                if compute_rank(matrix) != 4 :
                    print "Warning: The rank of the matrix_before is different of 4"

        else : # matrix_before is None
            matrix_before = np.eye(4)

        # "deformation"
        if deformation is not None :
            if isinstance(deformation, SpatialImage) and len(deformation.shape)==4:
                deformation = color2grey(deformation)

            if len(deformation) != 3:
                print "unable to read deformation"


    ###############################################
    #       MODE_ISOTROPIC
    ###############################################

    if mode == MODE_ISOTROPIC :
        # on construit une matrice d'homothetie, de rapport resdim.x/image->dim.x.

        #   Si on considere que le point est le centre du voxel, l'image s'etend
        #   alors de -0.5 a dim-1+0.5, un bon reechantillonage est donc donne par
        #   (x+0.5) * resdim.x/image->dim.x - 0.5
        #
        # en fait, on construit la matrice inverse, pour le calcul

        matrix = matrix_before = np.eye(4)

        matrix[0,0] = iso / image.siz.x
        matrix[0,3] = 0.5 * (matrix[0,0] - 1.0)
        matrix[1,1] = iso / image.siz.y
        matrix[1,3] = 0.5 * (matrix[1,1] - 1.0)
        matrix[2,2] = iso / image.siz.z
        matrix[2,3] = 0.5 * (matrix[2,2] - 1.0)

        resdim_x = (int)( (image.dim.x * image.siz.x / iso) + 1 )
        resdim_y = (int)( (image.dim.y * image.siz.y / iso) + 1 )
        resdim_z = (int)( (image.dim.z * image.siz.z / iso) + 1 )


    ###############################################
    #       MODE_RESIZE
    ###############################################

    if mode == MODE_RESIZE :
        #/* on construit une matrice d'homothetie, de rapport resdim.x/image->dim.x.
        #
        #   Si on considere que le point est le centre du voxel, l'image s'etend
        #   alors de -0.5 a dim-1+0.5, un bon reechantillonage est donc donne par
        #   (x+0.5) * resdim.x/image->dim.x - 0.5
        #
        # en fait, on construit la matrice inverse, pour le calcul
        matrix = matrix_before = np.eye(4)

        matrix[0,0] = float (image.dim.x) / float (resdim[0])
        matrix[0,3] = 0.5 * (matrix[0,0] - 1.0)
        matrix[1,1] = float (image.dim.y) / float (resdim[1])
        matrix[1,3] = 0.5 * (matrix[1,1] - 1.0)
        matrix[2,2] = float (image.dim.z) / float (resdim[2])
        matrix[2,3] = 0.5 * (matrix[2,2] - 1.0)


    ###############################################
    #       Creating of vt_image for result image
    ###############################################

    img_res = SpatialImage(np.zeros((resdim),dtype=img.dtype),resolution=vout)
    vt_imres = VT_Image(img_res)
    imres = vt_imres.get_vt_image()

    # instance of MATRIX object
    c_matrix = ctypes.cast(matrix.ctypes.data, Float32Ptr)

    # instance of MATRIX BEFORE object
    c_matrix_before = ctypes.cast(matrix_before.ctypes.data, Float32Ptr)


    ###############################################
    #       Compute Transformation with
    #           MODE_DEFBACK mode
    ###############################################

    if mode == MODE_DEFBACK :
        print "\t mode deformation"
        # deformation.X
        vt_imdef_x = VT_Image( deformation[0] )
        imdef_x = vt_imdef_x.get_vt_image()

        # deformation.Y
        vt_imdef_y = VT_Image( deformation[1] )
        imdef_y = vt_imdef_y.get_vt_image()

        # deformation.Z
        vt_imdef_z = VT_Image( deformation[2] )
        imdef_z = vt_imdef_z.get_vt_image()

        # Deformation Object
        _imdef = POINTER(_VT_IMAGE) * 3
        imdef = _imdef(pointer(imdef_x),pointer(imdef_y),pointer(imdef_z))

        ###############################################
        #       interpolation INTR_NEAREST
        ###############################################

        if interp == INTR_NEAREST :
            print "\t interpolation : nearest"
	    if ( libvt.Reech3DNearestDefBack( pointer(image), pointer(imres), pointer(imdef),
                                                c_matrix, c_matrix_before ) != 1 ) :
	        print "unable to compute result"
                return -1

        ###############################################
        #       interpolation INTR_LINEAR
        ###############################################

        elif interp == INTR_LINEAR :
            print "\t interpolation : linear"
            if ( libvt.Reech3DTriLinDefBack( pointer(image), pointer(imres), pointer(imdef),
                                                c_matrix, c_matrix_before,
                                                c_double(gain), c_double(bias)) != 1) :
                print "unable to compute result"
                return -1

        else :
            print "... switch to linear interpolation"

    ###############################################
    #       Compute Transformation with
    #           MODE_MATRICE or
    #           MODE_ISOTROPIC or
    #           MODE_RESIZE mode
    ###############################################

    else :
        ###############################################
        #               2D dimension
        ###############################################
        if ( imres.dim.z == 1 and image.dim.z == 1 ) :

            ###############################################
            #       interpolation INTR_NEAREST
            ###############################################

            if interp == INTR_NEAREST :
                print "\t interpolation : nearest"
	        if ( libvt.Reech2DNearest4x4( pointer(image), pointer(imres), c_matrix ) != 1 ) :
                    print "unable to compute result"
                    return -1

            ###############################################
            #       interpolation INTR_CSPLINE
            ###############################################

            if interp == INTR_CSPLINE :
                print "\t interpolation : spline"
	        if ( libvt.Reech3DCSpline4x4( pointer(image), pointer(imres), c_matrix ) != 1 ) :
                    print "unable to compute result"
                    return -1

            ###############################################
            #       interpolation INTR_LINEAR
            ###############################################

            if interp == INTR_LINEAR :
                print "\t interpolation : linear"
	        if bias_gain :
	            if ( libvt.Reech2DTriLin4x4gb( pointer(image), pointer(imres), c_matrix, c_float(gain), c_float(bias) ) != 1 ) :
	                print "unable to compute result"
                        return -1
	        else :
	            if ( libvt.Reech2DTriLin4x4( pointer(image), pointer(imres), c_matrix ) != 1 ) :
                        print "unable to compute result"
                        return -1


        ###############################################
        #               3D dimension
        ###############################################
        else :

            ###############################################
            #       interpolation INTR_NEAREST
            ###############################################

            if interp == INTR_NEAREST :
                print "\t interpolation : nearest"
	        if ( libvt.Reech3DNearest4x4( pointer(image), pointer(imres), c_matrix ) != 1 ) :
                    print "unable to compute result"
                    return -1

            ###############################################
            #       interpolation INTR_CSPLINE
            ###############################################

            if interp == INTR_CSPLINE :
                print "\t interpolation : spline"
                if ( libvt.Reech3DCSpline4x4( pointer(image), pointer(imres), c_matrix ) != 1 ) :
                    print "unable to compute result"
                    return -1

            ###############################################
            #       interpolation INTR_LINEAR
            ###############################################

            if interp == INTR_LINEAR :
                print "\t interpolation : linear"
	        if bias_gain :
	            if ( libvt.Reech3DTriLin4x4gb( pointer(image), pointer(imres), c_matrix, c_float(gain), c_float(bias) ) != 1 ) :
                        print "unable to compute result"
                        return -1
	        else :
	            if ( libvt.Reech3DTriLin4x4( pointer(image), pointer(imres), c_matrix ) != 1 ) :
                        print "unable to compute result"
                        return -1


    return img_res
