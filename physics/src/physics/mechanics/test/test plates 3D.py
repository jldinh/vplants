from physics.math import TriangleMesh,xyz,zeros,X,Y,Z
from physics.mechanics import PlateMechanics3D,isotropic_material
from physics.gui import QApplication,Viewer,Stage,Animation,\
				draw_mesh3D,JetMap
from scipy import matrix,ones

m=TriangleMesh()
#creation des points
for coords in [(0,0,0),(1,0,0),(1,1,1),(0,1,1)] :
	m.add_point(xyz(*coords))
for pts in [(0,1),(1,2),(2,3),(3,0),(0,2)] :
	eid=m.add_edge()
	for pid in pts :
		m.add_corner(eid,pid)
for edges in [(0,1,4),(2,3,4)] :
	fid=m.add_face()
	for eid in edges :
		m.add_border(fid,eid)

thickness=0.1 #cm
E=2e6 #N.cm-2
nu=0.1
material=isotropic_material(E,nu)

algo=PlateMechanics3D(m,
		dict( (fid,material) for fid in m.faces() ),
		dict( (fid,thickness) for fid in m.faces() ),
		dict( (fid,zeros( (2,2) )) for fid in m.faces() ),
		{3:xyz(0,0.1,0),2:xyz(0,0,0.1)},
				[(0,X),(0,Y),(0,Z),(1,X),(2,Y)])

d=algo.displacement()

qapp=QApplication([])
v=Viewer(locals())
st=Stage()
draw_mesh3D(st,m)
for pid,pos in m.positions() :
	m.set_position(pid,pos+d[pid])
draw_mesh3D(st,m)

v.set_scene(st)
v.show()
qapp.exec_()


