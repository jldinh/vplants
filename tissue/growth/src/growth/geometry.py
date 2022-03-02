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

__all__ = ["Uniform1D",
           "Uniform2D",
           "Uniform3D",
           "Radial",
           "Linear",
           "Unconstrained"]

from math import exp
from copy import copy
from vplants.plantgl.math import norm

class Uniform1D (object) :
	"""Defines a uniform scaling
	"""
	def __init__ (self, scaling) :
		"""Constructor
		
		Initialize the algorithm.
		
		:Parameters:
		 - `scaling` (float) - tells
		  the growth in each direction
		  of space
		"""
		self._scaling = scaling
	
	def grow (self, pos, dt) :
		"""Apply growth to a set of vectors
		
		Modify positions in place
		
		:Parameters:
		 - `pos` (dict of (pid,vec) ) -
		   spatial position of points
		 - `dt` (float) - time step
		"""
		sca = (1. + self._scaling * dt)
		for pid,vec in pos.iteritems() :
			pos[pid] = vec * sca

class Uniform2D (object) :
	"""Defines a uniform scaling
	"""
	def __init__ (self, scaling) :
		"""Constructor
		
		Initialize the algorithm.
		
		:Parameters:
		 - `scaling` (float,float) - tells
		  the growth in each direction
		  of space
		"""
		self._scaling = scaling
	
	def grow (self, pos, dt) :
		"""Apply growth to a set of vectors
		
		Modify positions in place
		
		:Parameters:
		 - `pos` (dict of (pid,vec) ) -
		   spatial position of points
		 - `dt` (float) - time step
		"""
		scax,scay = (1. + v * dt for v in self._scaling)
		for pid,vec in pos.iteritems() :
			vec.x *= scax
			vec.y *= scay

class Uniform3D (object) :
	"""Defines a uniform scaling
	"""
	def __init__ (self, scaling) :
		"""Constructor
		
		Initialize the algorithm.
		
		:Parameters:
		 - `scaling` (float,float,float) - tells
		  the growth in each direction
		  of space
		"""
		self._scaling = scaling
	
	def grow (self, pos, dt) :
		"""Apply growth to a set of vectors
		
		Modify positions in place
		
		:Parameters:
		 - `pos` (dict of (pid,vec) ) -
		   spatial position of points
		 - `dt` (float) - time step
		"""
		scax,scay,scaz = (1. + v * dt for v in self._scaling)
		for pid,vec in pos.iteritems() :
			vec.x *= scax
			vec.y *= scay
			vec.z *= scaz

class Radial (object) :
	"""Defines a radial growth
	"""
	def __init__ (self, center, speed_rate) :
		"""Constructor
		
		Initialize the algorithm.
		
		Parameters:
		 - `center` (Vector) - position
		  of the center (point that stay
		  fixed)
		 - `speed_rate` (float) - rate of
		  speed in m.m-1.s-1
		"""
		self._center = center
		self._speed_rate = speed_rate
	
	def grow (self, pos, dt) :
		"""Apply growth to a set of vectors
		
		Modify positions in place
		
		:Parameters:
		 - `pos` (dict of (pid,vec) ) -
		   spatial position of points
		 - `dt` (float) - time step
		"""
		center = self._center
		rate = self._speed_rate * dt
		for pid,vec in pos.iteritems() :
			pos[pid] = vec * (1. + norm(vec - center) * rate)

class Linear (object) :
	"""Defines growth along a given axis
	"""
	def __init__ (self, displacement_func, axis, center) :
		"""Constructor
		
		Initialize the algorithm.
		
		:Parameters:
		 - `displacement_func` (function) -
		    function setting the speed of
		    displacement for a given absciss
		 - `axis` (Vector) - oriented axis 
		    of growth
		 - `center` (Vector) - origin
		"""
		self._disp_func = displacement_func
		self._axis = axis / norm(axis)
		self._center = center
	
	def grow (self, pos, dt) :
		"""Apply growth to a set of vectors
		
		Modify positions in place
		
		:Parameters:
		 - `pos` (dict of (pid,vec) ) -
		   spatial position of points
		 - `dt` (float) - time step
		"""
		f = self._disp_func
		axis = self._axis
		center = self._center
		for pid,vec in pos.iteritems() :
			disp = f( (vec - center) * axis) * dt
			pos[pid] = vec + axis * disp

class Unconstrained (object) :
	"""Defines an unconstrained growth
	"""
	def __init__ (self, mesh, root, growth_speed) :
		"""constructor
		
		Initialize the algorithm
		
		.. warning:: the mesh must be linear (i.e.
		  without loops) of degree 2 (points and edges
		  only)
		
		:Paremeters:
		 - `mesh` (Topomesh) - topological structure
		   of the tissue
		 - `root` (pid) - point that will be fixed
		   throughout time
		 - `growth_speed` (dict of (int,float) ) -
		   rate of growth for each cell (edge of
		   the mesh) in (m.m-1.s-1)
		"""
		self._mesh = mesh
		self._root = root
		self._growth_speed = growth_speed
	
	def grow (self, pos, dt) :
		"""Apply growth to a set of vectors
		
		Modify positions in place
		
		:Parameters:
		 - `pos` (dict of (pid,vec) ) -
		   spatial position of points
		 - `dt` (float) - time step
		"""
		mesh = self._mesh
		gs = self._growth_speed
		front = [self._root]
		unvisited = set(mesh.wisps(1) )
		old_pos = dict( (pid,copy(vec) ) \
		  for pid,vec in pos.iteritems() )
		
		while len(front) > 0 :
			#retrieve current point
			pid = front.pop(0)
			
			#grow neighbor edges
			for eid in set(mesh.regions(0,pid) ) & unvisited :
				unvisited.discard(eid)
				opid, = set(mesh.borders(1,eid) ) - set([pid])
				front.append(opid)
				pos[opid] = pos[pid] \
				         + (old_pos[opid] - old_pos[pid]) \
				         * exp(gs[eid] * dt)


