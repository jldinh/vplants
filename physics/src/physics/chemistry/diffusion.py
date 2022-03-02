from interface.chemistry import IChemistry

class Diffusion (object) :
	"""Implementation of discrete diffusion.
	
	discretize equation
	"""
	def __init__ (self, buckets, pipes) :
		"""Set system elements.
		
		buckets: a dict of (bucket id, volume)
		pipes: a list of (bucket_id,bucket_id,capacity)
		"""
		self._buckets = buckets
		self._pipes = pipes
	
	def differential (self, state) :
		pass
	
	def fluxes (self, state) :
		"""Compute fluxes along each pipe.
		
		state: a dict of (bucket_id,concentration)
		return: a list of fluxes
		"""
		pass

class GraphDiffusion (IChemistry) :
	"""
	implementation of diffusion between vertices
	of an undirected graph
	Ci(t+dt)=Ci(t) + sum(neighbors j) (diffusivity(Eij)*dt/V(Ci)*(Cj(t+dt)-Ci(t+dt)))
	Eij, link between i and j
	"""
	def __init__ (self, graph, vertex_volume, edge_diffusion_coefficient) :
		self._graph=graph # diffusion will occur between vertices
						  # of this graph
		self._vertex_volume=vertex_volume # volume of vertices
		self._edge_diffusion_coefficient=edge_diffusion_coefficient # diffusivity of edges
	
	def react (self, substance, dt, nb_steps = 1) :
		graph=self._graph
		vV=self._vertex_volume
		fluxes = None
		for i in xrange(nb_steps) :
			fluxes=self.fluxes(substance)
			for eid,flux in fluxes.iteritems() :
				substance[graph.source(eid)] -= flux * dt / vV[graph.source(eid)]
				substance[graph.target(eid)] += flux * dt / vV[graph.target(eid)]
		return fluxes
	
	def fluxes (self, substance) :
		"""
		compute oriented fluxed along edges
		"""
		graph=self._graph
		return dict( (eid,D*(substance[graph.source(eid)]-substance[graph.target(eid)])) for eid,D in self._edge_diffusion_coefficient.iteritems() )


class RelationDiffusion (IChemistry) :
	"""
	implementation of diffusion between vertices
	of an undirected graph
	Ci(t+dt)=Ci(t) + sum(neighbors j) (diffusivity(Eij)*dt/V(Ci)*(Cj(t+dt)-Ci(t+dt)))
	Eij, link between i and j
	"""
	def __init__ (self, relation, vertex_volume, edge_diffusion_coefficient) :
		self._relation=relation # diffusion will occur between vertices
						  # of this graph
		self._vertex_volume=vertex_volume # volume of vertices
		self._edge_diffusion_coefficient=edge_diffusion_coefficient # diffusivity of edges
	
	def react (self, substance, dt, nb_steps = 1) :
		rel=self._relation
		vV=self._vertex_volume
		fluxes = None
		for i in xrange(nb_steps) :
			fluxes=self.fluxes(substance)
			for eid,flux in fluxes.iteritems() :
				substance[rel.left(eid)] -= flux * dt / vV[graph.left(eid)]
				substance[rel.right(eid)] += flux * dt / vV[graph.right(eid)]
		return fluxes
	
	def fluxes (self, substance) :
		"""
		compute oriented fluxed along edges
		"""
		rel=self._relation
		return dict( (eid,D*(substance[rel.left(eid)]-substance[rel.right(eid)])) for eid,D in self._edge_diffusion_coefficient.iteritems() )



