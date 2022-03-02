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

def draw (st, rest, strain) :
	f_prop=dict( (fid,e.trace()) for fid,e in strain.iteritems() )
	vmin,vmax=-10.,10.#min(f_prop.itervalues()),max(f_prop.itervalues())
	cm=JetMap(vmin,vmax)
	draw_mesh2D(st,rest,f_prop,cm)

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

mat=isotropic_material(1.,0.25)
mat=dict( (fid,mat) for fid in m.faces() )
forces={2:(xy(1,1)*0.5)}#{2:xy(0.1,0.5),3:xy(-0.1,0.5)}
fixed=[(0,X),(0,Y),(1,X),(1,Y)]
e0={}
for fid in m.faces() :
	e0[fid]=zeros( (2,2) )
#e0[2][Y,Y]=0.1
S=dict( (fid,surf(fid)) for fid in m.faces() )

st=Stage()
meca=TensorMechanics2D(m,mat,e0,forces,fixed)

X=[0]
efids=list(m.faces(pid=2))
Y=[tuple(0. for fid in efids)]

class Simu (Animation) :
	def __init__ (self) :
		Animation.__init__(self,1,(0,9))
		self.th=0.5
	
	def reset (self) :
		Animation.reset(self)
		st.clear()
		draw(st,m,e0)
	
	def next (self) :
		time=Animation.next(self)
		d=meca.displacement()
		e={}
		for fid in m.faces() :
			e[fid]=meca.strain(fid,d)
		st.clear()
		draw(st,m,e)
		#enregistrement
		X.append(X[-1]+1)
		Y.append(tuple(e[fid].trace() for fid in efids))
		#subdivision
		faces=list(m.faces())
		for fid in faces :
			div=m.refine(fid)
			for nid in div :
				if nid>fid :
					faces.remove(nid)
			for fid in div :
				if fid in efids :
					ind=efids.index(fid)
					common=set(m.faces(pid=2))&set(div[fid])
					assert len(common)==1
					efids[ind]=common.pop()
			old_S=dict( (fid,S[fid]) for fid in div )
			old_e=dict( (fid,e0[fid]) for fid in div )
			old_m=dict( (fid,mat[fid]) for fid in div )
			for fid in div :
				del S[fid]
				del e0[fid]
				del mat[fid]
			for ofid,nfids in div.iteritems() :
				for fid in nfids :
					S[fid]=old_S[ofid]
					e0[fid]=old_e[ofid]
					mat[fid]=old_m[ofid]
		self.th/=1.8
		return time

qapp=QApplication([])
v=Viewer(locals())
v.set_scene(st)
v.show()
v.set_animation(Simu())
qapp.exec_()

pylab.plot(X,Y)
pylab.show()

