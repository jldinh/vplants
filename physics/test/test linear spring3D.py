from openalea.plantgl.math import Vector3
from openalea.physics.mechanics import LinearSpring3D,ForwardEuler3D

weight={0:1.,1:1.,2:1.}
pos={0:Vector3(0.,0.),1:Vector3(1.,0.),2:Vector3(2.,0.)}

springs=[LinearSpring3D(0,1,1.,2.),LinearSpring3D(1,2,1.,2.)]

def bound (forces) :
	forces[0].x=0.
	forces[0].y=0.
	forces[0].z=0.
	forces[2].y=0.
	forces[2].z=0.

s=ForwardEuler3D(weight,springs,bound)

for i in xrange(100) :
	s.deform(pos,0.1,100)
	print pos[1],pos[2]


