################################################
#
print "parameters"
#
################################################
#begin parameters
from numpy import array

NB = 6 #(None) #number of points on the border
R = 1. #(m) #radius of the shape
thickness = 0.01 #(m) #thickness of the membrane

axis = array( (0,1) ) #orientation of fibers
E1 = 100e9 #(Pa) #Young's modulus along fibers
E2 = 10e9 #(Pa) #Young's modulus perpendicular to fibers
nu1 = 0. #(None) #Poisson's ratio
G12 = 20e9 #(Pa) #Shear modulus

F = 1e6 #(N) #force applied on each side

m = 1. #(kg) #mass of points
damping = 1e4 #(N.m-1.s) #damping coefficient

t0 = 0. #(s) #starting time of the simulation
dt = 1e-3 #(s) #time step hint to find equilibrium
Fmax = 1e-7 #(N) #force threshold below which points are considered not moving

#end parameters
################################################
#
print "create mesh"
#
################################################
#begin create mesh
from math import radians,sin,cos
from numpy import array
from openalea.container import Topomesh

#create mesh
mesh = Topomesh(2)
pos = {}

#create points
for i in range(NB) :
	pid = mesh.add_wisp(0,i)
	pos[pid] = array([R * cos(radians(30 + i * 60) ),
	                   R * sin(radians(30 + i * 60) ),
	                   0])

#create edges
for i,(pid1,pid2) in enumerate([(0,1),(1,2),(2,3),
                                (3,4),(4,5),(5,0),
                                (0,3),(0,2),(3,5)]) :
	eid = mesh.add_wisp(1,i)
	mesh.link(1,eid,pid1)
	mesh.link(1,eid,pid2)

#create faces
for eid1,eid2,eid3 in [(0,1,7),(2,6,7),(5,6,8),(3,4,8)] :
	fid = mesh.add_wisp(2)
	mesh.link(2,fid,eid1)
	mesh.link(2,fid,eid2)
	mesh.link(2,fid,eid3)

#end create mesh
################################################
#
print "create mechanical representation"
#
################################################
#begin create mechanical representation
from numpy import zeros
from numpy.linalg import norm
from openalea.mechanics import (triangle_frame,
          axis_material2D,TriangleMembrane3D)

mat = axis_material2D(axis,E1,E2,nu1,G12)

spring = {}
for fid in mesh.wisps(2) :
	pids = tuple(mesh.borders(2,fid,2) )
	pts = tuple(pos[pid] for pid in pids)
	fr = triangle_frame(*pts)
	
	ref_shape = array([fr.local_point(pt)[:2] for pt in pts])
	
	lmat = fr.local_tensor2(mat)
	
	sp = TriangleMembrane3D(pids,
	                        lmat,
	                        ref_shape,
	                        thickness)
	
	spring[fid] = sp

#compute external load
external_load = dict( (pid,pos[pid] * (F / norm(pos[pid]) ) ) \
                       for pid in mesh.wisps(0) )

#end create mechanical representation
############################################
#
print "create damper"
#
############################################
#begin create damper
from openalea.mechanics import ViscousDamper3D

damp = ViscousDamper3D(tuple(mesh.wisps(0) ),damping)

#end create damper
###################################################
#
print "gradient of energy"
#
###################################################
#begin gradient of energy
from scipy import zeros

actors = spring.values() + [damp]

def compute_forces (t, state) :
	forces = zeros( (NB,3) )
	for actor in actors :
		actor.assign_forces(forces,state,t)
	
	#boundary conditions
	for pid,load in external_load.iteritems() :
		forces[pid,:] += load
	
	forces[4,:] = 0. #bottom point fixed
	forces[1,0] = 0. #top point constraint to move according to Oy only
	
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

strain = {}
for fid,sp in spring.iteritems() :
	fr = triangle_frame(*tuple(state0[0,pid,:] for pid in sp.extremities() ) )
	strain[fid] = fr.global_tensor2(sp.strain(state_equ) )

print "mean strain",reduce(add,strain.values() ) / len(strain)

#end equilibrium state
###################################################
#
print "draw equilibrium state"
#
###################################################
#begin draw equilibrium state
from openalea.svgdraw import (display,save_png,
                              SVGScene,SVGLayer,
                              SVGSphere,
                              SVGPath,SVGText)

sca = 200.
size = 2.5 * sca
fontsize = 24
fw = 10.5 / 2.
fh = 16.3 / 2.

def svg_pos (vec) :
	return size / 2. + vec[0] * sca,\
	       size / 2. - vec[1] * sca

sc = SVGScene(size,size)

#draw frame
frame_lay = SVGLayer("frame",size,size,"layer0")
sc.append(frame_lay)

elm = SVGPath("Ox")
elm.move_to(10,size - 10)
elm.line_to(10 + sca,size - 10)
elm.set_fill(None)
elm.set_stroke( (255,0,0) )
elm.set_stroke_width(3)
frame_lay.append(elm)

elm = SVGPath("Oxhead")
elm.move_to(sca,size - 15)
elm.line_to(10 + sca,size - 10)
elm.line_to(sca,size - 5)
elm.set_fill(None)
elm.set_stroke( (255,0,0) )
elm.set_stroke_width(3)
frame_lay.append(elm)

elm = SVGText(20 + sca - fw,size - 10 + fh,"x",fontsize,"xaxis")
elm.set_fill( (255,0,0) )
frame_lay.append(elm)

elm = SVGPath("Oy")
elm.move_to(10,size - 10)
elm.line_to(10,size - 10 - sca)
elm.set_fill(None)
elm.set_stroke( (0,255,0) )
elm.set_stroke_width(3)
frame_lay.append(elm)

elm = SVGPath("Oyhead")
elm.move_to(5,size - sca)
elm.line_to(10,size - 10 - sca)
elm.line_to(15,size - sca)
elm.set_fill(None)
elm.set_stroke( (0,255,0) )
elm.set_stroke_width(3)
frame_lay.append(elm)

elm = SVGText(10 - fw,size - 30 - sca + fh,"y",fontsize,"yaxis")
elm.set_fill( (0,255,0) )
frame_lay.append(elm)

#draw reference state
lay = SVGLayer("ref",size,size,"layer1")
sc.append(lay)

for eid in mesh.wisps(1) :
	pt1,pt2 = (state0[0,pid,:] for pid in mesh.borders(1,eid) )
	elm = SVGPath("edge%.4d" % eid)
	elm.move_to(*svg_pos(pt1) )
	elm.line_to(*svg_pos(pt2) )
	elm.set_fill(None)
	elm.set_stroke( (0,0,0) )
	elm.set_stroke_width(2)
	lay.append(elm)

for pid in range(NB) :
	x,y = svg_pos(state0[0,pid,:])
	elm = SVGSphere(x,y,4,4,"point%.4d" % pid)
	elm.set_fill( (0,0,0) )
	lay.append(elm)

#draw equilibrium state
lay = SVGLayer("act",size,size,"layer2")
sc.append(lay)

for eid in mesh.wisps(1) :
	pt1,pt2 = (state0[0,pid,:] - (state0[0,pid,:] - state_equ[0,pid,:]) * 30 \
	           for pid in mesh.borders(1,eid) )
	elm = SVGPath("edge%.4d" % eid)
	elm.move_to(*svg_pos(pt1) )
	elm.line_to(*svg_pos(pt2) )
	elm.set_fill(None)
	elm.set_stroke( (0,0,255) )
	elm.set_stroke_width(2)
	lay.append(elm)

for pid in range(NB) :
	x,y = svg_pos(state0[0,pid,:] - (state0[0,pid,:] - state_equ[0,pid,:]) * 30)
	elm = SVGSphere(x,y,4,4,"point%.4d" % pid)
	elm.set_fill( (0,0,0) )
	lay.append(elm)

display(sc,"final state")

#end draw equilibrium state
save_png("equilibrium.png",sc)

###################################################
#
print "draw equilibrium strain"
#
###################################################
#begin draw equilibrium strain
from numpy.linalg import eig

sc = SVGScene(size,size)

#draw frame
sc.append(frame_lay)

#draw reference state
lay = SVGLayer("ref",size,size,"layer1")
sc.append(lay)

for eid in mesh.wisps(1) :
	pt1,pt2 = (state0[0,pid,:] for pid in mesh.borders(1,eid) )
	elm = SVGPath("edge%.4d" % eid)
	elm.move_to(*svg_pos(pt1) )
	elm.line_to(*svg_pos(pt2) )
	elm.set_fill(None)
	elm.set_stroke( (0,0,0) )
	elm.set_stroke_width(2)
	lay.append(elm)

for pid in range(NB) :
	x,y = svg_pos(state0[0,pid,:])
	elm = SVGSphere(x,y,4,4,"point%.4d" % pid)
	elm.set_fill( (0,0,0) )
	lay.append(elm)

#draw strain
lay = SVGLayer("strain",size,size,"layer2")
sc.append(lay)

for fid in mesh.wisps(2) :
	pt1,pt2,pt3 = (state0[0,pid,:] for pid in mesh.borders(2,fid,2) )
	cent = ( (pt1 + pt2 + pt3) / 3.)[:2]
	
	w,v = eig(strain[fid])
	v1 = v[:,0] * w[0]
	v2 = v[:,1] * w[1]
	
	elm = SVGPath("face%.4dV1" % fid)
	elm.move_to(*svg_pos(cent - v1 * 30) )
	elm.line_to(*svg_pos(cent + v1 * 30) )
	elm.set_fill(None)
	elm.set_stroke( (255,0,0) )
	elm.set_stroke_width(2)
	lay.append(elm)
	
	elm = SVGPath("face%.4dV2" % fid)
	elm.move_to(*svg_pos(cent - v2 * 30) )
	elm.line_to(*svg_pos(cent + v2 * 30) )
	elm.set_fill(None)
	elm.set_stroke( (0,255,0) )
	elm.set_stroke_width(2)
	lay.append(elm)

display(sc,"final strain")

#end draw equilibrium strain
save_png("strain.png",sc)

