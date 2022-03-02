from random import choice,random
from physics.math import Graph,xy
from physics.gui import QApplication,Viewer,EmptyScene,Stage,\
				draw_graph2D,\
				JetMap

g=Graph()
vid=g.add_vertex()
pos={}
pos[vid]=xy()
used_id=[vid]
for i in xrange(10) :
	vid=g.add_vertex()
	pos[vid]=xy(random(),random())
	g.add_edge( (vid,choice(used_id)) )
	used_id.append(vid)

substance=dict( (vid,random()) for vid in g.vertices() )

st=Stage()
draw_graph2D(st,g,pos,substance,JetMap())

qapp=QApplication([])
v=Viewer(locals())
v.set_scene(st)
v.show()
qapp.exec_()
