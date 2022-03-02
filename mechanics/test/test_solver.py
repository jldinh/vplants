from math import log
from numpy import array
from openalea.mechanics import LinearSpring3D,StaticSolver3D

from common_func import comp

################################################
#
#	static solver
#
################################################
def test_static () :
	pass
#	pt1 = Particule3D(1,(0,0,0) )
#	pt1.set_velocity(array([10,20,30]) )
#	pt2 = Particule3D(1,(2.2,0,0) )
#	pt2.set_velocity(array([10,20,30]) )
#	
#	pts = {1:pt1,2:pt2}
#	
#	spring = LinearSpring3D(1,2,10.,2.,0.3)
#	
#	def bound (solver) :
#		solver.set_force(1,solver.force(1) + (10,10,10) )
#		solver.set_position(2,(3,3,3) )
#	
#	solver = StaticSolver3D(pts,[spring],bound)
#	
#	solver.compute_forces()
#	
#	st = log(1.1)
#	
#	assert comp(solver.position(1),(0,0,0) )
#	assert comp(solver.position(2),(3,3,3) )
#	assert comp(pt2.position(),(3,3,3) )
#	
#	assert comp(solver.force(1),(st * 3 + 10,10,10) )
#	assert comp(solver.force(2),(-st * 3,0,0) )

