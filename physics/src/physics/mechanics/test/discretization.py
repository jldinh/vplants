#page 302 de "the finite element method in engineering"

from physics.math import X,Y,xy,zeros
from physics.mechanics import TensorMechanics2D
from test_plate import *

#refinement
for i in xrange(9) :
	faces=list(m.faces())
	while len(faces)>0 :
		fid=faces[0]
		for nid in m.refine(fid) :
			faces.remove(nid)

print "nb_faces",m.nb_faces()
#parameters
forces={}
for eid in m.edges() :
	pid1,pid2=m.points(eid=eid)
	pos1=m.position(pid1)
	pos2=m.position(pid2)
	if ((pos1+pos2)/2.).y>(1.99*ed) :
		F=xy(0,loading*(pos1-pos2).norm()/2.)
		try :
			forces[pid1]+=F
		except KeyError :
			forces[pid1]=F
		try :
			forces[pid2]+=F
		except KeyError :
			forces[pid2]=F.copy()

fixed=[]
for pid,pos in m.positions() :
	if pos.x<0.001 :
		fixed.append( (pid,X) )
	if pos.y<0.001 :
		fixed.append( (pid,Y) )

#algo
algo=TensorMechanics2D(m,
		dict( (fid,material) for fid in m.faces() ),
		dict( (fid,thickness) for fid in m.faces() ),
		dict( (fid,zeros( (2,2) )) for fid in m.faces() ),
		forces,
		fixed)
d=algo.displacement()
stress=dict( (fid,algo.stress(fid,d)) for fid in m.faces() )
strain=dict( (fid,algo.strain(fid,d)) for fid in m.faces() )

#verification
seuil=1e-9
for fid,T in stress.iteritems() :
	assert abs(T[X,X])<seuil
	assert abs(T[X,Y])<seuil
	assert abs(T[Y,X])<seuil
	assert abs(T[Y,Y]-2000.)<seuil

"""
from physics.gui import QApplication,Viewer,Stage,Animation,\
				draw_mesh2D,JetMap
qapp=QApplication([])
v=Viewer(locals())
st=Stage()
f_prop=dict( (fid,e.trace()) for fid,e in strain.iteritems() )
vmin,vmax=min(f_prop.itervalues()),max(f_prop.itervalues())
print vmin,vmax,vmax-vmin
draw_mesh2D(st,m,f_prop,JetMap(vmin,vmax))
v.set_scene(st)
v.show()
qapp.exec_()
"""
