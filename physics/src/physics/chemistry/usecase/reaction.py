from random import random
from physics.shapes import grid_graph2D
from physics.chemistry import Reaction
from physics.gui import QApplication,Viewer,Animation,Stage,\
				draw_graph2D,JetMap

g,pos=grid_graph2D( (10,10) )
creation=dict( (vid,0.01) for vid in g.vertices() )
decay=dict( (vid,0.01+random()/10.) for vid in g.vertices() )

dt=1.

substance=dict( (vid,0.) for vid in g.vertices() )
algo=Reaction(creation,decay)

st=Stage()
class Simu (Animation) :
	def __init__ (self) :
		Animation.__init__(self,dt,(0.,100.))
	
	def reset (self) :
		Animation.reset(self)
		for vid in g.vertices() :
			substance[vid]=0.
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
