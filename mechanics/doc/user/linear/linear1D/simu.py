###################################################
#
print "parameters"
#
###################################################
#begin parameters
from numpy import array

NB = 5 #number of masses
m = 1. #(kg) #mass of each point
S1 = 0.01 #(m2) #section of thin linear springs
S2 = 0.02 #(m2) #section of wide linear springs
E = 1e3 #(N.m-2) #Young's modulus

damping = 0.3 #(N.m-1.s) #damping coefficient

F = 10. #(N) #External load applied on the system

state0 = [[(0.,0,0),(2.,0,0),(4.,0,0),(5.,0,0),(6.,0,0)],
          [(0.,0,0),(0.,0,0),(0.,0,0),(0.,0,0),(0.,0,0)]]

state0 = array(state0)

t0 = 0. #(s) #starting time of the simulation
dt = 1e-1 #(s) #time step to look at the evolution of the system

#end parameters
############################################
#
print "create springs"
#
############################################
#begin create springs
from openalea.mechanics import LinearSpring3D

sps = [LinearSpring3D(0,1,E,2.,S2),
       LinearSpring3D(1,2,E,2.,S1),
       LinearSpring3D(2,3,E,1.,S2),
       LinearSpring3D(3,4,E,1.,S1),]

#end create springs
############################################
#
print "create damper"
#
############################################
#begin create damper
from openalea.mechanics import ViscousDamper3D

damp = ViscousDamper3D(tuple(range(NB) ),damping)

#end create damper
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
from scipy import zeros

actors = sps + [damp]

def compute_forces (t, state) :
	forces = zeros( (NB,3) )
	for actor in actors :
		actor.assign_forces(forces,state,t)
	
	#boundary conditions
	forces[0,:] = 0. #bottom point attached to the ground
	forces[4,0] += F #apply load
	
	forces[:,1] = 0. #points allowed to move according to Ox only
	forces[:,2] = 0. #points allowed to move according to Ox only
	
	return forces

#end gradient of energy
###################################################
#
print "system evolution function"
#
###################################################
#begin evolution
def evolution (t, state) :
	state = state.reshape( (2,NB,3) )
	
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
	state = state.reshape( (2,NB,3) )
	jac = zeros( (2,NB,3,2,NB,3) )
	
	#actors
	for actor in actors :
		actor.assign_jacobian(jac,state,t)
	
	jac[1,::] /= m
	
	#position
	for pid in range(NB) :
		for i in range(3) :
			jac[0,pid,i,1,pid,i] = 1.
	
	#boundary conditions
	jac[:,0,::] = 0.
	
	jac[:,:,1,::] = 0. #points forbidden to move along Oy
	jac[:,:,2,::] = 0. #points forbidden to move along Oz
	jac[:,:,:,:,:,1] = 0. #state of the system do not depend on y
	jac[:,:,:,:,:,2] = 0. #state of the system do not depend on z
	
	return jac.reshape( (2 * NB * 3,2 * NB * 3) )

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
res = zeros( (nb_steps,NB,3) )
res[0,::] = state0[0]
W_list = [W(t0,state0)]
F_list = [compute_forces(t0,state0).max()]
t_list = [t0]

tinit = time()
for i in xrange(1,nb_steps) :
	print i,
	stdout.flush()
	state = r.integrate(r.t + dt).reshape( (2,NB,3) )
	res[i,::] = state[0]
	W_list.append(W(r.t,state) )
	F_list.append(compute_forces(r.t,state).max() )
	t_list.append(r.t)

print "\nend of computation",time() - tinit

#end compute evolution
###################################################
#
print "plot evolution"
#
###################################################
#begin plot evolution
from pylab import *

fig = figure()
for pid in range(NB) :
	plot(t_list,
	     res[:,pid,0],
	     label = 'x%d in m' % pid)

plot(t_list,F_list,label = "Fmax in N",color='b',lw=1.5)

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
from pylab import *

fig = figure()
plot(t_list,W_list,label = "W in J",color='b',lw=1.5)

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
bar( (0,1,2,2.6),
     [sp.strain(state) for sp in sps],
     width = (0.8,0.8,0.4,0.4),
     color = ('r','r','b','b') )

axhline(y = 0.5,dashes = [2,2],color = 'k')
axhline(y = 1.,dashes = [2,2],color = 'k')

ylim(0.,1.5)
ylabel("strain (None)")

xlim(-0.2,3.2)
xticks((0.4,1.4,2.2,2.8), ('S0', 'S1', 'S2', 'S3') )

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
bar( (0,1,2,2.6),
     [sp.stress(state) for sp in sps],
     width = (0.8,0.8,0.4,0.4),
     color = ('r','r','b','b') )

axhline(y = 500,dashes = [2,2],color = 'k')
axhline(y = 1000,dashes = [2,2],color = 'k')

ylim(0.,1500.)
ylabel("stress (Pa)")

xlim(-0.2,3.2)
xticks((0.4,1.4,2.2,2.8), ('S0', 'S1', 'S2', 'S3') )

fig.savefig("result_stress.png")
show()
close(fig)

#end plot strain

