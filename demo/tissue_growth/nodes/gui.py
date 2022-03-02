###################################################
#
#	info
#
###################################################
from openalea.tissueshape import edge_length,face_surface_2D
from openalea.physics.mechanics import LinearSpring2D

def get_cell_info (cid, param) :
	#cell volume
	print "cell volume: ",face_surface_2D(param.mesh,param.pos,cid)
	#morphogen concentration
	print "morphogen: ",param.morphogen[cid]
	#cell age
	print "cell age: ",param.cell_age[cid]
	#reaction
	print "reaction, alpha: ",param.alpha[cid]," beta: ",param.beta[cid]
	#turgor
	print "turgor: ",param.turgor[cid]
	#gamma
	print "gamma: ",param.gamma[cid]

def get_wall_info (wid, param) :
	#wall length
	print "wall length: ",edge_length(param.mesh,param.pos,wid)
	#wall diffusivity
	if param.graph.has_edge(wid) :
		print "wall diffusivity: ",param.D[wid]
	#wall meca
	print "meca l0: ",param.l0[wid]," K: ",param.K[wid]
	pid1,pid2 = param.mesh.borders(1,wid)
	spring = LinearSpring2D(pid1,pid2,0.,param.l0[wid])
	strain = spring.strain(param.pos)
	print "strain",strain

###################################################
#
#	GUI
#
###################################################
from simu_view import SimuView
from simu_gui import SimuGUI

def create_gui (param) :
	sc = SimuView(param)
	gui = SimuGUI(sc)
	return sc,gui

def redraw_process (sc) :
	def process (time, dt) :
		sc.redraw()
	return (process,"redraw"),
###################################################
#
#	simulation loop
#
###################################################
from openalea.pglviewer import QApplication,Viewer
from openalea.pglviewer.data import InfiniteSimu,InfiniteSimuGUI

def init_simulation (sc) :
	def func() :
		sc.redraw()
	return func,

def create_simulation (param, init_func, process_list) :
	simu = InfiniteSimu(0.,0.1)
	simu.set_initialisation(init_func)
	for process,name in process_list :
		simu.add_process(process,name)
	return simu,

def launch_gui (sc, gui, simu, param) :
	def cell_info (cid) :
		get_cell_info(cid,param)
	def wall_info (wid) :
		get_wall_info(wid,param)
	v = Viewer(vars())
	v.set_world(sc)
	v.set_loop(simu)
	v.add_gui(InfiniteSimuGUI(simu))
	v.add_gui(gui)
	v.show()
	v.set_2D()


