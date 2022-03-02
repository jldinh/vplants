from math import radians
from openalea.plantgl.math import Vector2,Vector3,Matrix2,norm
from openalea.cphysics.mechanics import isotropic_material,TriangleSpring3D,ForwardEuler3D

weight={0:1.,1:1.,2:1.}
pos={0:Vector3(0.,0.,0.),1:Vector3(1.,0.,0.5),2:Vector3(0.,1.,0.6)}

rs={0:Vector2(0.,0.),1:Vector2(1.01,0.),2:Vector2(0.,1.01)}
rot=Matrix2.rotation(radians(60))
for pid,vec in rs.iteritems() :
	rs[pid]=rot*vec

spring=TriangleSpring3D(isotropic_material(1.,0),rs)

def bound (solver) :
	solver.set_force(0,0.,0.,0.)
	solver.set_force(1,solver.fx(1),0.,solver.fz(1))

s=ForwardEuler3D(weight,[spring],bound)

for i in xrange(100) :
	s.deform(pos,0.1,100)
	print norm(Vector3(s.posx(1),s.posy(1),s.posz(1))),norm(Vector3(s.posx(2),s.posy(2),s.posz(2)))

