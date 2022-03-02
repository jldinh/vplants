from physics.math import TriangleMesh,xy
from physics.gui import QApplication,Viewer,Stage,draw_mesh2D
import pdb

m=TriangleMesh()
for coords in [(0,0),(1,0),(1,1),(0,1),(0.5,1.5)] :
	m.add_point(xy(*coords))
for corners in [(0,1),(1,2),(2,3),(3,0),(0,2),(2,4),(4,3)] :
	eid=m.add_edge()
	for pid in corners :
		m.add_corner(eid,pid)
for edges in [ (0,1,4),(4,2,3),(2,5,6) ] :
	fid=m.add_face()
	for eid in edges :
		m.add_border(fid,eid)

####
print m.refine(2)
####
st=Stage()
draw_mesh2D(st,m)

qapp=QApplication([])
v=Viewer(locals())
v.set_scene(st)
v.show()
qapp.exec_()
