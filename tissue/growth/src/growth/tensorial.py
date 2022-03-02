# -*- python -*-
#
#       growth: geometrical transformations to grow tissues
#
#       Copyright 2006 INRIA - CIRAD - INRA  
#
#       File author(s): Jerome Chopard <jerome.chopard@sophia.inria.fr>
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
# 
#       OpenAlea WebSite : http://openalea.gforge.inria.fr
#
"""
This module import the main growth algorithms
"""

__license__= "Cecill-C"
__revision__=" $Id: $ "

from math import exp
from numpy import dot
from scipy.linalg import expm

def apply_strain1D (l, strain) :
	"""Apply a strain tensor in 1D
	to change length l.
	
	:Parameters:
	 - `l` (float) - the length that will change
	 - `strain` (float) - (tensor1D), relative
	    rate of growth
	
	:Return: length after transformation
	
	:Returns Type: float
	"""
	#return l * (1 + strain)
	return l * exp(strain)

def apply_strain2D (shape, strain) :
	"""Apply a strain tensor to change a shape
	
	Modify shape in place
	
	:Parameters:
	 - `shape` (dict of (pid,Vector2) ) -
	   position of points in the reference
	   state
	 - `strain` (2x2 array) - relative rate
	   of growth
	
	:Returns Type: None
	"""
	G = expm(strain)
	
	for i in range(3) :
		shape[i,:] = dot(G,shape[i,:])

#def apply_strain2D (ref_shape, strain) :
#	"""Apply a 2x2 strain tensor in 2D
#	to a triangle shape.
#	
#	ref_shape: tuple of float, (r1,r2,s2)
#	assume r0,s0,s1 are zero
#	strain: 2x2 array, relative rate of growth
#	voir 6 decembre#TODO a rediger
#	"""
#	R1,R2,S2 = ref_shape
#	
#	#derivatives
#	d1r = 1. / R1
#	d1s = - R2 / (R1 * S2)
#	d2s = 1. / S2
#	
#	#solve
#	s2 = S2 + strain[1,1] / d2s
#	r1 = R1 + strain[0,0] / d1r
#	r2 = R2 + (strain[0,1] + strain[1,0] + (R1 - r1) * d1s) / d2s
#	
#	#return
#	return (r1,r2,s2)


