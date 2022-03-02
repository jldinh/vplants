# -*- python -*-
# -*- coding: latin-1 -*-
#
#       MassSpring : mechanics package
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

__doc__ = """
This module provide an interface for deformation of spring systems
"""

__license__= "Cecill-C"
__revision__=" $Id: mass_spring_solver.py 9030 2010-06-01 09:00:10Z chopard $ "

from numpy import array,zeros
from numpy.linalg import norm

LARGE = 1e9

class DivergenceError (Exception) :
	"""Error raised if an algorithm do not converge
	"""
	pass

class MSSolver (object) :
	"""Integration method for mass spring systems
	
	basic implementation of mass spring resolution using a forward Euler method.
	"""
	
	dim = None
	"""dimension of space
	"""
	
	def __init__ (self, particules, actor_list, external_constraint,
	                    logout = None) :
		"""Constructor
		
		Initialise integrator.
		
		:Parameters:
		 - `particles` (dict of (pid|Particule) ) - set of particules
		    that will be connected by springs
		 - `actor_list` (list of :class:`Actor`) - interactions between points
		                         (springs, dampers, ...)
		 - `external_constraint` (function) - boundary function taking
		                                      this solver as argument
		 - `logout` (outstream) - an outfile stream like structure
		                          used to write some debug informations.
		                          If None, no output messages are printed
		"""
		self._particules = particules
		self._actor_list = actor_list
		self._external_constraint = external_constraint
		self._force = {}
		self.logout = logout
	
	########################################
	#
	#		accessors
	#
	########################################
	def position (self, pid) :
		"""Retrieve position of a given point
		
		:Parameters:
		 - `pid` (pid) - id of the point
		
		:Returns Type: Vector
		"""
		return self._particules[pid].position()
	
	def set_position (self, pid, vec) :
		"""Set the position of a given point
		
		:Parameters:
		 - `pid` (pid) - id of the point
		 - `vec` (Vector) - new geometrical position of the point
		"""
		self._particules[pid].set_position(array(vec) )
	
	def force (self, pid) :
		"""Retrieve the force applied on a point
		
		:Parameters:
		 - `pid` (pid) - id of the point
		
		:Returns Type: Vector
		"""
		return self._force[pid]
	
	def set_force (self, pid, F) :
		"""Apply a force on a given point
		
		:Parameters:
		 - `pid` (pid) - id of the point
		 - `F` (Vector) - new force applied on the point
		"""
		self._force[pid] = array(F)
	
	def force_max (self) :
		"""Return the biggest force applied in the system
		
		Use forces computed with :func:`compute_force`
		
		:Returns Type: float
		"""
		return max(norm(F) for F in self._force.itervalues() )
	
	def speed_max (self) :
		"""Return the speed of the fastest point in the system
		
		.. warning:: Uses velocities computed during the last time step
		             and stored into particules
		
		:Returns Type: float
		"""
		return max(norm(p.velocity() ) for p in self.particules.itervalues() )
	
	########################################
	#
	#		compute deformation
	#
	########################################
	def compute_forces (self) :
		"""Compute forces acting on points
		
		Use previously stored positions
		
		:Returns: None, modify forces stored inside the algo struct.
		"""
		#compute forces
		for pid in self._particules :
			self._force[pid] = zeros(self.dim)
		for actor in self._actor_list :
			actor.assign_forces(self._force,self._particules)
		
		#external constraints
		self._external_constraint(self)
	
	def deform (self, dt) :
		"""Compute deformation of the system
		
		Modify particules parameters internally
		
		:Parameters:
		 - `dt` (float) - time step hint
		
		:Returns: the actual dt used for computation
		
		:Returns Type: float
		"""
		raise NotImplementedError
	
	def deform_to_equilibrium (self, dt, force_threshold) :
		"""Compute equilibrium positions of the system
		
		While forces are bigger than a given threshold, call :func:`deform`
		
		:Parameters:
		 - `dt` (float) - time step
		 - `force_threshold` (float) - small force below which the system is
		                               considered to be in equilibrium
		"""
		Fmax = 2 * force_threshold
		while Fmax > force_threshold :
			dt = self.deform(dt)
			Fmax = self.force_max()
			if self.logout is not None :
				self.logout.write("Fmax: %e\n" % Fmax)
				self.logout.flush()


########################################################################
#
#	static solver used to compute forces
#
########################################################################
class StaticSolver2D (MSSolver) :
	"""Compute force generated by a set of actors for a given configuration
	"""
	dim = 2

class StaticSolver3D (MSSolver) :
	"""Compute force generated by a set of actors for a given configuration
	"""
	dim = 3
########################################################################
#
#	simple forward euler
#
########################################################################
class ForwardEuler (MSSolver) :
	"""Compute evolution using a simple Euler integration scheme
	"""
	
	def deform (self, dt) :
		"""Compute deformation of the system
		
		actually call compute_forces then update internally stored particules
		
		:Parameters:
		 - `dt` (float) - time step
		
		:Return: the actual dt used for computation
		
		:Returns Type: float
		"""
		#compute forces
		self.compute_forces()
		
		#compute new positions
		force = self._force
		
		for pid,p in self._particules.iteritems() :
			velocity = p.velocity() + force[pid] * (dt / p.weight() )
			pos = p.position() + velocity * dt
			
			p.set_velocity(velocity)
			p.set_position(pos)
		
		#return
		return dt# * self._nb_steps


class ForwardEuler2D (ForwardEuler) :
	dim = 2


class ForwardEuler3D (ForwardEuler) :
	dim = 3

########################################################################
#
#	Runge et Kuta order 4
#
########################################################################
class RungeKutta (MSSolver) :
	"""Compute equilibrium using a Runge et Kutta integration scheme.
	"""
	
	def deform (self, dt) :
		"""Deform positions using RG4 scheme.
		
		.. seealso:: `http://en.wikipedia.org/wiki/Runge%E2%80%93Kutta_methods`
		
		0   |
		1/2 | 1/2
		1/2 | 0   1/2
		1   | 0   0   1
		---------------------
		    | 1/6 1/3 1/3 1/6
		"""
		pts = self._particules
		
		#init
		x0 = dict( (pid,p.position() ) for pid,p in pts.iteritems() )
		v0 = dict( (pid,p.velocity() ) for pid,p in pts.iteritems() )
		
		#K1
		self.compute_forces()
		dx1 = dict( (pid,vec * dt) \
		             for pid,vec in v0.iteritems() )
		dv1 = dict( (pid,vec * (dt / pts[pid].weight() ) ) \
		             for pid,vec in self._force.iteritems() )
		
		#K2
		for pid,p in pts.iteritems() :
			p.set_position(x0[pid] + dx1[pid] / 2.)
			p.set_velocity(v0[pid] + dv1[pid] / 2.)
		self.compute_forces()
		dx2 = dict( (pid,(vec + dv1[pid] / 2.) * dt) \
		             for pid,vec in v0.iteritems() )
		dv2 = dict( (pid,vec * (dt / pts[pid].weight() ) ) \
		             for pid,vec in self._force.iteritems() )
		
		#K3
		for pid,p in pts.iteritems() :
			p.set_position(x0[pid] + dx2[pid] / 2.)
			p.set_velocity(v0[pid] + dv2[pid] / 2.)
		self.compute_forces()
		dx3 = dict( (pid,(vec + dv2[pid] / 2.) * dt) \
		             for pid,vec in v0.iteritems() )
		dv3 = dict( (pid,vec * (dt / pts[pid].weight() ) ) \
		             for pid,vec in self._force.iteritems() )
		
		#K4
		for pid,p in pts.iteritems() :
			p.set_position(x0[pid] + dx3[pid])
			p.set_velocity(v0[pid] + dv3[pid])
		self.compute_forces()
		dx4 = dict( (pid,(vec + dv3[pid]) * dt) \
		             for pid,vec in v0.iteritems() )
		dv4 = dict( (pid,vec * (dt / pts[pid].weight() ) ) \
		             for pid,vec in self._force.iteritems() )
		
		#compute new speed
		for pid,p in pts.iteritems() :
			p.set_velocity(v0[pid] + dv1[pid] / 6. \
			                       + dv2[pid] / 3. \
			                       + dv3[pid] / 3. \
			                       + dv4[pid] / 6.)
		
		#move points
		for pid,p in pts.iteritems() :
			p.set_position(x0[pid] + dx1[pid] / 6. \
			                       + dx2[pid] / 3. \
			                       + dx3[pid] / 3. \
			                       + dx4[pid] / 6.)
		
		#return
		return dt


class RungeKutta2D (RungeKutta) :
	dim = 2

class RungeKutta3D (RungeKutta) :
	dim = 3

########################################################################
#
#	Forward Marching
#
########################################################################
class ForwardMarching (MSSolver) :
	"""Compute equilibrium using a forward marching integration scheme.
	
	At each iteration, compare the forces obtained with the one
	on the previous dt. If force max is bigger, it means that the
	algorihtm will fail to converge and it will use a smaller dt
	"""
	def __init__ (self, point_weight, spring_list, external_constraint,
	                    logout = None) :
		"""Constructor
		
		Initialise integrator.
		
		:Parameters:
		 - `point_weight` (dict of (pid|float) ) - actual mass of points
		 - `spring_list` (list of :class:`Spring`) - elastic interactions
		                                           between points
		 - `external_constraint` (function) - boundary function taking
		                                      this solver as argument
		 - `logout` (outstream) - an outfile stream like structure
		                          used to write some debug informations.
		                          If None, no output messages are printed
		"""
		raise NotImplementedError("#TODO")
		MSSolver.__init__(self,
		                  point_weight,
		                  spring_list,
		                  external_constraint,
		                  logout)
		self._nb_good_iter = 0
	
	def safe_apply_forces (self, dt) :
		ref_pos = dict(self._pos)
		
		while True :
			try :
				self._pos.update(ref_pos)
				self.update_positions(dt)
				return dt
			except DivergenceError :
				dt = dt / 2.
				self._nb_good_iter = 0
				print "div error"
	
	def deform (self, dt) :
		"""Deform positions using ForwardMarching scheme.
		
		compare result with same computation with
		smaller dt
		"""
		pos_prev = dict(self._pos)
		
		Fmax_prev = self.force_max()
		
		if self._nb_good_iter > 10 :
			dt = dt * 1.9
			self._nb_good_iter = 0
			print "debug *2",dt
		
		dt = self.safe_apply_forces(dt)
		self.compute_forces()
		self._nb_good_iter += 1
		while self.force_max() > Fmax_prev :
			print "debug",dt,"%e" % (Fmax_prev - self.force_max())
			self._nb_good_iter = 0
			self._pos.update(pos_prev)
			dt = self.safe_apply_forces(dt / 2.)
			self.compute_forces()
		
		#return
		return dt
	
	def deform_to_equilibrium (self, dt, force_threshold) :
		"""Compute equilibrium positions of the system
		
		While forces are bigger than a given threshold,
		call :func:`deform`
		
		:Parameters:
		 - `dt` (float) - time step
		 - `force_threshold` (float) - small force below
		                  which the system is considered
		                  to be in equilibrium
		"""
		self.compute_forces()
		MSSolver.deform_to_equilibrium(self,dt,force_threshold)

class ForwardMarching2D (ForwardMarching) :
	dim = 2

class ForwardMarching3D (ForwardMarching) :
	dim = 3

