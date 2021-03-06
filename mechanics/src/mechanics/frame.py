# -*- python -*-
# -*- coding: latin-1 -*-
#
#       frame : mechanics package
#
#       Copyright or © or Copr. 2006 INRIA - CIRAD - INRA  
#
#       File author(s): Jerome Chopard <jerome.chopard@sophia.inria.fr>
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
# 
#       VPlants WebSite : https://gforge.inria.fr/projects/vplants/
#
"""
This module defines a frame or coordinate system in space
"""

__license__ = "Cecill-C"
__revision__ = " $Id: frame.py 9234 2010-07-06 16:44:13Z chopard $ "

__all__ = ["Frame",
           "triangle_frame","tetrahedron_frame",
           "polygon_frame","mean_frame",
           "change_frame_tensor2","local_to_global3D"]

from numpy import (array,zeros,
                   dot,add,subtract,divide,tensordot,
                   cross,concatenate,transpose,sign)
from numpy.linalg import norm
from openalea.container import triangulate_polygon

class Frame (object) :
	"""An helping class to deal with change of referential in 3D space.
	"""
	
	def __init__ (self, axes = None, origin = None) :
		"""Constructor
		
		Construct a new orthonormal Frame
		default is the canonical one.
		
		:Parameters:
		 - `axes` ([array,array,array]) - orientation of axes each array is
		               the coordinate of the local axis in the global frame
		 - `origin` (array) - position of the origin of this frame
		               in the global frame
		"""
		if axes is None :
			self._axes = array( [(1,0,0),(0,1,0),(0,0,1)] )
		else :
			self._axes = array(tuple(divide(vec,norm(vec) ) for vec in axes) )
		
		if origin is None :
			self._origin = zeros(3)
		else :
			self._origin = array(origin)
	
	###############################################
	#
	#	accessors
	#
	###############################################
	def axis (self, i) :
		"""Return the coordinates of the ith axis of the frame
		
		:Returns Type: array
		"""
		return self._axes[i,:]
	
	def rotation_to_local (self) :
		"""Return the rotation associated with this frame
		
		Compute the 3x3 tensor R that transform a vector from a global frame
		to this local one.
		local_vec = R * global_vec
		
		:Returns Type: 3x3 array
		"""
		return self._axes
	
	def rotation_to_global (self) :
		"""Return the inverse rotation associated with this frame
		
		Compute the 3x3 tensor R that transform a vector from the local frame
		to a global one.
		global_vec = R * local_vec
		
		:Returns Type: 3x3 array
		"""
		return transpose(self._axes)
	
	def origin (self) :
		"""Origin of this frame
		
		:Returns Type: array
		"""
		return self._origin
	
	###############################################
	#
	#	change of referential
	#
	###############################################
	def local_vec (self, vec) :
		"""Local coordinates of a global vector
		
		:Parameters:
		 `vec` (float,float,float) - a vector in the global frame
		
		:Returns Type: array
		"""
		return dot(self._axes,vec)
	
	def global_vec (self, vec) :
		"""Global coordinates of a local vector
		
		:Parameters:
		 `vec` (float,float,float) - a vector in the local frame
		
		:Returns Type: array
		"""
		return dot(transpose(self._axes),vec)
	
	def local_point (self, point) :
		"""Local coordinates of a global point
		
		:Parameters:
		 `point` (floatnfloat,float) - a position in the global frame
		
		:Returns Type: array
		"""
		return self.local_vec(subtract(point,self._origin) )
	
	def global_point (self, point) :
		"""Global coordinates of a local point
		
		:Parameters:
		 `point` (float,float,float) - a position in the local frame
		
		:Returns Type: array
		"""
		return self.global_vec(point) + self._origin
	
	def local_tensor (self, tensor) :
		"""Local coordinates of a global tensor
		
		:Parameters:
		 - `tensor` (3x3 array) - tensor expressed in global coordinates
		
		:Returns Type: 3x3 array
		"""
		if len(tensor.shape) == 2 :
			return dot(self._axes,dot(tensor,transpose(self._axes) ) )
		else :
			raise UserWarning("tensor of order higher thant 2 not handled")
	
	def global_tensor (self, tensor) :
		"""Global coordinates of a local tensor
		
		:Parameters:
		 - `tensor` (3x3 array) - tensor expressed in local coordinates
		
		:Returns Type: 3x3 array
		"""
		if len(tensor.shape) == 2 :
			return dot(transpose(self._axes),dot(tensor,self._axes) )
		else :
			raise UserWarning("tensor of order higher than 2 not handled")
	
	###############################################
	#
	#	change of referential in the local plane O,Ox,Oy
	#
	###############################################
	def local_tensor2 (self, tensor) :
		"""Local coordinates of a global tensor
		expressed in the local plane Ox,Oy
		
		.. warning:: use this function only if the third axis of the frame
		             is colinear to the third axis of the global frame.
		
		:Parameters:
		 - `tensor` (array) - tensor expressed in global coordinates
		
		:Returns Type: array
		"""
		R = self._axes[:2,:2]
		nb = len(tensor.shape) - 1
		
		ret = tensordot(R,tensor,[1,nb])
		for i in xrange(1,len(tensor.shape) ) :
			ret = tensordot(R,ret,[1,nb])
		
		return ret
	
	def global_tensor2 (self, tensor) :
		"""Global coordinates of a local tensor
		
		.. warning:: use this function only if the third axis of the frame
		             is colinear to the third axis of the global frame.
		
		:Parameters:
		 - `tensor` (array) - tensor expressed in local coordinates
		
		:Returns Type: array
		"""
		R = transpose(self._axes[:2,:2])
		nb = len(tensor.shape) - 1
		
		ret = tensordot(R,tensor,[1,nb])
		for i in xrange(1,len(tensor.shape) ) :
			ret = tensordot(R,ret,[1,nb])
		
		return ret

def triangle_frame (pt1, pt2, pt3) :
	"""Compute the local frame of a triangle
	
	The returned frame is such as :
	 - The origin of the frame will be in pt1.
	 - The first axis Ox will be directed along pt2 - pt1
	 - The second axis OY will be in the plane of the triangle
	   such as : Ox . Oy = 0
	 - The third axis Oz will be perpendicular to the plane
	   such as : Oz = Ox ^ Oy
	
	:Parameters:
	 - `pt1` (float,float,float) - first corner of the triangle
	 - `pt2` (float,float,float) - second corner of the triangle
	 - `pt3` (float,float,float) - third corner of the triangle
	
	:Returns Type: :class:`Frame`
	
	:Examples:
	
	>>> from numpy import array
	>>> a = (1,1,1)
	>>> b = (2,1,1)
	>>> c = (1,2,1)
	>>> fr = triangle_frame(a,b,c)
	>>>
	>>> fr.global_point( (0,0,0) )
	array([1,1,1])
	>>> fr.global_point( (1,0,0) )
	array([2,1,1])
	>>> fr.local_point( (2,2,2) )
	array([1,1,1])
	"""
	er = subtract(pt2,pt1)
	et = cross(er,subtract(pt3,pt1) )
	es = cross(et,er)
	return Frame( (er,es,et),pt1)

def tetrahedron_frame (pt1, pt2, pt3, pt4) :
	"""Compute the local frame of a tetrahedron
	
	The returned frame is such as :
	 - The origin of the frame will be in pt1.
	 - The first axis Ox will be directed along pt2 - pt1
	 - The second axis OY will be in the plane of the triangle pt1,pt2,pt3
	   such as : Ox . Oy = 0
	 - The third axis Oz will be perpendicular to the plane pt1,pt2,pt3
	   and oriented toward pt4
	   such as : Oz = Ox ^ Oy
	
	:Parameters:
	 - `pt1` (float,float,float) - first corner of the tetrahedron
	 - `pt2` (float,float,float) - second corner of the tetrahedron
	 - `pt3` (float,float,float) - third corner of the tetrahedron
	 - `pt4` (float,float,float) - fourth corner of the tetrahedron
	
	:Returns Type: :class:`Frame`
	
	:Examples:
	
	>>> from numpy import array
	>>> a = (1,1,1)
	>>> b = (2,1,1)
	>>> c = (1,2,1)
	>>> d = (1,1,2)
	>>> fr = tetrahedron_frame(a,b,c,d)
	>>>
	>>> fr.global_point( (0,0,0) )
	array([1,1,1])
	>>> fr.global_point( (1,0,0) )
	array([2,1,1])
	>>> fr.local_point( (2,2,2) )
	array([1,1,1])
	"""
	er = subtract(pt2,pt1)
	et = cross(er,subtract(pt3,pt1) )
	et *= sign(dot(et,subtract(pt4,pt1) ) )
	es = cross(et,er)
	return Frame( (er,es,et),pt1)

def mean_frame (frames) :
	"""Compute the mean frame of all given frames.
	
	The returned frame is such as:
	 - The origin of the frame is the barycenter of all frames
	 - The third axis is the mean third axes of all frames
	 - The first axis is the vector which is near the mean first axis of all
	   frames in the plane normal to Oz
	
	:Parameters:
	 - `frames` (list of `Frame`)
	
	:Returns Type: :class:`Frame`
	"""
	O = reduce(add,(fr.origin() for fr in frames) ) / len(frames)
	
	et = reduce(add,(fr.axis(2) for fr in frames) ) / len(frames)
	et = divide(et,norm(et) )
	
	Vref = frames[0].axis(1)
	tmp = reduce(add,(fr.axis(1) * sign(Vref,fr.axis(1) ) for fr in frames) ) \
	          / len(frames)
	
	er = cross(tmp,et)
	er = divide(er,norm(er) )
	
	es = cross(et,er)
	
	return Frame( (er,es,et),O)

def polygon_frame (corners) :
	"""Compute local frame associated with a flat convex polygon
	
	:Parameters:
	 - `corners` (list of array) - oriented corners of the polygon
	
	:Returns Type: :class:`Frame`
	"""
	pids = list(xrange(len(corners) ) )
	return mean_frame([triangle_frame(*tuple(corners[i] for i in tr) ) \
	                   for tr in triangulate_polygon(pids)])

def change_frame_tensor2 (T, frame1, frame2) :
	"""Change the reference frame of a tensor
	
	.. warning:: this function has a meaning only if the third axis 
	             of both frames is the same
	
	:Parameters:
	 - `T` (2x2 array) - tensor
	 - `frame1` (`Frame`) - frame in which the tensor `T` is currently expressed
	 - `frame2` (`Frame`) - frame in which the tensor `T` will be expressed
	
	:Returns Type: 2x2 array
	"""
	
	O1,(er1,es1,et1) = tuple(frame1)
	O2,(er2,es2,et2) = tuple(frame2)
	
	er = frame2.local_vec(er1)
	er = array( (er[0],er[1],0) )
	er = divide(er,norm(er) )
	
	es = frame2.local_vec(es1)
	es = array( (es[0],es[1],0) )
	es = divide(es,norm(es) )
	
	et = cross(er,es)
	
	fr = Frame( (er,es,et), array( (0,0,0) ) )
	
	return fr.global_tensor2(T)

def local_to_global3D (frame, tensor) :
	"""Express a tensor 2 into a world coordinate
	
	:Parameters:
	 - `frame` (Frame) - frame in which the tensor is expressed
	  - `tensor` (2x2 array) - local expression of the tensor
	
	:Returns Type: 3x3 array
	"""
	T = zeros( (3,3) )
	T[:2,:2] = tensor
	return frame.global_tensor(T)


















