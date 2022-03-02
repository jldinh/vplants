from physics.math import TriangleMesh,xy
from physics.mechanics import isotropic_material

ed=10#cm
thickness=0.1 #cm
loading=200 #N.cm-1
E=2e6 #N.cm-2
nu=0.1
material=isotropic_material(E,nu)

m=TriangleMesh()
#creation des points
for pid,pos in [(1,xy(2*ed,2*ed)),
				(2,xy(ed,2*ed)),
				(3,xy(0,2*ed)),
				(4,xy(0,ed)),
				(5,xy(0,0)),
				(6,xy(ed,0)),
				(7,xy(2*ed,0)),
				(8,xy(2*ed,ed)),
				(9,xy(ed,ed))] :
	m.add_point(pos,pid)
#creation des edges
for eid in xrange(1,9) :
	m.add_edge(eid)
	for pid in (eid,8-(9-eid)%8) :
		m.add_corner(eid,pid)

for i in xrange(1,9) :
	eid=m.add_edge(8+i)
	for pid in (9,i) :
		m.add_corner(eid,pid)
#creation des faces
for fid in xrange(1,9) :
	m.add_face(fid)
	for eid in (fid,8+fid,16-(9-fid)%8) :
		m.add_border(fid,eid)

