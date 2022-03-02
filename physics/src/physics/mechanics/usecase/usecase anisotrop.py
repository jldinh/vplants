#page 302 de "the finite element method in engineering"

from math import radians
from physics.math import X,Y,xy,zeros
from physics.mechanics import TensorMechanics2D,axis_material,UniformPressure2D
from square import *

#refinement
for i in xrange(8) :
	faces=list(m.faces())
	while len(faces)>0 :
		fid=faces[0]
		div_faces,div_edges=m.refine(fid)
		for nid,div_info in div_faces :
			faces.remove(nid)

hmat=axis_material(radians(0),E*0.5,E,nu)
vmat=axis_material(radians(90),E*0.5,E,nu)

mat={}
for fid in m.faces() :
	p1,p2,p3=[m.position(pid) for pid in m.points(fid=fid)]
	bary=(p1+p2+p3)/3.
	if bary.x>ed :
		mat[fid]=hmat
	else :
		mat[fid]=vmat
#algo
fixed=[]
for pid,pos in m.positions() :
	if pos.y<0.001 :
		fixed.append( (pid,X) )
		fixed.append( (pid,Y) )

F=xy(0,loading*(m.position(1)-m.position(2)).norm()/2.)*10
thick=dict( (fid,thickness) for fid in m.faces() )
algo=TensorMechanics2D(m,
		mat,
		thick,
		dict( (fid,zeros( (2,2) )) for fid in m.faces() ),
		UniformPressure2D(m,loading*100,thick).forces(),
		fixed)
d=algo.displacement()
stress=dict( (fid,algo.stress(fid,d)) for fid in m.faces() )
strain=dict( (fid,algo.strain(fid,d)) for fid in m.faces() )

from physics.gui import draw_mesh2D,JetMap
from pglvisu import QApplication,Viewer,Stage,Animation
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


