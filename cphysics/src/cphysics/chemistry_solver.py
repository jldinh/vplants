from openalea.physics.chemistry import Reaction,GraphTransport,RelationTransport,RelationReverseTransport,GraphDiffusion
from _cphysics import CReaction,CForwardTransport,CCForwardEuler

class ForwardEuler (object) :
	"""
	interface for forward euler integrator in C
	"""
	def __init__ (self, tank_volume, actors, external_constraint) :
		s=CCForwardEuler()
		trans={}
		for tid,v in tank_volume.iteritems() :
			ind=s.add_tank(v,0.)
			trans[tid]=ind
		cactor_list=[]
		for actor in actors :
			if isinstance(actor,Reaction) :
				act=CReaction()
				for tid,val in actor._creation.iteritems() :
					act.set_creation(trans[tid],val)
				for tid,val in actor._decay.iteritems() :
					act.set_decay(trans[tid],val)
				s.add_actor(act)
				cactor_list.append(act)
			elif isinstance(actor,GraphTransport) :
				act=CForwardTransport()
				graph=actor._graph
				for eid,pump in actor._edge_pumps.iteritems() :
					act.add_pipe(graph.source(eid),graph.target(eid),pump)
				s.add_actor(act)
				cactor_list.append(act)
			elif isinstance(actor,RelationTransport) :
				act=CForwardTransport()
				rel=actor._relation
				for lid,pump in actor._link_pumps.iteritems() :
					act.add_pipe(rel.left(lid),rel.right(lid),pump)
				s.add_actor(act)
				cactor_list.append(act)
			elif isinstance(actor,RelationReverseTransport) :
				act=CForwardTransport()
				rel=actor._relation
				for lid,pump in actor._link_pumps.iteritems() :
					act.add_pipe(rel.right(lid),rel.left(lid),pump)
				s.add_actor(act)
				cactor_list.append(act)
			elif isinstance(actor,GraphDiffusion) :
				act=CForwardTransport()
				graph=actor._graph
				for eid,strength in actor._edge_diffusion_coefficient.iteritems() :
					act.add_pipe(graph.source(eid),graph.target(eid),strength)
					act.add_pipe(graph.target(eid),graph.source(eid),strength)
				s.add_actor(act)
				cactor_list.append(act)
		self._cactor_list=cactor_list
		self._trans=trans
		self._solver=s
		self._boundary=external_constraint
	
	def _external_constraint (self) :
		self._boundary(self)
	
	def react (self, substance, dt, nb_steps=1) :
		s=self._solver
		trans=self._trans
		for tid,l in substance.iteritems() :
			s.set_level(trans[tid],l)
		s.set_boundary_function(self._external_constraint)
		s.react(dt,nb_steps)
		s.set_boundary_function(None)
		for tid in substance :
			substance[tid]=s.level(trans[tid])
	
	def level (self, tid) :
		return self._solver.level(self._trans[tid])
	
	def set_level (self, tid, l) :
		self._solver.set_level(self._trans[tid],l)

