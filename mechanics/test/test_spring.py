from math import degrees,atan2
from numpy import array,zeros,diag,dot,transpose,exp,log,tensordot
from numpy.random import uniform
from scipy.linalg import norm,expm
from openalea.mechanics import (isotropic_material2D,
                                LinearSpring3D,TriangleMembrane3D)

from common_func import comp,empty

###########################################################
#
#	common funcs
#
###########################################################
def rvec () :
	return uniform(-1.,1.,3)

###########################################################
#
#	test linear spring
#
###########################################################
def test_linear () :
	state = [[(0,0,0),(2.2,0,0)],
	         [(10,20,30),(10,20,30)]]
	state = array(state)
	
	spring = LinearSpring3D(0,1,10.,2.,0.3)
	
	st = log(1.1)
	
	assert comp(spring.strain(state),st)
	assert comp(spring.stress(state),10 * st)
	assert comp(spring.energy(state),10 * st * st * 2. * 0.3)
	
	F = empty(state)
	spring.assign_forces(F,state)
	
	assert comp(F[0],(st * 3,0,0) )
	assert comp(F[1],(-st * 3,0,0) )

def test_linear_rand () :
	for i in xrange(10) :
		state0 = array([[rvec(),rvec()],
		               [(0,0,0),(0,0,0)]])
		
		spring = LinearSpring3D(0,1,10.,norm(state0[0,1,:]-state0[0,0,:]),0.23)
		
		for j in xrange(10) :
			sca = uniform(-1e-1,1e-1,1)
			
			state = state0 * exp(sca)
			
			assert comp(spring.strain(state),sca)
	
###########################################################
#
#	test triangle spring
#
###########################################################
def test_triangle_rand () :
	return
	
	state0 = [[(-1,0,0),(1,0,0),(0,1,0)],
	          [(0,0,0),(0,0,0),(0,0,0.)]]
	state0 = array(state0)

	spring = TriangleMembrane3D([0,1,2],
	                            isotropic_material2D(10.,0.),
	                            state0[0,(0,1,2),:2],
	                            0.1)
	spring._big_displacements = 0.

	for i in xrange(10) :
		st = uniform(-1e-1,1e-1,(2,2) )
		st[0,1] = st[1,0] = 0.
		
		mul = zeros( (3,3) )
		mul[:2,:2] = expm(st)
		
		state = array([dot(mul,state0[0].transpose()).transpose(),state0[1]])
		print "state\n",state
		print "strain\n",spring.strain(state)
		print "ana\n",st
		#assert comp(spring.strain(state),st)
		assert comp(spring.stress(state),st * 10.)
		assert comp(spring.energy(state),10 * tensordot(st,st) * 1. * 0.1 * 0.5)
		
		F = empty(state)
		spring.assign_forces(F,state)
		
		assert comp(F[0],(st[0,0] / 2.,st[1,1] / 2., 0.) )
		assert comp(F[1],(- st[0,0] / 2.,st[1,1] / 2., 0.) )
		assert comp(F[2],(0,- st[1,1],0) )













