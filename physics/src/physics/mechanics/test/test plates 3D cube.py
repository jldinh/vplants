from physics.math import TriangleMesh,xyz,zeros,X,Y,Z
from physics.mechanics import PlateMechanics3D,isotropic_material
from physics.gui import QApplication,Viewer,Stage,Animation,\
				draw_mesh3D,JetMap
from scipy import matrix,ones

m=TriangleMesh()
#creation des points
for z in (0,1) :
	for coords in [(0,0,z),(1,0,z),(1,1,z),(0,1,z)] :
		m.add_point(xyz(*coords))
for i in xrange(4) :
	#bottom
	eid=m.add_edge()
	for pid in (i,(i+1)%4) :
		m.add_corner(eid,pid)
for i in xrange(4) :
	#top
	eid=m.add_edge()
	for pid in (i+4,4+(i+1)%4) :
		m.add_corner(eid,pid)
for i in xrange(4) :
	#vertical
	eid=m.add_edge()
	for pid in (i,i+4) :
		m.add_corner(eid,pid)
for i in xrange(4) :
	#diagonal
	eid=m.add_edge()
	for pid in (i,4+(i+1)%4) :
		m.add_corner(eid,pid)
eid=m.add_edge()
for pid in (0,2) :
	m.add_corner(eid,pid)
eid=m.add_edge()
for pid in (4,6) :
	m.add_corner(eid,pid)

for i in xrange(4) :
	fid=m.add_face()
	for eid in (i,8+(i+1)%4,12+i) :
		m.add_border(fid,eid)
	fid=m.add_face()
	for eid in (12+i,4+i,8+i) :
		m.add_border(fid,eid)

for edges in [(0,1,16),(16,2,3),(4,5,17),(17,6,7)] :
	fid=m.add_face()
	for eid in edges :
		m.add_border(fid,eid)

m-=0.5
m*=(20,20,20)

thickness=0.1 #cm
E=2e6 #N.cm-2
nu=0.1
material=isotropic_material(E,nu)
forces={}
for i in xrange(4) :
	forces[4+i]=xyz(0,0,1000)

algo=PlateMechanics3D(m,
		dict( (fid,material) for fid in m.faces() ),
		dict( (fid,thickness) for fid in m.faces() ),
		dict( (fid,zeros( (2,2) )) for fid in m.faces() ),
		forces,
		[(0,X),(0,Y),(0,Z),(1,Y),(1,Z),(3,X),(3,Z),(4,X),(4,Y)])

d=algo.displacement()
print [v.norm() for v in d.values()]

qapp=QApplication([])
v=Viewer(locals())
st=Stage()
draw_mesh3D(st,m)
for pid,pos in m.positions() :
	m.set_position(pid,pos+d[pid]*100)
draw_mesh3D(st,m)

v.set_scene(st)
v.ui.view.fit_to_scene()

v.show()
qapp.exec_()


