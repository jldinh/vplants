from math import radians
from openalea.plantgl.math import Vector3,Vector2,Matrix2,norm
from openalea.physics.mechanics import isotropic_material,TriangleSpring3D,ForwardEuler3D

weight={0:1.,1:1.,2:1.}
pos={0:Vector3(0.,0.,0.),1:Vector3(1.,0.,0.5),2:Vector3(0.,1.,0.6)}

rs={0:Vector2(0.,0.),1:Vector2(1.01,0.),2:Vector2(0.,1.01)}
rot=Matrix2.rotation(radians(60))
for pid,vec in rs.iteritems() :
	rs[pid]=rot*vec

spring=TriangleSpring3D(isotropic_material(1.,0),rs)

def bound (forces) :
	forces[0].x=0.
	forces[0].y=0.
	forces[0].z=0.
	forces[1].y=0.

s=ForwardEuler3D(weight,[spring],bound)

for i in xrange(1) :
	s.deform(pos,0.1,1)
	print norm(pos[1]),norm(pos[2])

