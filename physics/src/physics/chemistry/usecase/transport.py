from random import random
from physics.shapes import grid_graph2D
from physics.chemistry import Transport
from physics.gui import QApplication,Viewer,Animation,Stage,\
				draw_graph2D,JetMap,InvGrayMap

g,pos=grid_graph2D( (10,10) )
vV=dict( (vid,0.1) for vid in g.vertices() )
eP=dict( (eid,random()*0.01) for eid in g.edges() )
dt=1.

substance={}
algo=Transport(g,vV,eP,{0:0.9,99:0.},{})

st=Stage()
class Simu (Animation) :
	def __init__ (self) :
		Animation.__init__(self,dt,(0.,100.))
	
	def reset (self) :
		Animation.reset(self)
		for vid in g.vertices() :
			substance[vid]=0.
		substance[0]=0.9
		st.clear()
		draw_graph2D(st,g,pos,substance,JetMap(),eP,InvGrayMap(0.,0.01))
	
	def next (self) :
		time=Animation.next(self)
		algo.react(substance,dt)
		st.clear()
		draw_graph2D(st,g,pos,substance,JetMap(),eP,InvGrayMap(0.,0.01))
		return time

simu=Simu()

qapp=QApplication([])
v=Viewer(locals())
v.set_scene(st)
v.set_animation(simu)
v.show()
qapp.exec_()
