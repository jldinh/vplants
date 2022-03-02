from math import radians
from openalea.plantgl.math import Vector2,Matrix2
from openalea.physics.mechanics import isotropic_material,TriangleSpring2D,ForwardEuler2D

weight={0:1.,1:1.,2:1.}
pos={0:Vector2(0.,0.),1:Vector2(1.,0.),2:Vector2(0.,1.)}

rs={0:Vector2(0.,0.),1:Vector2(1.01,0.),2:Vector2(0.,1.01)}
rot=Matrix2.rotation(radians(60))
for pid,vec in rs.iteritems() :
	rs[pid]=rot*vec

spring=TriangleSpring2D(isotropic_material(1.,0),rs)

def bound (forces) :
	forces[0].x=0.
	forces[0].y=0.
	forces[1].y=0.

s=ForwardEuler2D(weight,[spring],bound)

for i in xrange(100) :
	s.deform(pos,0.1,100)
	print pos[1].x,pos[2]

