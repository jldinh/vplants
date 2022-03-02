from math import sqrt,exp
from random import random
from openalea.plantgl.math import Vector3,norm
from openalea.cmechanics import LinearSpring3D,ForwardEuler3D

NB = 10
K = 1.
weight = dict( (pid,1.) for pid in xrange(NB + 1) )
pos = dict( (pid,Vector3(pid,0,0) ) for pid in xrange(NB + 1) )
springs = [LinearSpring3D(i,i+1,K,1.) for i in xrange(NB)]

logout = open("logout.txt",'w')
###############################################
#
print "simple horizontal force"
#
###############################################
def bound (solver) :
	solver.set_force(0,Vector3(0,0,0) )
	solver.set_force(NB,solver.force(NB) + Vector3(1,0,0) )

algo = ForwardEuler3D(weight,springs,bound,logout)

dt = 0.1
algo.deform_to_equilibrium(pos,dt,1e-9)

print pos
for pid,vec in pos.iteritems() :
	assert norm(vec - (pid * exp(1),0,0) ) < 1e-6

###############################################
#
print "simple vertical force"
#
###############################################
def bound (solver) :
	solver.set_force(0,Vector3(0,0,0) )
	solver.set_force(NB,solver.force(NB) + Vector3(0,1,0) )

algo = ForwardEuler3D(weight,springs,bound,logout)

dt = 0.1
algo.deform_to_equilibrium(pos,dt,1e-9)

print pos
for pid,vec in pos.iteritems() :
	assert norm(vec - (0,pid * exp(1),0) ) < 1e-6

###############################################
#
print "simple deformation without force"
#
###############################################
K = 1.
weight = dict( (pid,1.) for pid in xrange(3) )
pos = dict( (pid,Vector3(pid,0,0) ) for pid in xrange(3) )
pos[1].y = random() * 0.01
springs = [LinearSpring3D(i,i+1,K,sqrt(2.) ) for i in xrange(2)]

def bound (solver) :
	solver.set_force(0,Vector3(0,0,0) )
	solver.set_force(2,Vector3(0,0,0) )

algo = ForwardEuler3D(weight,springs,bound,logout)

dt = 0.1
algo.deform_to_equilibrium(pos,dt,1e-7)

print pos
assert norm(pos[0] - (0,0,0) ) < 1e-6
assert norm(pos[1] - (1,1,0) ) < 1e-6
assert norm(pos[2] - (2,0,0) ) < 1e-6


