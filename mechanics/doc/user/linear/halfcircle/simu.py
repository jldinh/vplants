###################################################
#
print "parameters"
#
###################################################
#begin parameters
from numpy import zeros
from math import pi,sin,cos

NB = 101 #(None) #number of points
m = 1. #(kg) #mass of points
E = 1e3 #(N.m-2) #Young's modulus
l0 = 1. #(m) #ref length
depth = 1. #(m) #depth of the surface
thickness = 0.01 #(m) #thickness of the surface
P = 0.01 #(Pa) #pressure inside

R = l0 * (NB - 1) / pi #(m) #radius of the circle
S = depth * thickness #(m2) #cross section of a spring

damping = 0.3 #(N.m-1.s) #damping coefficient

state0 = zeros( (2,NB,2) )
for i in range(NB) :
	state0[0,i,0] = R * cos(pi - pi * i / (NB - 1.) )
	state0[0,i,1] = R * sin(pi - pi * i / (NB - 1.) )

t0 = 0. #(s) #starting time of the simulation
dt = 1e0 #(s) #time step to look at the evolution of the system

#end parameters
############################################
#
print "create springs"
#
############################################
#begin create springs
from openalea.mechanics import LinearSpring2D

sps = [LinearSpring2D(i,i + 1,E,l0,S) for i in range(NB - 1)]

#end create springs
############################################
#
print "create damper"
#
############################################
#begin create damper
from openalea.mechanics import ViscousDamper2D

damp = ViscousDamper2D(tuple(range(NB) ),damping)

#end create damper
############################################
#
print "create pressure"
#
############################################
#begin create pressure
from openalea.mechanics import PressureSegment

ps = [PressureSegment(i,i+1,P,depth) for i in range(NB - 1)]

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
	forces = zeros( (NB,2) )
	for actor in actors :
		actor.assign_forces(forces,state,t)
	
	#boundary conditions
	forces[0,1] = 0. #left bottom point move horizontaly
	forces[NB - 1,1] = 0. #right bottom point move horizontaly
	forces[NB / 2,0] = 0. #top most point move vertically
	
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
	state = state.reshape( (2,NB,2) )
	
	forces = compute_forces(t,state)
	return array([state[1,::],forces / m]).flatten()

#end evolution
###################################################
#
print "jacobian"
#
###################################################
#begin jacobian
def jacobian (t, state) :
	state = state.reshape( (2,NB,2) )
	jac = zeros( (2,NB,2,2,NB,2) )
	
	#actors
	for actor in actors :
		actor.assign_jacobian(jac,state,t)
	
	jac[1,::] /= m
	
	#position
	for pid in range(NB) :
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
	
	return jac.reshape( (2 * NB * 2,2 * NB * 2) )

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

r = ode(evolution,jacobian)
r.set_integrator('vode', method = 'bdf', with_jacobian = True)
r.set_initial_value(state0.flatten(),t0)

nb_steps = 1000
res = zeros( (nb_steps,2,NB,2) )
res[0,::] = state0
W_list = [W(t0,state0)]
F_list = [compute_forces(t0,state0).max()]
t_list = [t0]

tinit = time()
for i in xrange(1,nb_steps) :
	print i,
	stdout.flush()
	state = r.integrate(r.t + dt).reshape( (2,NB,2) )
	res[i,::] = state
	W_list.append(W(r.t,state) )
	F_list.append(compute_forces(r.t,state).max() )
	t_list.append(r.t)

print "\nend of computation",time() - tinit

#end compute evolution
###################################################
#
print "analytical result"
#
###################################################
#begin analytical result
from math import exp
from scipy.optimize import fsolve

a = P * R / (E * thickness)

def func (dr) :
	return exp(a * dr) - dr

Rf = R * fsolve(func,1.)

stress_ana = P * Rf / thickness
strain_ana = stress_ana / E

#end analytical result
###################################################
#
print "plot evolution"
#
###################################################
#begin plot evolution
from pylab import *

fig = figure()
for pid in (0,NB / 4,NB / 2,NB - 1) :
	plot(t_list[:300],
	     [norm(res[i,0,pid,:]) / Rf - 1. for i in range(300)],
	     label = 'dr%d' % pid)

axhline(y = 0.,dashes = [2,2],color = 'k')

plot(t_list[:300],
     F_list[:300],
     label = "Fmax in N",
     color='b',lw=1.5)

xlabel("time in s")
legend(loc = 'upper right',ncol = 2)
fig.savefig("result_evolution.png")
show()
close(fig)

#end plot evolution
###################################################
#
print "plot energy"
#
###################################################
#begin plot energy

fig = figure()
plot(t_list[:300],W_list[:300],label = "W in J",color='b',lw=1.5)

xlabel("time in s")
ylabel("W in J")
fig.savefig("result_energy.png")
show()
close(fig)

#end plot energy
###################################################
#
print "plot strain"
#
###################################################
#begin plot strain

fig = figure()
for step in (300,400,500,600,700,800,900,999) :
	plot([(sp.strain(res[step,::]) - strain_ana) / strain_ana * 1e5 for sp in sps],
	      label = "t = %d" % (step * dt) )

axhline(y = 0,dashes = [2,2],color = 'k')

ylabel("strain relative error x1e5 (None)")
legend(loc = 'upper center', ncol = 2)

fig.savefig("result_strain.png")
show()
close(fig)

#end plot strain
###################################################
#
print "plot stress"
#
###################################################
#begin plot stress

fig = figure()
plot([(sp.stress(state) - stress_ana) / stress_ana * 1e5 for sp in sps])
axhline(y = 0,dashes = [2,2],color = 'k')

ylabel("stress relative error x1e5 (None)")

fig.savefig("result_stress.png")
show()
close(fig)

#end plot strain
###################################################
#
print "plot final state"
#
###################################################
#begin plot final state

fig = figure()
plot(state[0,:,0],state[0,:,1])

fig.savefig("result_final_state.png")
show()
close(fig)

#end plot final state

