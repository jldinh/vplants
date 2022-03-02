################################################
#
print "parameters"
#
################################################
#begin parameters
R = 1. #(m) #radius of the sphere
thickness = 0.01 #(m) #thickness of the membrane

E = 1e10 #(Pa) #Young's modulus
nu = 0. #(None) #Poisson's ratio

P = 1e6 #(Pa) #pressure applied from inside the sphere

m = 1. #(kg) #mass of points
damping = 1e4 #(N.m-1.s) #damping coefficient

t0 = 0. #(s) #starting time of the simulation
dt = 1e-3 #(s) #time step hint to find equilibrium
Fmax = 1e-3 #(N) #force threshold below which points are considered not moving

#end parameters
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
################################################
#
print "create springs"
#
################################################
#begin create springs
from numpy import zeros
from openalea.mechanics import triangle_frame,\
          isotropic_material2D,TriangleMembrane3D

mat = isotropic_material2D(E,nu)

spring = {}
for fid in mesh.wisps(2) :
	pids = tuple(mesh.borders(2,fid,2) )
	pts = tuple(pos[pid] for pid in pids)
	fr = triangle_frame(*pts)
	
	ref_shape = array([fr.local_point(pt)[:2] for pt in pts])
	
	spring[fid] = TriangleMembrane3D(pids,mat,ref_shape,thickness)

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

turg = {}
for fid in mesh.wisps(2) :
	pid1,pid2,pid3 = mesh.borders(2,fid,2)
	if dot( (pos[pid1] + pos[pid2] + pos[pid3]) / 3.,
	       cross(pos[pid2] - pos[pid1],pos[pid3] - pos[pid1]) ) > 0 :
		turg[fid] = PressureTriangle(pid1,pid2,pid3,P)
	else :
		turg[fid] = PressureTriangle(pid1,pid3,pid2,P)

#end create pressure
###################################################
#
print "gradient of energy"
#
###################################################
#begin gradient of energy
from scipy import zeros

actors = spring.values() + [damp] + turg.values()

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
################################################
#
print "find equilibrium"
#
################################################
#begin find equilibrium
from scipy.integrate import ode
from time import time

state0 = array([[pos[pid] for pid in range(NB)],
               zeros( (NB,3) )])

r = ode(evolution)
r.set_integrator('vode', method = 'bdf', with_jacobian = False)
r.set_initial_value(state0.flatten(),t0)

tinit = time()
while compute_forces(r.t,r.y.reshape( (2,NB,3) ) ).max() > Fmax :
	r.integrate(r.t + dt)
	print compute_forces(r.t,r.y.reshape( (2,NB,3) ) ).max()

print "\nend of computation",time() - tinit

#end find equilibrium
################################################
#
print "equilibrium state"
#
################################################
#begin equilibrium state
from numpy import add

state_equ = r.y.reshape( (2,NB,3) )

#end equilibrium state

from pickle import dump
dump(state_equ,open("equ.pkl",'w') )

from pickle import load
state_equ = load(open("equ.pkl",'rb') )

###################################################
#
print "display final state"
#
###################################################
#begin display final state
from numpy import zeros
from numpy.linalg import eig
from vplants.plantgl.scenegraph import Material
from openalea.tissueview import MeshView,TensorialPropView
from openalea.pglviewer import display

#initial state
for pid in pos :
	pos[pid] = state0[0,pid,:]

imv = MeshView(mesh,pos,2,10,Material( (0,0,100) ) )
imv.redraw()

#strain
for pid in pos :
	pos[pid] = state_equ[0,pid,:]

stvec = {}
v = zeros( (3,2) )

for fid,sp in spring.iteritems() :
	fr = sp.local_frame(state_equ)
	w,v[:2,:] = eig(sp.strain(state_equ) )
	
	stvec[fid] = [fr.global_vec(v[:,i]) * w[i] for i in (0,1)]

stv = TensorialPropView(mesh,pos,2,stvec,20.)
stv.redraw()

#final state
for pid in pos :
	pos[pid] = state0[0,pid,:] + (state_equ[0,pid,:] - state0[0,pid,:]) * 20

mv = MeshView(mesh,pos,1,0,Material( (0,0,0) ) )
mv.redraw()

mv.merge(imv)
mv.merge(stv)

display(mv,gui = False)

#end display final state
###################################################
#
print "strain distribution"
#
###################################################
#begin strain distribution
from pylab import figure,close,hist,show,legend,axhline,xlabel

fig = figure()
hist([sp.strain(state_equ).trace() for sp in spring.itervalues()])
fig.savefig("strain_dist.png")
show()
close(fig)

#end strain distribution

