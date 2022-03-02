from random import choice
from scipy import matrix
from scipy.linalg import det
import pylab
from physics.math import TriangleMesh,xy,zeros,X,Y
from physics.mechanics import isotropic_material,TensorMechanics2D
from physics.gui import QApplication,Viewer,Stage,Animation,\
				draw_mesh2D,JetMap

def surf (fid) :
	v=[m.position(pid) for pid in m.points(fid=fid)]
	A=matrix([[1,v[0].x,v[0].y],\
			  [1,v[1].x,v[1].y],\
			  [1,v[2].x,v[2].y]])
	return abs(det(A))/2.

def draw (st, rest, strain, d) :
	f_prop=dict( (fid,e.trace()) for fid,e in strain.iteritems() )
	vmin,vmax=min(f_prop.itervalues()),max(f_prop.itervalues())
	print vmin,vmax
	cm=JetMap(vmin,vmax)
	draw_mesh2D(st,rest,f_prop,cm)
	for pid,pos in rest.positions() :
		rest.set_position(pid,pos+d[pid])
	draw_mesh2D(st,rest)

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

m.refine(0)
for i in xrange(10) :
	faces=list(m.faces())
	for fid in faces :
		div=m.refine(fid)
		for nid in div :
			if nid>fid :
				faces.remove(nid)

mat=isotropic_material(10.,0.25)
mat=dict( (fid,mat) for fid in m.faces() )
forces={2:(xy(1,1)*0.5)}#{2:xy(0.1,0.5),3:xy(-0.1,0.5)}
fixed=[(0,X),(0,Y),(1,X),(1,Y)]
e0={}
for fid in m.faces() :
	e0[fid]=zeros( (2,2) )
#e0[2][Y,Y]=0.1
S=dict( (fid,surf(fid)) for fid in m.faces() )

meca=TensorMechanics2D(m,mat,e0,forces,fixed)

d=meca.displacement()
e=dict( (fid,meca.strain(fid,d)) for fid in m.faces() )

st=Stage()
draw(st,m,e,d)

qapp=QApplication([])
v=Viewer(locals())
v.set_scene(st)
v.show()
qapp.exec_()

