
def square_mesh () :
	from physics.math import TriangleMesh,xy
	m=TriangleMesh()
	for coords in [(0,0),(1,0),(1,1),(0,1),(0.5,0.5)] :
		m.add_point(xy(*coords))
	for corners in [(0,1),(1,2),(2,3),(3,0)] :
		eid=m.add_edge()
		for pid in corners :
			m.add_corner(eid,pid)
	for corner in xrange(4) :
		eid=m.add_edge()
		for pid in (4,corner) :
			m.add_corner(eid,pid)
	for i in xrange(4) :
		fid=m.add_face()
		for eid in (i,4+i,4+(i+1)%4) :
			m.add_border(fid,eid)
	return m
