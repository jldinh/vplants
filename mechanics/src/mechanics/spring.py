# -*- python -*-
# -*- coding: latin-1 -*-
#
#       spring : mechanics package
#
#       Copyright or ? or Copr. 2006 INRIA - CIRAD - INRA  
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
This module provide an interface for deformation of spring systems
"""

__license__= "Cecill-C"
__revision__=" $Id: spring.py 9193 2010-06-26 07:09:19Z chopard $ "

from math import atan2,pi,log
from numpy import array
from numpy.linalg import norm

from actor import MechanicalActor

class Spring (MechanicalActor) :
	"""Interface for all spring objects
	
	On top of the assign_forces defined by MechanicalActor, this class
	defines these mandatory methods:
	
	 - :func:`strain`
	 - :func:`stress`
	 - :func:`energy`
	"""
	def strain (self, state, t = None) :
		"""Compute actual strain of the spring
		
		:Parameters:
		 - `state` (array of float) - current position and velocity of points
		 - `t` (float) - current time
		
		:Returns Type: UnDef
		"""
		raise NotImplementedError
	
	def stress (self, state, t = None) :
		"""Compute actual stress of the spring
		
		:Parameters:
		 - `state` (array of float) - current position and velocity of points
		 - `t` (float) - current time
		
		:Returns Type: UnDef
		"""
		raise NotImplementedError
	
	def energy (self, state, t = None) :
		"""Compute the elastic energy stored in the spring
		
		:Parameters:
		 - `state` (array of float) - current position and velocity of points
		 - `t` (float) - current time
		
		:Returns Type: float
		"""
		raise NotImplementedError
	
	def assign_forces (self, forces, state, t = None) :
		"""Compute local forces and insert them into forces
		
		Compute local forces generated by this actor
		according to current state.
		
		:Parameters:
		 - `forces` (array of float) - an array that store force vectors
		 - `state` (array of float) - current position and velocity of points
		 - `t` (float) - current time
		
		:Returns: None, modify forces in place
		"""
		raise NotImplementedError
	
	def assign_jacobian (self, jacobian, state, t = None) :
		"""Compute jacobian contribution of this actor
		
		:Parameters:
		 - `jacobian` (array of float) - an array that store jacobian
		 - `state` (array of float) - current position and velocity of points
		 - `t` (float) - current time
		
		:Returns: None, modify jacobian in place
		"""
		raise NotImplementedError
	
	##########################################
	#
	#		scipy integrator interface
	#
	##########################################
	def scipy_energy (self, t, state) :
		"""Compute the elastic energy stored in the spring
		
		:Parameters:
		 - `t` (float) - current time
		 - `state` (array of float) - current position and velocity of points
		
		:Returns Type: float
		"""
		raise NotImplementedError
	
	def scipy_forces (self, t, state, forces) :
		"""Compute local forces and insert them into forces
		
		Compute local forces generated by this spring
		according to current state.
		
		:Parameters:
		 - `t` (float) - current time
		 - `state` (array of float) - current position and velocity of points
		 - `forces` (array of float) - an array that store force vectors
		
		:Returns: None, modify forces in place
		"""
		raise NotImplementedError

class LinearSpring (Spring) :
	"""Classical linear spring.
	"""
	def __init__ (self, pid1, pid2, stiffness, ref_length, section) :
		"""Constructor
		
		Initialise spring parameters.
		
		:Parameters:
		 - `pid1` (pid) - id of first extremity
		 - `pid2` (pid) - id of second extremity
		 - `stiffness` (float) - stiffness of the spring
		 - `ref_length` (float) - reference length
		 - `section` (float) - surface of a section of the spring
		"""
		self._pid1 = pid1
		self._pid2 = pid2
		self._stiffness = stiffness
		self._ref_length = ref_length
		self._section = section
	
	##########################################
	#
	#		accessors
	#
	##########################################
	def extremities (self) :
		"""Iterator on both extremities
		
		:Returns Type: iter of pid
		"""
		yield self._pid1
		yield self._pid2
	
	def set_extremities (self, pid1, pid2) :
		"""Set extremal points
		
		:Parameters:
		 - `pid1` (pid) - id of first extremity
		 - `pid2` (pid) - id of second extremity
		"""
		self._pid1 = pid1
		self._pid2 = pid2
	
	def stiffness (self) :
		"""Retrieve stiffness (K) of the spring
		
		unit: N.m-2 or Pa
		
		:Returns Type: float
		"""
		return self._stiffness
	
	def set_stiffness (self, stiffness) :
		"""Set the stiffness of the spring
		
		:Parameters:
		 - `stiffness` (float) - stiffness rate per unit of length
		"""
		self._stiffness = stiffness
	
	def ref_length (self) :
		"""Retrieve the reference length of this spring
		
		:Returns Type: float
		"""
		return self._ref_length
	
	def set_ref_length (self, length) :
		"""Set the reference (or rest) length
		
		:Parameters:
		 - `length` (float)
		"""
		self._ref_length = length
	
	def section (self) :
		"""Retrieve the section of this spring
		
		:Returns Type: float
		"""
		return self._section
	
	def set_section (self, section) :
		"""Set the section of this spring
		
		:Parameters:
		 - `section` (float)
		"""
		self._section = section
	
	##########################################
	#
	#		mechanics computations
	#
	##########################################
	def length (self, state, t = None) :
		"""Compute actual length of the spring
		
		:Parameters:
		 - `state` (array of float) - current position and velocity of points
		 - `t` (float) - current time
		
		:Returns Type: float
		"""
		return norm(state[0,self._pid2,:] - state[0,self._pid1,:])
	
	def strain (self, state, t = None) :
		"""Compute actual strain of the spring
		
		:Parameters:
		 - `state` (array of float) - current position and velocity of points
		 - `t` (float) - current time
		
		:Returns Type: float
		"""
		#return (self.length(state,t) - self._ref_length) / self._ref_length
		return log(self.length(state,t) ) - log(self._ref_length)
	
	def stress (self, state, t = None) :
		"""compute actual stress of the spring
		
		:Parameters:
		 - `state` (array of float) - current position and velocity of points
		 - `t` (float) - current time
		
		:Returns Type: float
		"""
		return self.strain(state,t) * self._stiffness
	
	def energy (self, state, t = None) :
		"""Compute the elastic energy stored in the spring
		
		:Parameters:
		 - `state` (array of float) - current position and velocity of points
		 - `t` (float) - current time
		
		:Returns Type: float
		"""
		return self.strain(state,t) * self.stress(state,t) \
		     * self._ref_length * self._section
	
	def assign_forces (self, forces, state, t = None) :
		"""Compute local forces and insert them into forces
		
		Compute local forces generated by this actor
		according to current state.
		
		:Parameters:
		 - `forces` (array of float) - an array that store force vectors
		 - `state` (array of float) - current position and velocity of points
		 - `t` (float) - current time
		
		:Returns: None, modify forces in place
		"""
		#compute force
		fdir = state[0,self._pid2,:] - state[0,self._pid1,:]
		
		force = fdir * (self.stress(state,t) * self._section / norm(fdir) )
		
		#assign force
		forces[self._pid1,:] += force
		forces[self._pid2,:] -= force
	
	def assign_jacobian (self, jacobian, state, t = None) :
		"""Compute jacobian contribution of this actor
		
		:Parameters:
		 - `jacobian` (array of float) - an array that store jacobian
		 - `state` (array of float) - current position and velocity of points
		 - `t` (float) - current time
		
		:Returns: None, modify jacobian in place
		"""
		Fdir = state[0,self._pid2] - state[0,self._pid1]
		l = norm(Fdir)
		
		alpha = self._stiffness * self._section / l
		ll = log(l) - log(self._ref_length)
		
		pid1 = self._pid1
		pid2 = self._pid2
		dim = len(Fdir)
		for fi in range(dim) :
			for i in range(dim) :
				v = alpha * (Fdir[fi] * Fdir[i] / l**2  * (1 - ll) \
				           + (fi == i) * ll)
				jacobian[1,pid1,fi,0,pid1,i] += v
				jacobian[1,pid1,fi,0,pid2,i] -= v
				jacobian[1,pid2,fi,0,pid1,i] -= v
				jacobian[1,pid2,fi,0,pid2,i] += v


class LinearSpring2D (LinearSpring) :
	pass


class LinearSpring3D (LinearSpring) :
	pass


class CircularSpring2D (Spring) :
	"""Add an angular constraint between two linked segments
	
	Apply a force on each extremity of the segments
	that tend to maintain a given angle between them.
	"""
	def __init__ (self, central_pid, pid1, pid2, stiffness, ref_angle) :
		"""Constructor
		
		Initialise spring parameters.
		
		:Parameters:
		 - `central_pid` (pid) - id of common point
		 - `pid1` (pid) - id of first point
		 - `pid2` (pid) - id of second point
		 - `stiffness` (float) - stiffness of the spring
		 - `ref_angle` (float) - reference angle in radians
		"""
		raise NotImplementedError ("#TODO")
		self._central_pid = central_pid
		self._pid1 = pid1
		self._pid2 = pid2
		self._stifness = stiffness
		self._ref_angle = ref_angle
	
	def angle (self, pos) :
		"""Compute actual angle between the 2 segments
		
		:Parameters:
		 - `pos` (dict of (pid|Vector) ) - geometrical
		         position of points in space
		
		:Returns Type: float
		"""
		v1 = pos[self._pid1] - pos[self._central_pid]
		v2 = pos[self._pid2] - pos[self._central_pid]
		return atan2(v1 ^ v2,v1 * v2)
	
	def strain (self, pos) :
		"""Compute actual strain
		
		:Parameters:
		 - `pos` (dict of (pid|Vector) ) - geometrical
		         position of points in space
		
		:Returns Type: float
		"""
		delta_angle=self.angle(pos) - self._ref_angle
		if delta_angle > pi :
			delta_angle -= 2 * pi
		elif delta_angle < -pi :
			delta_angle += 2 * pi
		return delta_angle
	
	def stress (self, pos) :
		"""Compute actual stress
		
		:Parameters:
		 - `pos` (dict of (pid|Vector) ) - geometrical
		         position of points in space
		
		:Returns Type: float
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
	
	assign_forces.__doc__ = Spring.assign_forces.__doc__


class VolumetricSpring (Spring) :
	"""Add a volumetric constraint
	
	Compute forces toward barycenter of a shape
	that tend to maintain a given volume.
	"""
	def __init__ (self, polyhedra, stiffness, ref_volume) :
		"""Constructor
		
		Initialise spring.
		
		polyhedra: Polyhedra
		stiffness: float
		ref_volume: float
		"""
		raise NotImplementedError ("#TODO")
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
	
	assign_forces.__doc__ = Spring.assign_forces.__doc__


class VolumetricSpring2D (VolumetricSpring) :
	pass


class VolumetricSpring3D (VolumetricSpring) :
	pass


class Beam (Spring) :
	"""Beam wih rotational energy
	"""
	def __init__ (self, pid1, pid2, stiffness, ref_dir) :
		"""Constructor
		
		Initialise spring parameters.
		
		:Parameters:
		 - `pid1` (pid) - id of first extremity
		 - `pid2` (pid) - id of second extremity
		 - `stiffness` (float) - stiffness of the spring
		 - `ref_dir` (Vector) - reference direction
		"""
		raise NotImplementedError ("#TODO")
		self._pid1 = pid1
		self._pid2 = pid2
		self._stiffness = stiffness
		self._ref_dir = ref_dir
	
	##########################################
	#
	#		accessors
	#
	##########################################
	def extremities (self) :
		"""Iterator on both extremities
		
		:Returns Type: iter of pid
		"""
		yield self._pid1
		yield self._pid2
	
	def set_extremities (self, pid1, pid2) :
		"""Set extremal points
		
		:Parameters:
		 - `pid1` (pid) - id of first extremity
		 - `pid2` (pid) - id of second extremity
		"""
		self._pid1 = pid1
		self._pid2 = pid2
	
	def stiffness (self) :
		"""Retrieve stiffness (K) of the spring
		
		:Returns Type: float
		"""
		return self._stiffness
	
	def set_stiffness (self, stiffness) :
		"""Set the stiffness of the spring
		
		:Parameters:
		 - `stiffness` (float) - stiffness rate
		                     per unit of length
		"""
		self._stiffness = stiffness
	
	def ref_dir (self) :
		"""Retrieve the reference direction of this beam
		
		:Returns Type: Vector
		"""
		return self._ref_dir
	
	def set_ref_dir (self, vec) :
		"""Set the reference direction of this beam
		
		:Parameters:
		 - vec (Vector)
		"""
		self._ref_dir = vec / norm(vec)
	
	##########################################
	#
	#		mechanics computations
	#
	##########################################
	def length (self, pos) :
		"""Compute actual length of the beam
		
		:Parameters:
		 - `pos` (dict of (pid|Vector) ) - geometrical
		         position of points in space
		
		:Returns Type: float
		"""
		return norm(pos[self._pid2] - pos[self._pid1])
	
	def strain (self, pos) :
		"""Compute actual strain of the spring
		
		:Parameters:
		 - `pos` (dict of (pid|Vector) ) - geometrical
		         position of points in space
		
		:Returns Type: float
		"""
		#return (self.length(pos) - self._ref_length) / self._ref_length
		return log(self.length(pos) ) - log(self._ref_length)
	
	def stress (self, pos) :
		"""compute actual stress of the spring
		
		:Parameters:
		 - `pos` (dict of (pid|Vector) ) - geometrical
		         position of points in space
		
		:Returns Type: float
		"""
		return self.strain(pos) * self._stiffness
	
	def assign_forces (self, forces, pos) :
		#compute force
		beam_dir = pos[self._pid2] - pos[self._pid1]
		l = beam_dir.normalize()
		
		#assign angular forces
		fdir = beam_dir - self._ref_dir
		force = fdir * (l * self._stiffness) / 2.
		
		forces[self._pid1] += force
		forces[self._pid2] -= force
	
	assign_forces.__doc__ = Spring.assign_forces.__doc__


class Beam2D (Beam) :
	pass


class Beam3D (Beam) :
	pass


