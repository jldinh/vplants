from openalea.plantgl.math import Vector3,norm
from openalea.cphysics.mechanics import LinearSpring3D,ForwardEuler3D

weight={0:1.,1:1.,2:1.}
pos={0:(0.,0.,0.),
	1:(1.,0.1,0.),
	2:(2.,0.,0.)}

springs=[LinearSpring3D(0,1,1.,1.414),LinearSpring3D(1,2,1.,1.414)]

def bound (solver) :
	solver.set_force(0,(0.,0.,0.) )
	solver.set_force(2,(0.,0.,0.) )

#solver.set_force(1,solver.fx(1)+0.1,solver.fy(1)+0.1)

s = ForwardEuler3D(weight,springs,bound)

for i in xrange(100) :
	s.deform(pos,0.1,100)
	print i,norm(s.position(1))

