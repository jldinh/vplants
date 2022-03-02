from numpy import array
from openalea.mechanics import ViscousDamper3D
from common_func import comp,empty

def test_forces () :
	state = [[(0.,0,0),(0,0,0),(0,0,0),(1,1,1)],
	         [(10,20,30),(10,20,30),(10,20,30),(10,20,30)]]
	state = array(state)
	
	damp = ViscousDamper3D( (0,),0.1)
	F = empty(state)
	damp.assign_forces(F,state)
	
	assert comp(F[0],(-1,-2,-3) )
	assert comp(F[1],(0,0,0) )
	assert comp(F[2],(0,0,0) )
	assert comp(F[3],(0,0,0) )
	
	damp = ViscousDamper3D( (1,),0.1)
	F = empty(state)
	damp.assign_forces(F,state)
	
	assert comp(F[0],(0,0,0) )
	assert comp(F[1],(-1,-2,-3) )
	assert comp(F[2],(0,0,0) )
	assert comp(F[3],(0,0,0) )
	
	damp = ViscousDamper3D( (2,),0.1)
	F = empty(state)
	damp.assign_forces(F,state)
	
	assert comp(F[0],(0,0,0) )
	assert comp(F[1],(0,0,0) )
	assert comp(F[2],(-1,-2,-3) )
	assert comp(F[3],(0,0,0) )
	
	damp = ViscousDamper3D( (3,),0.1)
	F = empty(state)
	damp.assign_forces(F,state)
	
	assert comp(F[0],(0,0,0) )
	assert comp(F[1],(0,0,0) )
	assert comp(F[2],(0,0,0) )
	assert comp(F[3],(-1,-2,-3) )


