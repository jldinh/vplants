from random import choice,random
from physics.math import Mesh,xy
from physics.gui import QApplication,Viewer,EmptyScene,Stage,\
				draw_mesh2D,\
				JetMap

m=Mesh()
for c in [(0,0),(1,0),(1,1),(0,1),(0.5,0.5)] :
	m.add_point(xy(*c))
for c in [(0,1,4),(1,2,4),(2,3,4),(3,0,4)] :
	fid=m.add_face()
	for pid in c :
		m.add_link(fid,pid)

substance=dict( (fid,random()) for fid in m.faces() )

st=Stage()
draw_mesh2D(st,m,substance,JetMap())

qapp=QApplication([])
v=Viewer(locals())
v.set_scene(st)
v.show()
qapp.exec_()
