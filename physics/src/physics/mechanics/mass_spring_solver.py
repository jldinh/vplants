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
__revision__=" $Id: mass_spring_solver.py 7882 2010-02-08 18:36:38Z cokelaer $ "

from openalea.plantgl.math import Vector2,Vector3,norm

LARGE = 1e9

class DivergenceError (Exception) :
	pass

class MSSolver (object) :
	"""Integration method for mass spring systems.
	
	basic implementation of mass spring resolution
	using a forward Euler method
	"""
	
	Vector = None
	"""type of vector objects used.
	"""
	
	def __init__ (self, point_weight, spring_list, external_constraint) :
		"""Initialise integrator.
		
		point_weight: a dict of (pid|float)
		spring_list: a list of spring objects
		external_constraint: a function taking this solver as argument
		"""
		self._weight = point_weight
		self._spring_list = spring_list
		self._external_constraint = external_constraint
		self._pos = None
		self._force = None
	
	########################################
	#
	#		accessors
	#
	########################################
	def position (self, pid) :
		"""Retrieve position of a given point.
		
		pid: point id
		return: Vector
		"""
		return self._pos[pid]
	
	def set_position (self, pid, vec) :
		"""Set the position of a given point.
		
		pid: point id
		vec: Vector
		"""
		self._pos[pid] = vec
	
	def force (self, pid) :
		"""Retrieve the force applied on a point
		
		pid: point id
		return: Vector
		"""
		return self._force[pid]
	
	def set_force (self, pid, F) :
		"""Apply a force on a given point.
		
		pid: point id
		F: Vector
		"""
		self._force[pid] = F
	########################################
	#
	#		compute deformation
	#
	########################################
	def compute_forces (self, pos) :
		"""Compute forces acting on points.
		"""
		#compute forces
		force = dict( (pid,self.Vector()) for pid in pos )
		for spring in self._spring_list :
			spring.assign_forces(force,pos)
		
		#external constraints
		self._pos = pos
		self._force = force
		self._external_constraint(self)
		
		#return
		return force
	
	def update_positions (self, pos, force, dt) :
		#compute new positions
		weight = self._weight
		for pid,F in force.iteritems() :
			vec = pos[pid] + F * (dt / weight[pid])
			pos[pid] = vec
			for coord in vec :
				if coord > LARGE :
					raise DivergenceError
	
	def deform (self, pos, dt) :
		"""Compute deformation.
		"""
		#compute forces
		force = self.compute_forces(pos)
		#compute new positions
		self.update_positions(pos,force,dt)
		
		return pos,dt,force
	
	def force_max (self, forces) :
		"""Return biggest force applied on the system.
		"""
		return max(norm(F) for F in forces.itervalues())
	
	def deform_to_equilibrium (self, pos, dt, force_threshold) :
		"""Compute equilibrium positions of the system.
		
		while forces are bigger than a given threshold,
		call deform
		"""
		Fmax = 2 * force_threshold
		while Fmax > force_threshold :
			dt,forces = self.deform(pos,dt)
			Fmax = self.force_max(forces)
			print "Fmax",Fmax


########################################################################
#
#	simple forward euler
#
########################################################################
class ForwardEuler (MSSolver) :
	"""Compute equilibrium using a simple Euler integration scheme.
	
	call deform until forces drop below a given threshold
	"""
	def deform (self, pos, dt, nb_steps = 100) :
		"""Compute nb_steps of deformation.
		"""
		for i in xrange(nb_steps) :
			#compute forces
			force = self.compute_forces(pos)
			#compute new positions
			self.update_positions(pos,force,dt)
		
		return dt,force


class ForwardEuler2D (ForwardEuler) :
	Vector = Vector2


class ForwardEuler3D (ForwardEuler) :
	Vector = Vector3

########################################################################
#
#	Runge et Kuta order 4
#
########################################################################
class RungeKuta (MSSolver) :
	"""Compute equilibrium using a Runge et Kuta integration scheme.
	"""
	
	def deform (self, pos, dt) :
		"""Deform positions using RG4 scheme.
		
		call compute_force for 0, dt /2, dt /2 and dt
		"""
		#F1
		force1 = self.compute_forces(pos)
		#F2
		pos2 = dict( (pid,self.Vector(vec)) for pid,vec in pos.iteritems() )
		self.update_positions(pos2,force1,dt / 2.)
		force2 = self.compute_forces(pos2)
		#F3
		pos3 = dict( (pid,self.Vector(vec)) for pid,vec in pos.iteritems() )
		self.update_positions(pos3,force2,dt / 2.)
		force3 = self.compute_forces(pos3)
		#F4
		pos4 = dict( (pid,self.Vector(vec)) for pid,vec in pos.iteritems() )
		self.update_positions(pos3,force3,dt)
		force4 = self.compute_forces(pos4)
		#compute final displacement
		force = dict( (pid,(force1[pid] +
		                    force2[pid] * 2. + 
		                    force3[pid] * 2. + 
		                    force4[pid]) / 6.) for pid in pos )
		self.update_positions(pos,force,dt)
		#return
		return dt,force


class RungeKuta2D (RungeKuta) :
	Vector = Vector2

class RungeKuta3D (RungeKuta) :
	Vector = Vector3

########################################################################
#
#	Forward Marching
#
########################################################################
class ForwardMarching (MSSolver) :
	"""Compute equilibrium using a forward marching integration scheme.
	
	At each iteration, compare the displacement obtained
	with the given dt and a smaller dt
	adapt dt accordingly
	"""
	DT_MAX = 10.
	NB_SUBDI = 10
	ERR_MAX_THRESHOLD = 1e-4
	ERR_MIN_THRESHOLD = 1e-5
	
	def deform (self, pos, dt) :
		"""Deform positions using ForwardMarching scheme.
		
		compare result with same computation with
		smaller dt
		"""
		self._prev_err = -1
		self._nb_fine_iter = 0
		force = self.compute_forces(pos)
		return self._deform(pos,dt,force)
	
	def _deform (self, pos, dt, force) :
		"""Actually perform the deformation.
		"""
		force_ref = force
		try :
			#compute ref
			pos_ref = dict( (pid,self.Vector(vec)) for pid,vec in pos.iteritems() )
			self.update_positions(pos_ref,force,dt)
			
			#compute test
			dt_test = dt / self.NB_SUBDI
			pos_test = dict( (pid,self.Vector(vec)) for pid,vec in pos.iteritems() )
			self.update_positions(pos_test,force,dt_test)
			
			for i in xrange(self.NB_SUBDI - 1) :
				force = self.compute_forces(pos_test)
				self.update_positions(pos_test,force,dt_test)
		except DivergenceError :
			print "nan",dt
			return self._deform(pos,dt / 2,force_ref)
		
		#compare
		err = max(norm(pos_test[pid] - pos_ref[pid]) for pid in pos)
		print "                        err",err,self._prev_err,dt,self._nb_fine_iter
		if self._prev_err > 0 :
			if err > (self._prev_err * 1.4) and err > self.ERR_MIN_THRESHOLD :
				print "                        go back"
				self._nb_fine_iter = 0
				return self._deform(pos,dt / 1.5)
		if err > self.ERR_MAX_THRESHOLD :
			self._prev_err = -1
			self._nb_fine_iter = 0
			return self._deform(pos,dt / 2,force_ref)
		else :
			for pid,vec in pos_test.iteritems() :
				pos[pid] = vec
			if err < self.ERR_MIN_THRESHOLD and self._nb_fine_iter > 10 :
				self._prev_err = err
				self._nb_fine_iter = 0
				return min(self.DT_MAX,dt * 1.5),force
			else :
				self._prev_err = -1
				self._nb_fine_iter += 1
				return dt,force
		


class ForwardMarching2D (ForwardMarching) :
	Vector = Vector2

class ForwardMarching3D (ForwardMarching) :
	Vector = Vector3

