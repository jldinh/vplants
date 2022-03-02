from physics.shapes import grid_graph2D
from physics.chemistry import Diffusion
from physics.gui import QApplication,Viewer,Animation,Stage,\
				draw_graph2D,JetMap

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

st=Stage()
class Simu (Animation) :
	def __init__ (self) :
		Animation.__init__(self,dt,(0.,100.))
	
	def reset (self) :
		Animation.reset(self)
		for vid in g.vertices() :
			substance[vid]=0.
		substance[0]=0.98
		st.clear()
		draw_graph2D(st,g,pos,substance,JetMap())
	
	def next (self) :
		time=Animation.next(self)
		algo.react(substance,dt)
		st.clear()
		draw_graph2D(st,g,pos,substance,JetMap())
		return time

simu=Simu()

qapp=QApplication([])
v=Viewer(locals())
v.set_scene(st)
v.set_animation(simu)
v.show()
qapp.exec_()
