from physics.shapes import grid_graph2D
from physics.chemistry import Diffusion

g,pos=grid_graph2D( (10,10) )
vV=dict( (vid,0.01) for vid in g.vertices() )
eD=dict( (eid,0.1) for eid in g.edges() )
dt=1.

class GraphTopoMesh (object) :
	def __init__ (self, graph) :
		self._graph=graph
	def _cells (self, pid) :
		yield self._graph.source(pid)
		yield self._graph.target(pid)
	def cells (self, pid=None) :
		if pid is None :
			return self._graph.vertices()
		else :
			return self._cells(pid)
	def points (self) :
		return self._graph.edges()

topo=GraphTopoMesh(g)
substance={}
algo=Diffusion(topo,vV,eD,{0:0.98,99:0.},{})

algo.react(substance,dt)

