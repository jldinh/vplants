from openalea.cphysics.mechanics import LinearSpring2D,ForwardEuler2D

raw_input("start")

for loop in xrange(1000) :
	print loop
	NB = 1000
	weight = dict( (pid,1.) for pid in xrange(NB+1) )
	pos = dict( (pid,(pid,0.) ) for pid in xrange(NB+1) )
	springs = [LinearSpring2D(0,1,1.,1.) for i in xrange(NB)]
	
	def boundary (s) :
		s.set_force(NB,s.force(NB) + (1.,0.) )
		s.set_force(0,(0.,0.))
	
	euler = ForwardEuler2D(weight,springs,boundary)
	del springs
	euler.deform(pos,0.1,1)

