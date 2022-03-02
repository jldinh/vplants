from openalea.physics.mechanics import LinearSpring2D,LinearSpring3D,\
									TriangleMembrane3D
from _cphysics import CLinearSpring2D,CLinearSpring3D,\
						CTriangleMembrane3D,\
						CForwardEuler2D,CForwardEuler3D,\
						CForwardMarching2D,CForwardMarching3D

class MSSolver (object) :
	"""
	interface for forward euler integrator in C
	"""
	
	SolverType = None #subclass
	
	def __init__ (self, point_weight, spring_list, external_constraint) :
		self._solver = self.SolverType()
		
		self._trans = {}
		self.create_particules(point_weight)
		
		self._cspring_list = []
		self.create_springs(spring_list)
		
		self._boundary = external_constraint
	
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
	
	def deform (self, pos, dt) :
		s = self._solver
		trans = self._trans
		for pid,v in pos.iteritems() :
			s.set_position(trans[pid],v)
		s.set_boundary_function(self._external_constraint)
		s.deform(dt)
		s.set_boundary_function(None)
		for pid,vec in pos.iteritems() :
			pos[pid] = s.position(trans[pid])
	
	def deform_to_equilibrium (self, pos, dt, force_threshold) :
		s = self._solver
		trans = self._trans
		for pid,v in pos.iteritems() :
			s.set_position(trans[pid],v)
		s.set_boundary_function(self._external_constraint)
		s.deform_to_equilibrium(dt,force_threshold)
		s.set_boundary_function(None)
		for pid,vec in pos.iteritems() :
			pos[pid] = s.position(trans[pid])
	
	def position (self, pid) :
		return self._solver.position(self._trans[pid])
	
	def set_position (self, pid, vec) :
		self._solver.set_position(self._trans[pid],vec)
	
	def force (self, pid) :
		return self._solver.force(self._trans[pid])
	
	def set_force (self, pid, F) :
		self._solver.set_force(self._trans[pid],F)

class MSSolver2D (MSSolver) :
	"""
	interface for forward euler integrator in C
	"""
	
	def create_springs (self, spring_list) :
		s = self._solver
		trans = self._trans
		cspring_list = self._cspring_list
		for spring in spring_list :
			if isinstance(spring,LinearSpring2D) :
				sp = CLinearSpring2D(trans[spring._pid1],
									 trans[spring._pid2],
									 spring._stiffness,
									 spring._ref_length)
			else :
				raise UserWarning("unrecognized spring")
			#add spring to solver
			s.add_spring(sp)
			cspring_list.append(sp)

class MSSolver3D (MSSolver) :
	"""
	interface for forward euler integrator in C
	"""
		
	def create_springs (self, spring_list) :
		s = self._solver
		trans = self._trans
		cspring_list = self._cspring_list
		for spring in spring_list :
			if isinstance(spring,LinearSpring3D) :
				sp = CLinearSpring3D(trans[spring._pid1],
									 trans[spring._pid2],
									 spring._stiffness,
									 spring._ref_length)
			elif isinstance(spring,TriangleMembrane3D) :
				pid0,pid1,pid2 = spring._pids
				r1,r2,s2 = spring._ref_coords
				th = spring._thickness
				sp = CTriangleMembrane3D(trans[pid0],trans[pid1],trans[pid2],r1,r2,s2,th)
				mat = []
				for i in xrange(2) :
					for j in xrange(2) :
						for k in xrange(2) :
							for l in xrange(2) :
								mat.append(spring._material[i,j,k,l])
				
				sp.set_material(tuple(mat))
			else :
				raise UserWarning("unrecognized spring")
			#add spring to solver
			s.add_spring(sp)
			cspring_list.append(sp)

class ForwardEuler2D (MSSolver2D) :
	SolverType = CForwardEuler2D

class ForwardEuler3D (MSSolver3D) :
	SolverType = CForwardEuler3D

class ForwardMarching2D (MSSolver2D) :
	SolverType = CForwardMarching2D

class ForwardMarching3D (MSSolver3D) :
	SolverType = CForwardMarching3D


