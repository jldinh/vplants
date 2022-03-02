from numpy import array
from numpy.linalg import eig
from openalea.mechanics import isotropic_material2D,TriangleMembrane3D

from common_func import empty,comp

def test_rotational_invariance () :
	mat = isotropic_material2D(10.,0.)

	state0 = [[(0,0,0),(1,0,0),(0,1,0)],
	          [(0,0,0),(0,0,0),(0,0,0.)]]
	state0 = array(state0)
	
	state = state0 * 1.1
	
	#first triangle
	sp = TriangleMembrane3D( (0,1,2),
	                         mat,
	                         state0[0,(0,1,2),:2],
	                         0.1)
	
	st1 = sp.strain(state)

	f1 = empty(state)
	sp.assign_forces(f1,state)
	
	#second triangle
	sp = TriangleMembrane3D( (1,2,0),
	                         mat,
	                         state0[0,(1,2,0),:2],
	                         0.1)
	
	st2 = sp.strain(state)
	
	f2 = empty(state)
	sp.assign_forces(f2,state)
	
	#third triangle
	sp = TriangleMembrane3D( (2,0,1),
	                         mat,
	                         state0[0,(2,0,1),:2],
	                         0.1)
	
	st3 = sp.strain(state)
	
	f3 = empty(state)
	sp.assign_forces(f3,state)
	
	#comparisons
	assert comp(st1,st2)
	assert comp(st2,st3)
	
	assert comp(f1,f2)
	assert comp(f2,f3)


