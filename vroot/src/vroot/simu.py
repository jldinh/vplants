from random import random
from openalea.plantgl.math import Vector3
from openalea.pglviewer import QApplication,Viewer,Vec
from openalea.pglviewer.data import SceneView,SceneGUI,WorldView,WorldGUI,LandscapeView,LandscapeGUI,\
				RangeSimu,RangeSimuGUI,\
				InfiniteSimu,InfiniteSimuGUI

from display import RootGUI,Root2DView
from root import Root
from simu_process import constraint_auxin,react_auxin,diffuse_auxin,diffuse_wall_auxin,transport_auxin,react_pumps,canalize_auxin,orient_flux
from simu_params import *

r=Root()
r.read("totod")
#r.read("totosmall")

root_center=sum(r.position.itervalues(),Vector3())/len(r.position)

rv=Root2DView(r)
rv.frame().translate(Vec(-root_center[0],-root_center[1],0))
rv.wall_thickness_min=2.
rv.wall_thickness_max=10.
#rv.display_base_cells(False)
#rv.display_pumps(True)

endoderm = [128,130,132,134,136,137,141,142,143,144,147,149,151,153,154,156,159,160,161,163,165,166,169,171,173,175,176,234,233,231,229,227,225,223,222,218,217,215,213,212,211,208,207,206,205,199,198,197,196,195,189,188,184,183,182]
endoedges = []
epiderm = [91,92,93,94,95,96,97,98,99,100,101,102,103,104,105,106,107,108,109,110,111,112,113,114,115,116,117,118,119,120,121,122,123,124,59,60,61,62,63,64,65,66,67,68,69,70,71,72,73,74,75,76,77,78,79,80]
epidedges = []
cortex = [178,179,180,181,185,186,187,190,191,192,193,194,200,201,202,203,204,209,210,214,216,219,220,221,224,226,228,230,232,127,129,131,133,135,138,139,140,145,146,148,150,152,155,157,158,162,164,167,168,170,172,174]
cortedges = []
cap = [44,17,16,21,85,45,15,14,13,84,48,46,1,12,83,49,0,2,11,82,50,47]
capedges = []
elongzone = [113,114,115,116,117,118,119,120,121,122,123,124,72,73,74,75,76,77,78,79,80]
QC = [87,88]
meristem = [87,88,82,83,84,85,81,86,89,288,240,239,235,126,125]


def display (time, dt) :
	rv.redraw()

pump_init=dict(r.relative_pumps)

def pre_init () :
	for wid in r.walls() :
		r.cells_of_wall[wid] = r.associated_cells(wid)
	for cid in r.cells() :
		r.walls_of_cell[cid] = r.associated_walls(cid)
	for cell in endoderm :
		for wall in r.walls_of_cell[cell]:
			endoedges.append(wall)
	for cell in epiderm :
		for wall in r.walls_of_cell[cell]:
			epidedges.append(wall)
	for cell in cortex :
		for wall in r.walls_of_cell[cell]:
			cortedges.append(wall)
	for cell in cap :
		for wall in r.walls_of_cell[cell]:
			capedges.append(wall)

test_autoorg = 1

def init () :
	#initiate cell auxin contempt and production/degradation
	for cid in r.cells() :
		r.auxin[cid]=base_auxin_level
		r.auxin_creation[cid]=base_auxin_creation
		r.auxin_degradation[cid]=base_auxin_degradation#+random()/10.
		if test_autoorg:
			if (cid in elongzone):# or (cid in meristem):
				r.auxin_degradation[cid] = 0.5
	
	#initate wall auxin contempt
	for wid in r.walls() :
		r.auxin[wid]= 0.
		if (wid == 382):
			r.auxin[wid] = 100.
	
	#change some diffusion properties of endoderm wall
	graph=r.diffusion_graph()
	for eid in graph.edges() :
		if eid in endoedges :
			r.diffusion_coeff[eid]= global_diffusion_coeff*r.wall_surface[eid]
		else :
			r.diffusion_coeff[eid]=global_diffusion_coeff*r.wall_surface[eid]
	
	#initiate pumps comptemp and production/degradation
	for pid in r.pumps() :
		r.pump_creation[pid]=base_pump_creation
		r.pump_degradation[pid]=base_pump_degradation
		if pump_init[pid]<0.5 :
			r.relative_pumps[pid]= 0.0 #0.01
		else :
			r.relative_pumps[pid]= pump_init[pid]

	#trans = r.transport_graph()
	#for pid in trans.out_edges(6):
	#	r.relative_pumps[pid] = 1.
	#for pid in r.pumps() :
	#	r.relative_pumps[pid]= 0

	r.fixed_concentration.clear()
	r.fixed_flux.clear()
	display(0,0)

def constraint(time, dt) :
	constraint_auxin(r,time,dt)

def reaction(time, dt) :
	react_auxin(r,time,dt)

def diffusion (time, dt) :
	diffuse_auxin(r,time,dt)

def wall_diffusion (time, dt) :
	diffuse_wall_auxin(r,time,dt)

def transport (time, dt) :
	transport_auxin(r,time,dt)

def recycle_pumps (time, dt) :
	react_pumps(r,time,dt)

def canalize (time, dt) :
	canalize_auxin(r,time,dt)

def gravistimulus (time,dt) :
	orient_flux(r,time,dt)


snapshot_index=[0]
def snapshot (time, dt) :
    v.view().saveSnapshot("formovies/step%.4d.png" % snapshot_index[0])
    snapshot_index[0]+=1

pre_init()
init()

#simu=RangeSimu([i*dt for i in xrange(int(1000/dt))])
simu=InfiniteSimu(0.,dt)
simu.set_initialisation(init)
#simu.add_process(gravistimulus,"gravistimulus")
simu.add_process(reaction,"reaction")
simu.add_process(diffusion,"diffusion")
#simu.add_process(wall_diffusion,"wall diffusion")
simu.add_process(transport,"transport")
simu.add_process(recycle_pumps,"pumps recycling")
simu.add_process(canalize,"canalize auxin")
simu.add_process(constraint,"constraint")
#simu.add_process(snapshot,"snapshot")

simu.add_process(display,"display")

land1=LandscapeView()
land1.set_size(1000.)
land1.set_background( (255,255,255) )
land2=LandscapeView()
land2.set_size(1000.)
land2.set_background( (255,0,0) )

world=WorldView()

qapp=QApplication([])
v=Viewer(locals())
v.view().setSnapshotFormat("png")
v.set_world(world)
v.set_loop(simu)

#v.add_gui(RangeSimuGUI(simu))
v.add_gui(InfiniteSimuGUI(simu))

gui=WorldGUI(world)
v.add_gui(gui)

ind=gui.add(RootGUI(rv))
gui.set_current_element(ind)
ind=gui.add_land(LandscapeGUI(land1))
gui.add_land(LandscapeGUI(land2))
gui.element().set_current_land(ind)

v.show()
#v.showMaximized()
v.set_2D()
qapp.exec_()
