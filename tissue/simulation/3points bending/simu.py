# -*- python -*-
#
#       simulation.3points bending: example simulation package for mass spring systems
#
#       Copyright 2006 INRIA - CIRAD - INRA  
#
#       File author(s): Jerome Chopard <jerome.chopard@sophia.inria.fr>
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
# 
#       OpenAlea WebSite : http://openalea.gforge.inria.fr
#

__doc__="""
This module launch the simulation
"""

__license__= "Cecill-C"
__revision__=" $Id: $ "

###################################################
#
print "read tissue and properties"
#
###################################################
from vplants.plantgl.math import Vector2
from openalea.celltissue import topen

f = topen("tissue.zip",'r')
t,descr = f.read()
pos,descr = f.read("position")
cfg = f.read_config("config")
f.close()

mesh = t.relation(cfg.mesh_id)
pos = dict( (pid,Vector2(*tup)) for pid,tup in pos.iteritems() )
###################################################
#
print "mechanics"
#
###################################################
from math import cos,pi
from openalea.tissueshape import edge_length
from openalea.physics.mechanics import LinearSpring2D,CircularSpring2D,ForwardEuler2D
#mecha constants
K = 20. #unit
L = 1. #unit
current_load = 0. #N
dt_meca = 0.1 #s

#find bottom fixed point
nb = len(cfg.bottom_points)
fixed_points = (cfg.bottom_points[nb/5],cfg.bottom_points[nb - 1 - nb/5])

#compute the fraction of load distributed in each top_point
top_center = sum((pos[pid] for pid in cfg.top_points),Vector2())/len(cfg.top_points)
load_extension = top_center.x/4.
load_fraction = {}
for pid in cfg.top_points :
	d = pos[pid].x - top_center.x
	if abs(d) >= load_extension :
		load_fraction[pid] = 0.
	else :
		load_fraction[pid] = cos(pi/2.*d/load_extension)

#compute springs
weight = dict( (pid,1.) for pid in mesh.wisps(0) )
springs = []

#linear springs along edges
for eid in mesh.wisps(1) :
	pid1,pid2 = mesh.borders(1,eid)
	l = edge_length(mesh,pos,eid)
	spring = LinearSpring2D(pid1,pid2,K,l)
	springs.append(spring)

#circular springs between each pair of edges
#around a point
for pid in mesh.wisps(0) :
	neighbors = list(mesh.region_neighbors(0,pid))
	nb = len(neighbors)
	for i in xrange(nb) :
		pid1 = neighbors[i]
		pid2 = neighbors[(i+1)%nb]
		ref_angle = CircularSpring2D(pid,pid1,pid2,L,0.).angle(pos) #used only to compute the angle between two edges
		spring = CircularSpring2D(pid,pid1,pid2,L,ref_angle)
		springs.append(spring)
		
#bound function
def load (pid) :
	return load_fraction[pid] * current_load

def bound (solver) :
	for pid in fixed_points :
		solver.set_force(pid,0.,0.)
	for pid in cfg.top_points :
		solver.set_force(pid,solver.fx(pid),solver.fy(pid) - load(pid))

#meca solver
algo = ForwardEuler2D(weight,springs,bound)

def meca_equilibrium () :
 	algo.deform(pos,dt_meca,1000)
###################################################
#
print "geometric deformation"
#
###################################################
#compute the deformation of the tissue in the middle
mid_top_point = cfg.top_points[len(cfg.top_points)/2]
mid_bottom_point = cfg.bottom_points[len(cfg.bottom_points)/2]
ref_alt = pos[mid_top_point].y

def deformation () :
	return ref_alt - pos[mid_top_point].y

def geom_width () :
	return pos[mid_top_point].y - pos[mid_bottom_point].y
###################################################
#
print "GUI"
#
###################################################
from openalea.pglviewer import QApplication
qapp = QApplication([])
from simu_view import SimuView
from simu_gui import SimuGUI

sc = SimuView(vars())
gui = SimuGUI(sc)

###################################################
#
print "processes"
#
###################################################
from math import exp
tau = 10 #s, time constant for reaching max load

def change_load (time, dt) :
	global current_load
	current_load = 1.* (1 - exp(-time/tau))

def meca (time, dt) :
	meca_equilibrium()

def display (time, dt) :
	sc.redraw()

def update_deformation (time, dt) :
	sc.update_info(time)
###################################################
#
#	simulation loop
#
###################################################
from openalea.pglviewer import Viewer
from openalea.pglviewer.data import InfiniteSimu,InfiniteSimuGUI

simu = InfiniteSimu(0.,1.)
simu.add_process(change_load,"load")
simu.add_process(meca,"meca")
simu.add_process(update_deformation,"deformation")
simu.add_process(display,"display")

v = Viewer(vars())
v.set_world(sc)
v.set_loop(simu)
v.add_gui(InfiniteSimuGUI(simu))
v.add_gui(gui)
v.show()
v.set_2D()
qapp.exec_()


