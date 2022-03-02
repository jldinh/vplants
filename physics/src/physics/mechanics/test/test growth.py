import pylab
from physics.math import xy,zeros,X,Y
from physics.shapes import square_mesh
from physics.mechanics import isotropic_material,TensorMechanics2D
from physics.gui import QApplication,Viewer,Stage,Animation,\
				draw_mesh2D,JetMap

l=1. #cm
thickness=0.01 #cm
P=2000 #N.cm-2
E=2e6 #N.cm-2
nu=0.25
material=isotropic_material(E,nu)

m=square_mesh()
m*=(l,l)

for i in xrange(10) :
	faces=list(m.faces())
	for fid in faces :
		div=m.refine(fid)
		for nid in div :
			if nid>fid :
				faces.remove(nid)

print m.nb_faces()

mat=dict( (fid,material) for fid in m.faces() )
thickness=dict( (fid,0.1) for fid in m.faces() )

fixed=[]
for pid,pos in m.positions() :
	if pos.y<0.001 :
		fixed.append( (pid,X) )
		fixed.append( (pid,Y) )
forces={}
top_pid=set()
for eid in m.edges() :
	if m.centroid(m.points(eid=eid)).y>0.999 :
		f=P*m.length(eid)/2.
		for pid in m.points(eid=eid) :
			top_pid.add(pid)
			try :
				forces[pid]+=xy(0,f)
			except KeyError :
				forces[pid]=xy(0,f)

toto=[(m.position(pid).x,pid) for pid in top_pid]
toto.sort()
top_pid=[i[1] for i in toto]

e0=dict( (fid,zeros( (2,2) )) for fid in m.faces() )
algo=TensorMechanics2D(m,mat,thickness,e0,forces,fixed)
d=algo.displacement()
npos=dict( (pid,m.position(pid)+d[pid]) for pid in m.points() )
strain=dict( (fid,algo.strain(fid,d)) for fid in m.faces() )

ne0=dict( (fid,0.5*st) for fid,st in strain.iteritems() )
nforces={}
algo=TensorMechanics2D(m,mat,thickness,ne0,{},fixed)
nd=algo.displacement()
nstrain=dict( (fid,algo.strain(fid,nd)) for fid in m.faces() )

for pid,pos in m.positions() :
	m.set_position(pid,pos+nd[pid])

for fid,st in nstrain.iteritems() :
	ne0[fid]-=st

algo=TensorMechanics2D(m,mat,thickness,ne0,{},fixed)
nnd=algo.displacement()




pylab.plot([(d[pid].y,nd[pid].y,nnd[pid].y) for pid in top_pid])
pylab.show()

