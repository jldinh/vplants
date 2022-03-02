# -*- python -*-
# -*- coding: latin-1 -*-
#
#       vplants.asclepios.vt_exec.recfilters
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

#Loading dynamic link libraries
libvt = cdll.LoadLibrary(find_library('vt'))
libbasic = cdll.LoadLibrary(find_library('basic'))

import numpy as np
from vplants.asclepios.vt.vt_image import _VT_IMAGE, VT_Image
from openalea.image.spatial_image import SpatialImage
from openalea.core import logger

mylogger = logger.get_logger(__name__)


class derivativeOrder :
    NODERIVATIVE  = -1          # no derivative (no filtering)
    DERIVATIVE_0  = 0           # smoothing
    SMOOTHING     = 0           # smoothing
    DERIVATIVE_1  = 1           # derivative of order 1
    DERIVATIVE_2  = 2           # derivative of order 2
    DERIVATIVE_3  = 3           # derivative of order 3
    DERIVATIVE_1_CONTOURS = 11  # derivative of order 1, normalization adapted to
				# contours. The response to a step-edge is the
				# height of the step.

    DERIVATIVE_1_EDGES = 11     # derivative of order 1, normalization adapted to
				# contours. The response to a step-edge is the
				# height of the step.


class recursiveFilterType :
    UNKNOWN_FILTER = 0    # unknown filter type
    ALPHA_DERICHE = 1     # Deriche's filter (exponential (- alpha |X|))
    GAUSSIAN_DERICHE = 2  # gaussian approximation (Deriche's coefficients)
    GAUSSIAN_FIDRICH = 3  # gaussian approximation (Fidrich's coefficients)


def _get_buffer(image):
    dt = image._to_c_type()
    size = image.dim.x * image.dim.y * image.dim.z
    print image.dim.x, image.dim.y, image.dim.z
    return (dt * size).from_address(image.buf)


def recfilters (img,filter_type="sigma",filter_value=None,xyz=None,cont=None,edges=False,inv=False,swap=False):
    """
    - `image` (|SpatialImage|) - input image

    - `filter_type` (str, optional) - type of filtering :
                                        * "alpha" for Deriche recursive filter
                                        * "sigma" for Gaussian filter
                                        * "gradient"
                                        * "gradient_extrema"
                                        * "laplacian"
                                        * "gradient_laplacian"
                                        * "hessian"
                                        * "gradient_hessian"
                                        * "neg"
                                        * "pos"

    - `filter_value` (float or (float,float,float), required for "alpha" and "sigma") - standard deviation of the Gaussian according to X,Y or Z

    - `xyz` ( (int,int,int), optional) - derivation order according to X, Y or Z :
                                            * 0 : smoothing,
                                            * 1 : derivative of order 1
                                            * 2 : derivative of order 2
                                            * 3 : derivative of order 3
                                            default : no derivative (no filtering)

    - `cont` (int or (int,int,int), optional) - added points to the edges

    """
    mylogger.info("init parameters")

    derivatives = c_int * 3
    c_derivatives = derivatives(derivativeOrder.NODERIVATIVE,
                                derivativeOrder.NODERIVATIVE,
                                derivativeOrder.NODERIVATIVE)



    borderLengths = c_int * 3
    c_borderLengths = borderLengths(0,0,0)

    filterType = recursiveFilterType.GAUSSIAN_DERICHE

    filterCoefs = c_float * 3
    c_filterCoefs = filterCoefs(1.0,1.0,1.0)

    bool_contours = 0

    if xyz is not None:
        x,y,z = xyz
        d = dict(zip((0,1,2,3),(derivativeOrder.DERIVATIVE_0,
                                derivativeOrder.DERIVATIVE_1,
                                derivativeOrder.DERIVATIVE_2,
                                derivativeOrder.DERIVATIVE_3)))
        if x in d.iterkeys() :
            dx = d[x]
        else:
            dx = derivativeOrder.NODERIVATIVE
        if y in d.iterkeys() :
            dy = d[y]
        else:
            dy = derivativeOrder.NODERIVATIVE
        if z in d.iterkeys() :
            dz = d[z]
        else:
            dz = derivativeOrder.NODERIVATIVE

        c_derivatives = derivatives(dx,dy,dz)

    if cont is not None :
        if isinstance(cont,tuple):
            cx,cy,cz = cont
            c_borderLengths = borderLengths(cx,cy,cz)
        else :
            c_borderLengths = borderLengths(cont,cont,cont)

    if edges :
        bool_contours = 1

    mylogger.info("reading of input image")
    if not isinstance(img, SpatialImage) :
	img = SpatialImage(img)
    vt_image = VT_Image(img)
    image = vt_image.get_vt_image()

    if inv :  libvt.VT_InverseImage( image )
    if swap : libvt.VT_SwapImage( image )

    mylogger.info("initialization of result image")
    res_spa = SpatialImage(np.zeros((img.shape), dtype=img.dtype), img.resolution)
    vt_res = VT_Image(res_spa)
    imres = vt_res.get_vt_image()

    theDims = c_int * 3
    c_theDims = theDims(*img.shape)
    print img.shape

    if filter_type == 'alpha' or filter_type == 'sigma':
        if filter_value is None :
            raise RuntimeError, 'filter value is required'
        else :
            if isinstance(filter_value,tuple):
                vx,vy,vz = filter_value
                c_filterCoefs = filterCoefs(vx,vy,vz)
            else :
                c_filterCoefs = filterCoefs(filter_value,filter_value,filter_value)

            if filter_type == 'alpha':
                filterType = recursiveFilterType.ALPHA_DERICHE

            if ( libbasic.RecursiveFilterOnBuffer( _get_buffer(image), image.type,
		                          _get_buffer(imres), imres.type, c_theDims,
				          c_borderLengths, c_derivatives,
				          c_filterCoefs, c_int(filterType) ) != 1 ) :
                mylogger.error("unable to filter input image")
                return -1

    elif filter_type == 'gradient':
        if ( libbasic.GradientModulus( _get_buffer(image), image.type, _get_buffer(imres), imres.type,
			  theDims, borderLengths, filterCoefs, filterType ) == 0 ) :
            mylogger.error("processing failed")
            return -1

    elif filter_type == 'gradient_extrema' :
        if ( libbasic.Extract_Gradient_Maxima_2D( _get_buffer(image), image.type,
				     _get_buffer(imres), imres.type,
				     theDims, borderLengths, filterCoefs, filterType ) == 0 ) :
            mylogger.error("processing failed")
            return -1

    elif filter_type == 'laplacian' :
        if ( libbasic.Laplacian( _get_buffer(image), image.type,
		       _get_buffer(imres), imres.type,
		       theDims, borderLengths, filterCoefs, filterType ) == 0 ) :
            mylogger.error("processing failed")
            return -1

    elif filter_type == 'gradient_laplacian' :
        if ( libbasic.Gradient_On_Laplacian_ZeroCrossings_2D( _get_buffer(image), image.type,
		       _get_buffer(imres), imres.type,
		       theDims,
		       borderLengths,
		       filterCoefs,
		       filterType ) == 0 ) :
            mylogger.error("processing failed")
            return -1

    elif filter_type == 'hessian' :
        if ( libbasic.GradientHessianGradient( _get_buffer(image), image.type,
		       _get_buffer(imres), imres.type,
		       theDims,
		       borderLengths,
		       filterCoefs,
		       filterType ) == 0 ) :
            mylogger.error("processing failed")
            return -1

    elif filter_type == 'gradient_hessian' :
        if ( libbasic.Gradient_On_GradientHessianGradient_ZeroCrossings_2D( _get_buffer(image), image.type,
		       _get_buffer(imres), imres.type,
		       theDims,
		       borderLengths,
		       filterCoefs,
		       filterType ) == 0 ) :
            mylogger.error("processing failed")
            return -1

    elif filter_type == 'neg' :
        libbasic.ZeroCrossings_Are_Negative()

    elif filter_type == 'pos' :
        libbasic.ZeroCrossings_Are_Positive()

    else :
        raise RuntimeError, 'filter type not supported'

    # return vt_res.get_spatial_image()
    return res_spa #libvt has already written to the buffer.

