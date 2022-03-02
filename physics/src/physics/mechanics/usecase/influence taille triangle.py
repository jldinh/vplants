import pylab
from physics.math import TriangleMesh,xy,zeros,X,Y
from physics.mechanics import isotropic_material,TensorMechanics2D
from physics.gui import QApplication,Viewer,Stage,Animation,\
				draw_mesh2D,JetMap

m=TriangleMesh()
for coords in [(0,0),(1,0),(1,1),(0,1)] :
	m.add_point(xy(*coords))
for corners in [(0,1),(1,2),(2,3),(3,0),(0,2)] :
	eid=m.add_edge()
	for pid in corners :
		m.add_corner(eid,pid)
for edges in [ (0,1,4),(4,2,3) ] :
	fid=m.add_face()
	for eid in edges :
		m.add_border(fid,eid)
m.refine(0)

materiau=isotropic_material(10.,0.25)
#forces={2:(xy(1,1)*0.05)}#{2:xy(0.1,0.5),3:xy(-0.1,0.5)}
P=0.1

def meca () :
	mat=dict( (fid,materiau) for fid in m.faces() )
	fixed=[]
	for pid,pos in m.positions() :
		if pos.y<0.001 :
			fixed.append( (pid,X) )
			fixed.append( (pid,Y) )
	forces={}
	for eid in m.edges() :
		if m.centroid(m.points(eid=eid)).y>0.999 :
			pid1,pid2=m.points(eid=eid)
			f=P*(m.position(pid2)-m.position(pid1)).norm()/2.
			try :
				forces[pid1]+=xy(0,f)
			except KeyError :
				forces[pid1]=xy(0,f)
			try :
				forces[pid2]+=xy(0,f)
			except KeyError :
				forces[pid2]=xy(0,f)
	e0=dict( (fid,zeros( (2,2) )) for fid in m.faces() )
	algo=TensorMechanics2D(m,mat,e0,forces,fixed)
	return algo

xp=[0]
algo=meca()
d=algo.displacement()
yp=[max(abs(algo.strain(fid,d).trace()) for fid in m.faces() )]
dp=[d[2].norm()]
sp=[d[2].norm()/1.]
spyy=[max(abs(algo.strain(fid,d)[Y,Y]) for fid in m.faces() )]

for i in xrange(1,12) :
	print i
	faces=list(m.faces())
	for fid in faces :
		div=m.refine(fid)
		for nid in div :
			if nid>fid :
				faces.remove(nid)
	print "\t",m.nb_faces()
	algo=meca()
	d=algo.displacement()
	yp.append(max(abs(algo.strain(fid,d).trace()) for fid in m.faces() ))
	spyy.append(max(abs(algo.strain(fid,d)[Y,Y]) for fid in m.faces() ))
	dp.append(d[2].norm())
	for eid in m.edges(pid=2) :
		if m.centroid(m.points(eid=eid)).x>0.999 :
			pid1,pid2=m.points(eid=eid)
			sp.append( (d[pid1]-d[pid2]).norm()/(m.position(pid1)-m.position(pid2)).norm() )
	xp.append(i)

qapp=QApplication([])
v=Viewer(locals())
st=Stage()
draw_mesh2D(st,m)
for pid,pos in m.positions() :
	m.set_position(pid,pos+d[pid])
draw_mesh2D(st,m)
v.set_scene(st)
v.show()
qapp.exec_()

pylab.plot(xp,spyy)
pylab.show()

