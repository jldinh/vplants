from openalea.mechanics import LinearSpring2D,LinearSpring3D,\
                               TriangleMembrane3D,PolygonMembrane3D
from _cmechanics import CLinearSpring2D,CLinearSpring3D,\
						CTriangleMembrane3D,\
						CForwardEuler2D,CForwardEuler3D,\
						CForwardMarching2D,CForwardMarching3D

class MSSolver (object) :
	"""interface for mass spring solvers integrator in C
	"""
	
	SolverType = None #subclass
	
	def __init__ (self, point_weight, spring_list, external_constraint, logout = None) :
		"""Constructor
		
		Initialise integrator.
		
		:Parameters:
		 - `point_weight` (dict of (pid|float) ) - actual mass of points
		 - `spring_list` (list of :class:`Spring`) - elastic interactions
		                                           between points
		 - `external_constraint` (function) - boundary function taking
		                                      this solver as argument
		"""
		self._solver = self.SolverType()
		
		self._trans = {}
		self.create_particules(point_weight)
		
		self._cspring_list = []
		self.create_springs(spring_list)
		
		self._boundary = external_constraint
	
	#############################################
	#
	#	internal constructors
	#
	#############################################
	def create_particules (self, point_weight) :
		s = self._solver
		trans = self._trans
		for pid,w in point_weight.iteritems() :
			ind = s.add_particule()
			s.set_weight(ind,w)
			trans[pid] = ind
	
	def create_springs (self, spring_list) :
		raise NotImplementedError
	
	def _external_constraint (self) :
		self._boundary(self)
	
	#############################################
	#
	#	accessors
	#
	#############################################
	def position (self, pid) :
		"""Retrieve position of a given point
		
		:Parameters:
		 - `pid` (pid) - id of the point
		
		:Returns Type: Vector
		"""
		return self._solver.position(self._trans[pid])
	
	def set_position (self, pid, vec) :
		"""Set the position of a given point
		
		:Parameters:
		 - `pid` (pid) - id of the point
		 - `vec` (Vector) - new geometrical position
		                    of the point
		"""
		self._solver.set_position(self._trans[pid],vec)
	
	def force (self, pid) :
		"""Retrieve the force applied on a point
		
		:Parameters:
		 - `pid` (pid) - id of the point
		
		:Returns Type: Vector
		"""
		return self._solver.force(self._trans[pid])
	
	def set_force (self, pid, F) :
		"""Apply a force on a given point
		
		:Parameters:
		 - `pid` (pid) - id of the point
		 - `F` (Vector) - new force applied
		                  on the point
		"""
		self._solver.set_force(self._trans[pid],F)
	
	########################################
	#
	#		compute deformation
	#
	########################################
	def compute_forces (self) :
		"""Compute forces acting on points
		
		Use positions stored with :func:`set_position`
		"""
		s = self._solver
		s.set_boundary_function(self._external_constraint)
		s.compute_forces()
		s.set_boundary_function(None)
	
	def update_positions (self, dt) :
		"""Apply forces on point to physically move them
		
		raise :class:`DivergenceError` if a point goes
		to far away
		
		Use positions stored with :func:`set_position`
		and forces computed with :func:`compute_forces`
		"""
		self._solver.update_positions(dt)
	
	def force_max (self) :
		"""Return the biggest force applied in the system
		
		:Returns Type: float
		"""
		return self._solver.force_max()
	
	def deform (self, dt) :
		"""Compute deformation of the system
		
		actually call compute_forces then
		update_positions.
		
		:Parameters:
		 - `dt` (float) - time step
		
		:Return: None, modify positions
		         stored inside the algorithm
		"""
		s = self._solver
		s.set_boundary_function(self._external_constraint)
		new_dt = s.deform(dt)
		s.set_boundary_function(None)
		return new_dt
	
	def deform_to_equilibrium (self, dt, force_threshold) :
		"""Compute equilibrium positions of the system
		
		While forces are bigger than a given threshold,
		call :func:`MSSolver.deform`
		
		:Parameters:
		 - `pos` (dict of (pid|Vector) ) - geometrical
		         position of points in space
		 - `dt` (float) - time step
		 - `force_threshold` (float) - small force below
		                  which the system is considered
		                  to be in equilibrium
		 - `logout` (stream) - an output file like
		        used to write infos during computation
		"""
		s = self._solver
		s.set_boundary_function(self._external_constraint)
		s.deform_to_equilibrium(dt,force_threshold)
		s.set_boundary_function(None)


class MSSolver2D (MSSolver) :
	"""interface for 2D mass spring solvers integrator in C
	"""
	
	def create_springs (self, spring_list) :
		s = self._solver
		trans = self._trans
		cspring_list = self._cspring_list
		for spring in spring_list :
			if isinstance(spring,LinearSpring2D) :
				tpid0,tpid1 = (trans[pid] for pid in spring.extremities() )
				sp = CLinearSpring2D(tpid0,
				                     tpid1,
				                     spring.stiffness(),
				                     spring.ref_length() )
			else :
				raise UserWarning("unrecognized spring")
			#add spring to solver
			s.add_spring(sp)
			cspring_list.append(sp)

def create_triangle_spring (spring, trans) :
	tpid0,tpid1,tpid2 = (trans[pid] for pid in spring.extremities() )
	r1,r2,s2 = spring._ref_coords
	th = spring.thickness()
	sp = CTriangleMembrane3D(tpid0,tpid1,tpid2,r1,r2,s2,th)
	sp.set_material(tuple(spring._local_mat.flatten() ) )
	return sp

class MSSolver3D (MSSolver) :
	"""interface for 3D mass spring solvers integrator in C
	"""
	
	def create_springs (self, spring_list) :
		s = self._solver
		trans = self._trans
		cspring_list = self._cspring_list
		for spring in spring_list :
			if isinstance(spring,LinearSpring3D) :
				tpid0,tpid1 = (trans[pid] for pid in spring.extremities() )
				sp = CLinearSpring3D(tpid0,
				                     tpid1,
				                     spring.stiffness(),
				                     spring.ref_length() )
				#add spring to solver
				s.add_spring(sp)
				cspring_list.append(sp)
			elif isinstance(spring,TriangleMembrane3D) :
				sp = create_triangle_spring(spring,trans)
				#add spring to solver
				s.add_spring(sp)
				cspring_list.append(sp)
			elif isinstance(spring,PolygonMembrane3D) :
				for sub_spring in spring._sub_triangles :
					sp = create_triangle_spring(sub_spring,trans)
					#add spring to solver
					s.add_spring(sp)
					cspring_list.append(sp)
			else :
				raise UserWarning("unrecognized spring")

class ForwardEuler2D (MSSolver2D) :
	SolverType = CForwardEuler2D

class ForwardEuler3D (MSSolver3D) :
	SolverType = CForwardEuler3D

class ForwardMarching2D (MSSolver2D) :
	SolverType = CForwardMarching2D

class ForwardMarching3D (MSSolver3D) :
	SolverType = CForwardMarching3D


