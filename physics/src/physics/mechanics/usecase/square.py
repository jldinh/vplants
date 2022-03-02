from openalea.plantgl.math import Vector2
from openalea.container import Topomesh
from openalea.physics.mechanics import isotropic_material,TriangleMesh2DEnergy,EulerIntegrator

ed=10#cm
thickness=0.1 #cm
loading=200 #N.cm-1
E=2e6 #N.cm-2
nu=0.1
mat=isotropic_material(E,nu)

m=Topomesh(2)
pos={}
#########################
#
#		geometry
#
#########################
#creation des points
for pid,vec in [(1,(2*ed,2*ed)),
				(2,(ed,2*ed)),
				(3,(0,2*ed)),
				(4,(0,ed)),
				(5,(0,0)),
				(6,(ed,0)),
				(7,(2*ed,0)),
				(8,(2*ed,ed)),
				(9,(ed,ed))] :
	m.add_wisp(0,pid)
	pos[pid]=Vector2(*vec)
#creation des edges
for eid in xrange(1,9) :
	m.add_wisp(1,eid)
	for pid in (eid,8-(9-eid)%8) :
		m.link(1,eid,pid)

for i in xrange(1,9) :
	eid=m.add_wisp(1,8+i)
	for pid in (9,i) :
		m.link(1,eid,pid)
#creation des faces
for fid in xrange(1,9) :
	m.add_wisp(2,fid)
	for eid in (fid,8+fid,16-(9-fid)%8) :
		m.link(2,fid,eid)

#solution
wanted_disp={1:Vector2(-0.002,0.02),
			2:Vector2(-0.001,0.02),
			3:Vector2(0,0.02),
			4:Vector2(0,0.01),
			5:Vector2(0,0),
			6:Vector2(-0.001,0),
			7:Vector2(-0.002,0),
			8:Vector2(-0.002,0.01),
			9:Vector2(-0.001,0.01)}

#########################
#
#		mechanics
#
#########################
rest_shape={}
material={}
for fid in m.wisps(2) :
	material[fid]=mat
	pid1,pid2,pid3=m.borders(2,fid,2)
	rest_shape[fid]={pid1:Vector2(),
					 pid2:pos[pid2]-pos[pid1],
					 pid3:pos[pid3]-pos[pid1]}

fval=loading*ed/2./thickness
ext_forces={1:Vector2(0,fval),2:Vector2(0,fval*2),3:Vector2(0,fval)}

def external_constraint (forces) :
	for pid,force in ext_forces.iteritems() :
		forces[pid]+=force
	for pid in (3,4,5) :
		forces[pid].x=0.
	for pid in (5,6,7) :
		forces[pid].y=0

force_field=TriangleMesh2DEnergy(rest_shape,material)
weight=dict( (pid,1.) for pid in m.wisps(0) )
meca=EulerIntegrator(weight,[force_field],external_constraint,Vector2)

ini_pos=dict( (pid,Vector2(vec)) for pid,vec in pos.iteritems() )
dt_meca=1e-4
from time import time
tinit=time()
for j in xrange(100) :
	print "step",j
	for i in xrange(100) :
		meca.deform(pos,dt_meca)
	
	"""for fid in m.wisps(2) :
		strain=force_field.strain(fid,pos)
		print "ep",strain
		stress=force_field.stress(fid,pos)
		print stress"""
	
	for pid,vec in pos.iteritems() :
		print pid,wanted_disp[pid],vec-ini_pos[pid]

print "total time",time()-tinit
