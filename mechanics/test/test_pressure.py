from numpy import array,zeros,cross
from openalea.mechanics import PressureSegment,PressureTriangle

from common_func import comp,empty

######################################################
#
#	test segment
#
######################################################
def test_segment () :
	state = [[(0,0),(2,1)],
	         [(0,0),(0,0.)]]
	state = array(state)
	
	actor = PressureSegment(0,1,0.5,10.)
	F = empty(state)
	actor.assign_forces(F,state)
	
	assert comp(F[0],(- 2.5,5.) )
	assert comp(F[1],(- 2.5,5.) )

######################################################
#
#	test triangle
#
######################################################
def test_triangle () :
	state = [[(0,0,0),(2,1,0),(0,1,1)],
	         [(0,0,0),(0,0,0),(0,0,0.)]]
	state = array(state)
	
	actor = PressureTriangle(0,1,2,10.)
	F = empty(state)
	actor.assign_forces(F,state)
	
	Fref = cross(state[0,1,:] - state[0,0,:],state[0,2,:] - state[0,0,:])
	Fref *= (10. / 6.)
	
	assert comp(F[0],Fref)
	assert comp(F[1],Fref)
	assert comp(F[2],Fref)

