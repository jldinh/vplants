from openalea.cphysics.mechanics import LinearSpring2D,ForwardEuler2D

weight = {0:1.,1:1.,2:1.}
pos = {0:(0.,0.),
	   1:(1.,0.1),
	   2:(2.,0.)}

springs = [LinearSpring2D(0,1,1.,1.414),LinearSpring2D(1,2,1.,1.414)]

def bound (solver) :
	solver.set_force(0, (0.,0.) )
	solver.set_force(2, (0.,0.) )

#solver.set_force(1,solver.fx(1)+0.1,solver.fy(1)+0.1)

s = ForwardEuler2D(weight,springs,bound)

for i in xrange(100) :
	s.deform(pos,0.1,100)
	print i,s.position(1)

