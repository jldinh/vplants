# -*- python -*-
#
#       simulation.diffusion reaction: example simulation package to perform
#										integration of differential equations
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
cfg = f.read_config("config")
pos,descr = f.read("position")
f.close()

pos = dict( (pid,Vector2(*tup)) for pid,tup in pos.iteritems() )
mesh = t.relation(cfg.mesh_id)
###################################################
#
print "physiology"
#
###################################################
from openalea.physics.chemistry import Reaction,GraphDiffusion

IAA = dict( (cid,0.) for cid in mesh.wisps(2) ) #(mol.m-3) concentration in IAA in each cell

#reaction
alpha = dict( (cid,0.1) for cid in mesh.wisps(2) ) #(mol.m-3.s-1) creation of IAA in each cell
beta = dict( (cid,0.1) for cid in mesh.wisps(2) ) #(s-1) destruction of IAA in each cell

reaction_algo = Reaction(alpha,beta)

#diffusion
graph_id = t.add_relation("graph",(cfg.cell,cfg.wall)) #create a topological relation between cells
graph = t.relation(graph_id)
for wid in mesh.wisps(1) :
	if mesh.nb_regions(1,wid) == 2 :
		cid1,cid2 = mesh.regions(1,wid)
		graph.add_edge(cid1,cid2,wid)

V = dict( (vid,1.) for vid in graph.vertices() ) #(m3) volume of the cells
D = dict( (eid,1.) for eid in graph.edges() ) #(m.s-1) diffusion constant of the walls

diffusion_algo = GraphDiffusion(graph,V,D)
###################################################
#
print "GUI"
#
###################################################
from simu_view import SimuView
from simu_gui import SimuGUI

sc = SimuView(vars())
gui = SimuGUI(sc)

###################################################
#
print "processes"
#
###################################################
def reinit (*args) :
	for cid in mesh.wisps(2) :
		IAA[cid] = 0.
	sc.redraw()

def reaction (time, dt) :
	reaction_algo.react(IAA,dt)

def diffusion (time, dt) :
	diffusion_algo.react(IAA,dt)

def boundary (*args) :
	for cid in cfg.sources :
		IAA[cid] = 1.
	for cid in cfg.sinks :
		IAA[cid] = 0.

def display (*args) :
	sc.redraw()

###################################################
#
#	simulation loop
#
###################################################
from openalea.pglviewer import QApplication,Viewer
from openalea.pglviewer.data import InfiniteSimu,InfiniteSimuGUI

simu = InfiniteSimu(0.,0.1)
simu.set_initialisation(reinit)
simu.add_process(reaction,"reaction")
simu.add_process(diffusion,"diffusion")
simu.add_process(boundary,"boundary")
simu.add_process(display,"display")

qapp = QApplication([])
v = Viewer()
v.set_world(sc)
v.set_loop(simu)
v.add_gui(InfiniteSimuGUI(simu))
v.add_gui(gui)
v.show()
v.set_2D()
qapp.exec_()


