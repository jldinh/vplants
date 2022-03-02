###################################################
#
print "parameters"
#
###################################################
R = 1. #(m) #radius of the sphere
m = 1. #(kg) #mass of each point
thickness = 0.01 #(m) #thickness of the membrane
E = 1e3 #(N.m-2) #Young's modulus
nu = 0. #(None) #Poisson ratio

damping = 0.3 #(N.m-1.s) #damping coefficient

P = 0.5 #(N) #force acting on each point to simulate pressure

############################################
#
print "read mesh"
#
############################################
from numpy import array
from numpy.linalg import norm
from openalea.container import read_topomesh

mesh,descr,props = read_topomesh("sphere.msh")

p = dict(props[0])

pos = dict( (pid,array([p['X'][pid],p['Y'][pid],p['Z'][pid]]) ) for pid in mesh.wisps(0) )

for pid,vec in pos.iteritems() :
	pos[pid] = vec * (R / norm(vec) )

#ensure ids are consecutive starting from 0
NB = len(pos)

assert len(pos) == (max(pos.iterkeys() ) + 1)

############################################
#
print "create springs"
#
############################################
from openalea.mechanics import (triangle_frame,
                                isotropic_material2D,TriangleMembrane3D)

mat = isotropic_material2D(E,nu)

sps = []
for fid in mesh.wisps(2) :
	pids = tuple(mesh.borders(2,fid,2) )
	fr = triangle_frame(*tuple(pos[pid] for pid in pids) )
	ref_shp = dict( (pid,fr.local_point(pos[pid]) ) for pid in pids)
	
	sp = TriangleMembrane3D(pids,mat,ref_shp,thickness)
	sps.append(sp)

############################################
#
print "create damper"
#
############################################
from openalea.mechanics import ViscousDamper3D

damp = ViscousDamper3D(tuple(mesh.wisps(0) ),damping)

############################################
#
print "pressure forces"
#
############################################
PF = dict( (pid,vec * (P / norm(vec) ) ) for pid,vec in pos.iteritems() )

###################################################
#
print "energy"
#
###################################################
def W (t, state) :
	return sum(sp.scipy_energy(t,state) for sp in sps)

###################################################
#
print "gradient"
#
###################################################
from scipy import zeros

def compute_forces (t, state) :
	forces = zeros( (NB,3) )
	for sp in sps :
		sp.scipy_forces(t,state,forces)
	
	damp.scipy_forces(t,state,forces)
	
	for pid,F in PF.iteritems() :
		forces[pid,:] += F
	
	#boundary conditions
	forces[25,:] = 0.
	forces[30,0] = 0.
	forces[30,2] = 0.
	
	return forces

def grad (t, state) :
	state = state.reshape( (2,NB,3) )
	forces = compute_forces(t,state)
	
	return array([state[1,::],forces / m]).flatten()

###################################################
#
print "jacobian"
#
###################################################
def jacobian (t, state) :
	state = state.reshape( (2,NB,3) )
	jac = zeros( (2,NB,3,2,NB,3) )
	
	for sp in sps :
		sp.scipy_jacobian(t,state,jac)
	
	damp.scipy_jacobian(t,state,jac)
	
	for pid in range(NB) :
		for i in range(3) :
			jac[0,pid,i,1,pid,i] = 1.
			jac[1,pid,i,0,pid,i] /= m
			jac[1,pid,i,1,pid,i] /= m
	
	return jac.reshape( (2 * NB * 3,2 * NB * 3) )

###################################################
#
print "compute evolution"
#
###################################################
from sys import stdout
from scipy.integrate import ode
from time import time

state0 = zeros( (2,len(pos),3) )
for pid,vec in pos.iteritems() :
	state0[0,pid,:] = vec * 1.

t0 = 0.
dt = 1e0

r = ode(grad)
r.set_integrator('vode', method = 'bdf', with_jacobian = False)
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

print "end of computation",time() - tinit

###################################################
#
print "plot evolution"
#
###################################################
from pylab import figure,close,plot,show,legend,axhline,xlabel

fig = figure()
for pid in pos.keys()[:10] :
	plot(t_list,
	     [norm(res[i,pid,:]) - R for i in xrange(nb_steps)],
	     label = 'dx%.2d in m' % pid)

plot(t_list,F_list,label = "F in N")

axhline(y = 0,dashes = [2,2])
xlabel("time in s")
legend(loc = 'upper right')
fig.savefig("result_pressure.png")
show()
close(fig)

###################################################
#
print "display result"
#
###################################################
from vplants.plantgl.scenegraph import Material
from openalea.tissueview import MeshView
from openalea.pglviewer import display

for pid in pos :
	pos[pid] = res[-1,pid,:]

mv = MeshView(mesh,pos,1,0,Material( (0,0,0) ) )
mv.redraw()

display(mv)
