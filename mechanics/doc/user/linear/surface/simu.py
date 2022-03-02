###################################################
#
print "parameters"
#
###################################################
#begin parameters
from numpy import zeros
from math import pi,sin,cos
from openalea.container import Grid

NB = 10 #(None) #number of points in one dimension
g = Grid( (NB,NB) ) #topology of the system

m = 1. #(kg) #mass of points
E = 1e2 #(N.m-2) #Young's modulus
l0 = 1. #(m) #ref length
thickness = 0.01 #(m) #thickness of the surface
P = 0.01 #(Pa) #pressure inside

S = l0 * thickness #(m2) #cross section of a spring

damping = 0.3 #(N.m-1.s) #damping coefficient

state0 = zeros( (2,len(g),3) )
for pid in g :
	i,j = g.coordinates(pid)
	state0[0,pid,0] = i * l0 - l0 * (NB - 1) / 2.
	state0[0,pid,1] = j * l0 - l0 * (NB - 1) / 2.

t0 = 0. #(s) #starting time of the simulation
dt = 1e0 #(s) #time step to look at the evolution of the system

#end parameters
############################################
#
print "create springs"
#
############################################
#begin create springs
from openalea.mechanics import LinearSpring3D

sps = []

#horizontal
for i in range(1,(NB - 1) ) :
	for j in range(NB - 1) :
		pid1 = g.index( (i,j) )
		pid2 = g.index( (i,j + 1) )
		sp = LinearSpring3D(pid1,pid2,E,l0,S)
		sps.append(sp)

#vertical
for i in range(NB - 1) :
	for j in range(1,(NB - 1) ) :
		pid1 = g.index( (i,j) )
		pid2 = g.index( (i + 1,j) )
		sp = LinearSpring3D(pid1,pid2,E,l0,S)
		sps.append(sp)

#end create springs
############################################
#
print "create damper"
#
############################################
#begin create damper
from openalea.mechanics import ViscousDamper3D

damp = ViscousDamper3D(tuple(g),damping)

#end create damper
############################################
#
print "create pressure"
#
############################################
#begin create pressure
from openalea.mechanics import PressureTriangle

ps = []
for i in range(NB - 1) :
	for j in range(NB - 1) :
		act = PressureTriangle(g.index( (i,j) ),
		                       g.index( (i,j + 1) ),
		                       g.index( (i + 1,j + 1) ),
		                       P)
		
		ps.append(act)
		
		act = PressureTriangle(g.index( (i,j) ),
		                       g.index( (i + 1,j + 1) ),
		                       g.index( (i + 1,j) ),
		                       P)
		
		ps.append(act)

#end create pressure
###################################################
#
print "energy"
#
###################################################
#begin energy
def W (t, state) :
	return sum(sp.energy(state,t) for sp in sps)

#end energy
###################################################
#
print "gradient of energy"
#
###################################################
#begin gradient of energy
actors = sps + [damp] + ps

def compute_forces (t, state) :
	forces = zeros( (len(g),3) )
	for actor in actors :
		actor.assign_forces(forces,state,t)
	
	#boundary conditions
	for i in (0,NB - 1) :
		for j in range(NB) :
			forces[g.index( (i,j) ),:] = 0.
	
	for i in range(NB) :
		for j in (0,NB - 1) :
			forces[g.index( (i,j) ),:] = 0.
	
	return forces

#end gradient of energy
###################################################
#
print "system evolution function"
#
###################################################
#begin evolution
from numpy import array

def evolution (t, state) :
	state = state.reshape( (2,len(g),3) )
	
	forces = compute_forces(t,state)
	return array([state[1,...],forces / m]).flatten()

#end evolution
###################################################
#
print "jacobian"
#
###################################################
#begin jacobian
def jacobian (t, state) :
	state = state.reshape( (2,len(g),2) )
	jac = zeros( (2,len(g),2,2,len(g),2) )
	
	#actors
	for actor in actors :
		actor.assign_jacobian(jac,state,t)
	
	jac[1,::] /= m
	
	#position
	for pid in g :
		for i in range(2) :
			jac[0,pid,i,1,pid,i] = 1.
	
	#boundary conditions
	jac[:,0,1,::] = 0. #left bottom point forbidden to move along Oy
	jac[:,NB - 1,1,::] = 0. #right bottom point forbidden to move along Oy
	jac[:,NB / 2,0,::] = 0. #top most point forbidden to move along Ox
	
	jac[:,:,:,:,0,1] = 0. #state of the system do not depend on the y
	                      #components of left bottom point
	jac[:,:,:,:,NB - 1,1] = 0. #state of the system do not depend on the y
	                      #components of right bottom point
	jac[:,:,:,:,NB / 2,0] = 0. #state of the system do not depend on the x
	                      #components of top most point
	
	return jac.reshape( (2 * len(g) * 2,2 * len(g) * 2) )

#end jacobian
###################################################
#
print "compute evolution"
#
###################################################
#begin compute evolution
from sys import stdout
from scipy.integrate import ode
from time import time

r = ode(evolution)#,jacobian)
r.set_integrator('vode', method = 'bdf', with_jacobian = False)
r.set_initial_value(state0.flatten(),t0)

nb_steps = 100
res = zeros( (nb_steps,2,len(g),3) )
res[0,::] = state0
W_list = [W(t0,state0)]
F_list = [compute_forces(t0,state0).max()]
t_list = [t0]

tinit = time()
for i in xrange(1,nb_steps) :
	print i,
	stdout.flush()
	state = r.integrate(r.t + dt).reshape( (2,len(g),3) )
	res[i,::] = state
	W_list.append(W(r.t,state) )
	F_list.append(compute_forces(r.t,state).max() )
	t_list.append(r.t)
	print F_list[-1],state[1,:,:].max()

print "\nend of computation",time() - tinit

#end compute evolution
###################################################
#
print "display final strain"
#
###################################################
#begin display final strain
from pylab import *

fig = figure()
hist([sp.strain(state) for sp in sps])
fig.savefig("result_strain.png")
show()
close(fig)

#end display final strain
###################################################
#
print "display final state"
#
###################################################
#begin display final state
from vplants.plantgl.scenegraph import Polyline,Material,Shape
from openalea.pglviewer import SceneView,display

sc = SceneView()

mat = Material( (0,0,0) )

for sp in sps :
	geom = Polyline([state[0,pid,:] for pid in sp.extremities()])
	sc.add(Shape(geom,mat) )

display(sc)

#end display final state
