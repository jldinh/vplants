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
This module growth the reference shape of a spring
"""

__license__= "Cecill-C"
__revision__=" $Id: $ "

from numpy import diag,dot,transpose
from numpy.linalg import eig
from openalea.mechanics import LinearSpring3D,Membrane3D
from tensorial import apply_strain1D,apply_strain2D

class MecaGrowth (object) :
	"""Grow reference shape of springs
	"""
	def __init__ (self, springs, strain_threshold, gamma) :
		"""Initialize the algorithm.
		
		.. math:
		   G = (strain - strain_threshold) * gamma * dt
		
		:Parameters:
		 - `springs` (list of Springs)
		 - `strain_threshold` (float) - threshold
		    above which growth occurs
		 - `gamma` (float) - speed of growth
		
		:Return: None modify springs in place
		"""
		self._springs = springs
		self._strain_threshold = strain_threshold
		self._gamma = gamma
	
	def grow (self, pos, dt) :
		"""Apply growth
		"""
		gamma = self._gamma * dt
		th = self._strain_threshold
		
		for sp in self._springs :
			st = sp.strain(pos)
			if isinstance(sp,LinearSpring3D) :
				if st > th :
					G = (st - th) * gamma
					L = apply_strain1D(sp.ref_length(),G)
					sp.set_ref_length(L)
			elif isinstance(sp,Membrane3D) :
				w,v = eig(st)
				for i in (0,1) :
					if w[i] > th :
						w[i] = (w[i] - th) * gamma
					else :
						w[i] = 0
				
				if w[0] > 0 or w[1] > 0 :
					G = dot(v,dot(diag(w),transpose(v) ) )
					
					RS = sp.ref_shape()
					apply_strain2D(RS,G)
					sp.set_ref_shape(RS)
			else :
				raise UserWarning("unable to handle this spring: %s" % str(sp) )


