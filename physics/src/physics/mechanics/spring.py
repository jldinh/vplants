# -*- python -*-
# -*- coding: latin-1 -*-
#
#       MassSpring : physics package
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

__doc__="""
This module provide an interface for deformation of spring systems
"""

__license__= "Cecill-C"
__revision__=" $Id: spring.py 7882 2010-02-08 18:36:38Z cokelaer $ "

from math import atan2,pi
from openalea.plantgl.math import Vector2,Vector3,norm

class Spring (object) :
	"""Interface for all spring objects.
	
	defines a unique mandatory method : assign_forces
	"""
	def strain (self, pos) :
		"""Compute actual strain of the spring.
		"""
		raise NotImplementedError
	
	def stress (self, pos) :
		"""Compute actual stress of the spring.
		"""
		raise NotImplementedError
	
	def energy (self, pos) :
		"""Compute the elastic energy stored in the spring.
		"""
		raise NotImplementedError
	
	def assign_forces (self, forces, pos) :
		"""Compute local forces and insert them into forces.
		
		compute local forces according to current positions.
		forces: a dict of (pid|Vector)
		pos: a dict of (pid|Vector)
		"""
		raise NotImplementedError

class LinearSpring (Spring) :
	"""Classical linear spring.
	"""
	def __init__ (self, pid1, pid2, stiffness, ref_length) :
		"""Initilise spring parameters.
		
		pid1: id of point
		pid2: id of point
		stiffness: float
		ref_length: float
		"""
		self._pid1 = pid1
		self._pid2 = pid2
		self._stiffness = stiffness
		self._ref_length = ref_length
	
	def length (self, pos) :
		"""Compute actual length of the spring.
		
		return: float
		"""
		return norm(pos[self._pid2] - pos[self._pid1])
	
	def strain (self, pos) :
		"""Compute actual strain of the spring.
		
		return float
		"""
		return (self.length(pos) - self._ref_length) / self._ref_length
	
	def stress (self, pos) :
		"""compute actual stress of the spring.
		"""
		return self.strain(pos) * self._stiffness
	
	def assign_forces (self, forces, pos) :
		#compute force
		fdir = pos[self._pid2] - pos[self._pid1]
		fdir.normalize()
		force = fdir * self.stress(pos)
		#assign force
		forces[self._pid1] += force
		forces[self._pid2] -= force

class LinearSpring2D (LinearSpring) :
	pass

class LinearSpring3D (LinearSpring) :
	pass

class CircularSpring2D (Spring) :
	"""Add an angular constraint betwwen two linked segments.
	
	Apply a force on each extremity of the segments
	that tend to maintain a given angle between them
	"""
	def __init__ (self, central_pid, pid1, pid2, stiffness, ref_angle) :
		"""Initialise spring parameters.
		
		central_pid: id of common point
		pid1: id of point
		pid2: id of point
		stiffness: float
		ref_angle: float (radians)
		"""
		self._central_pid = central_pid
		self._pid1 = pid1
		self._pid2 = pid2
		self._stifness = stiffness
		self._ref_angle = ref_angle
	
	def angle (self, pos) :
		"""Compute actual angle between the 2 segments.
		"""
		v1 = pos[self._pid1] - pos[self._central_pid]
		v2 = pos[self._pid2] - pos[self._central_pid]
		return atan2(v1 ^ v2,v1 * v2)
	
	def strain (self, pos) :
		"""Compute actual strain.
		"""
		delta_angle=self.angle(pos) - self._ref_angle
		if delta_angle > pi :
			delta_angle -= 2 * pi
		elif delta_angle < -pi :
			delta_angle += 2 * pi
		return delta_angle
	
	def stress (self, pos) :
		"""Compute actual stress
		"""
		return self.strain(pos) * self._stfifness
	
	def assign_forces (self, forces, pos) :
		#compute tork
		v1 = pos[self._pid1] - pos[self._central_pid]
		v2 = pos[self._pid2] - pos[self._central_pid]
		tork = self.stress(pos)
		#compute resultant forces
		f1 = Vector2(-v1.y * tork,v1.x * tork)
		f2 = Vector2(v2.y * tork,-v2.x * tork)
		#assign forces
		forces[self._pid1] += f1
		forces[self._pid2] += f2
		forces[self._central_pid] -= (f1 + f2)

class VolumetricSpring (Spring) :
	"""Add a volumetric constraint.
	
	Compute forces toward barycenter of a shape
	that tend to maintain a given volume
	"""
	def __init__ (self, polyhedra, stiffness, ref_volume) :
		"""Initialise spring.
		
		polyhedra: Polyhedra
		stiffness: float
		ref_volume: float
		"""
		self._polyhedra = polyhedra
		self._stiffness = stiffness
		self._ref_volume = ref_volume
	
	def volume (self, pos) :
		"""Compute actual volume of the polyhedra.
		"""
		return self._polyhedra.volume(pos)
	
	def strain (self, pos) :
		"""Compute actual strain of the spring.
		"""
		return (self.volume(pos) - self._ref_volume) / self._ref_volume
	
	def stress (self, pos) :
		"""Compute actual stress of the spring.
		"""
		return self.strain(pos) * self.stiffness
	
	def assign_forces (self, forces, pos) :
		force = self.stress(pos)
		cent = self._polyhedra.centroid(pos)
		for pid in self._polyhedra :
			fdir = cent - pos[pid]
			fdir.normalize()
			forces[pid] += fdir * force_norm

class VolumetricSpring2D (VolumetricSpring) :
	pass

class VolumetricSpring3D (VolumetricSpring) :
	pass

