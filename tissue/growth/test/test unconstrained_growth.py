#################################
#
print "create tissue"
#
#################################
from openalea.container import Topomesh
from vplants.plantgl.math import Vector3

mesh = Topomesh(2)
pos = {}

#points
for pid,vec in enumerate([(0,0,0),
                          (0,0,1),
                          (0,0,2),
                          (1,0,2),
                          (-0.5,0.5,2),
                          (-0.5,-0.5,2),
                          (1,0,3)]) :
	mesh.add_wisp(0,pid)
	pos[pid] = Vector3(*vec)

#cells
for cid,pids in enumerate([(0,1),(1,2),
                           (1,3),(1,4),(1,5),
                           (3,6)]) :
	mesh.add_wisp(1,cid)
	for pid in pids :
		mesh.link(1,cid,pid)

#################################
#
print "growth algo"
#
#################################
from random import random
from openalea.growth import Unconstrained

G = dict( (cid,random() * 0.1) for cid in mesh.wisps(1) )
dt_growth = 0.1
algo = Unconstrained(mesh,0,G)

def grow () :
	algo.grow(pos,dt_growth)

#################################
#
print "draw"
#
#################################
from vplants.plantgl.scenegraph import Material
from openalea.tissueview import MeshView

mv = MeshView(mesh,pos,1,0,Material( (0,0,0) ) )
mv.set_line_width(3)

def redraw () :
	mv.redraw()

#################################
#
print "scheduler"
#
#################################
from openalea.scheduler import Scheduler,Task

sch = Scheduler()
sch.register(Task(grow,1,1,"grow") )
sch.register(Task(redraw,1,0,"redraw") )

#################################
#
print "launch"
#
#################################
from openalea.pglviewer import QApplication,Viewer, \
                               LoopView,LoopGUI

loop = LoopView(sch)
redraw()

qapp = QApplication([])
v = Viewer()
v.set_world(mv)
v.add_gui(LoopGUI(loop) )

v.show()
v.view().show_entire_world()

qapp.exec_()

















