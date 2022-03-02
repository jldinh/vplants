############################################
#
print "read mesh"
#
############################################
#begin read mesh
from numpy import array
from numpy.linalg import norm
from openalea.container import read_topomesh

mesh,descr,props = read_topomesh("sphere.msh")

p = dict(props[0])

pos = dict( (pid,array([p['X'][pid],p['Y'][pid],p['Z'][pid]]) ) \
             for pid in mesh.wisps(0) )

#renormalize to R
R = 1. #(m) #radius of the sphere

for pid,vec in pos.iteritems() :
	pos[pid] = vec * (R / norm(vec) )

#ensure ids are consecutive starting from 0
NB = len(pos)

assert len(pos) == (max(pos.iterkeys() ) + 1)

#end read mesh
###################################################
#
print "parameters"
#
###################################################
#begin parameters
from numpy import zeros

m = 1. #(kg) #mass of each point
S = 0.01 #(m2) #section of each linear spring
E = 1e3 #(N.m-2) #Young's modulus

damping = 0.3 #(N.m-1.s) #damping coefficient

P = 10. #(Pa) #Pressure inside the sphere

state0 = zeros( (2,len(pos),3) ) #initial state of the system
for pid,vec in pos.iteritems() :
	state0[0,pid,:] = vec

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

sps = []
for eid in mesh.wisps(1) :
	pid0,pid1 = mesh.borders(1,eid)
	l0 = norm(pos[pid1] - pos[pid0])
	sp = LinearSpring3D(pid0,pid1,E,l0,S)
	sps.append(sp)

#end create springs
############################################
#
print "create damper"
#
############################################
#begin create damper
from openalea.mechanics import ViscousDamper3D

damp = ViscousDamper3D(tuple(mesh.wisps(0) ),damping)

#end create damper
############################################
#
print "create pressure actors"
#
############################################
#begin create pressure
from numpy import dot,cross
from openalea.mechanics import PressureTriangle

ps = []
for fid in mesh.wisps(2) :
	pid1,pid2,pid3 = mesh.borders(2,fid,2)
	if dot( (pos[pid1] + pos[pid2] + pos[pid3]) / 3.,
	       cross(pos[pid2] - pos[pid1],pos[pid3] - pos[pid1]) ) > 0 :
		ps.append(PressureTriangle(pid1,pid2,pid3,P) )
	else :
		ps.append(PressureTriangle(pid1,pid3,pid2,P) )

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
from scipy import zeros

actors = sps + [damp] + ps

def compute_forces (t, state) :
	forces = zeros( (NB,3) )
	for actor in actors :
		actor.assign_forces(forces,state,t)
	
	#boundary conditions
	forces[0,:] = 0. #bottom point attached to the ground
	forces[11,0] = 0.
	forces[11,1] = 0. #top point allowed to move according to Oz only
	
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
	return array([state[1,...],forces / m]).flatten()

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
	jac[:,11,0,::] = 0.
	jac[:,11,1,::] = 0.
	
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

nb_steps = 200
res = zeros( (nb_steps,len(pos),3) )
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
#begin plot
from pylab import figure,close,plot,show,legend,axhline,xlabel

sph_center = [res[i,::].sum(0) / NB for i in range(nb_steps)]

fig = figure()
for pid in (0,11,25,30,22,27) :
	plot(t_list,
	     [norm(res[i,pid,:] - sph_center[i]) - R for i in xrange(nb_steps)],
	     label = 'dx%.2d in m' % pid)

plot(t_list,F_list,label = "F in N",color='b',lw=1.5)

axhline(y = 0,dashes = [2,2])
xlabel("time in s")
legend(loc = 'upper right')
fig.savefig("result.png")
show()
close(fig)

#end plot
###################################################
#
print "display final state"
#
###################################################
#begin display final state
from vplants.plantgl.scenegraph import Material
from openalea.tissueview import MeshView
from openalea.pglviewer import display

#initial state
for pid in pos :
	pos[pid] = res[0,pid,:]

imv = MeshView(mesh,pos,2,0,Material( (0,155,0) ) )
imv.redraw()

#final state
for pid in pos :
	pos[pid] = res[-1,pid,:]

mv = MeshView(mesh,pos,1,0,Material( (0,0,0) ) )
mv.redraw()

mv.merge(imv)

display(mv,gui = False)

#end display final state

