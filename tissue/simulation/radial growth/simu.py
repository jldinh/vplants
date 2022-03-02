# -*- python -*-
#
#       simulation.global growth: example simulation package of global growth field
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
#	read tissue and properties
#
###################################################
from vplants.plantgl.math import Vector2
from openalea.celltissue import topen

f = topen("tissue.zip",'r')
t,descr = f.read()
pos,descr = f.read("position")
cell_age,descr = f.read("cell_age")
cfg = f.read_config("config")
f.close()

pos = dict( (pid,Vector2(*tup)) for pid,tup in pos.iteritems() )
mesh = t.relation(cfg.mesh_id)
###################################################
#
#	cell division
#
###################################################
from openalea.tissueshape import main_axis_2D,divide_segment_2D

def divide_cell (cid, shrink_factor) :
	"""
	divide a cell according to its main axis
	"""
	bary,axis = main_axis_2D(mesh,pos,cid)
	#create daughter cells
	daughter = [mesh.add_wisp(2) for i in xrange(2)]
	for did in daughter :#update cell property
		cell_age[did] = 0.
	#compute side of points
	point_side = {}
	for pid in mesh.borders(2,cid,2) :
		val = ( pos[pid] - bary ) * axis
		if val > 0 :
			point_side[pid] = 1
		else :
			point_side[pid] = 0
	#compute side of walls
	border_points = {}
	for wid in list(mesh.borders(2,cid)) :
		wall_side = set(point_side[pid] for pid in mesh.borders(1,wid))
		if len(wall_side) == 1 :
			side, = wall_side
			mesh.link(2,daughter[side],wid)
		else : #need to divide wall
			pid0, = (pid for pid in mesh.borders(1,wid) if point_side[pid]==0)
			pid1, = (pid for pid in mesh.borders(1,wid) if point_side[pid]==1)
			#mid point
			mid_pid = mesh.add_wisp(0)
			#pos[mid_pid] = (pos[pid0] + pos[pid1]) / 2.
			pos[mid_pid] = divide_segment_2D(pos[pid0],pos[pid1],axis,bary)
			border_points[mid_pid] = (mesh.nb_regions(1,wid) == 1) #property used later to create the new separation wall
																   #and shrink the size of this new wall
			#first half wall
			wid0 = mesh.add_wisp(1)
			mesh.link(1,wid0,pid0)
			mesh.link(1,wid0,mid_pid)
			for rid in mesh.regions(1,wid) :
				mesh.link(2,rid,wid0)
			mesh.link(2,daughter[0],wid0)
			#second half wall
			wid1 = mesh.add_wisp(1)
			mesh.link(1,wid1,pid1)
			mesh.link(1,wid1,mid_pid)
			for rid in mesh.regions(1,wid) :
				mesh.link(2,rid,wid1)
			mesh.link(2,daughter[1],wid1)
			#remove old wall
			t.remove_element(wid)
	#remove old cell
	t.remove_element(cid)
	del cell_age[cid]#update cell property
	#create border
	wid = mesh.add_wisp(1)
	for pid in border_points :
		mesh.link(1,wid,pid)
	for cid in daughter :
		mesh.link(2,cid,wid)
	#shrink border
	pid1,pid2 = border_points
	mid = (pos[pid1] + pos[pid2])/2.
	for pid,is_border in border_points.iteritems() :
		if not is_border :
			pos[pid] = mid + ( pos[pid] - mid ) * shrink_factor
###################################################
#
#	GUI
#
###################################################
from simu_view import SimuView
from simu_gui import SimuGUI

sc = SimuView(vars())
gui = SimuGUI(sc)

###################################################
#
#	processes
#
###################################################
from openalea.tissueshape import face_surface_2D
expand_center = Vector2()
expand_speed = 0.1 #(mum.s-1)
Vmax = 1.
shrink_factor = 0.7

def expand (time, dt) :
	for pid,vec in pos.iteritems() :
		pos[pid] = vec + (vec - expand_center) * (expand_speed*dt)

def divide (*args) :
	for cid in list(mesh.wisps(2)) :
		V = face_surface_2D(mesh,pos,cid)
		if V > Vmax :
			divide_cell(cid,shrink_factor)

def update_age (time, dt) :
	for cid,age in cell_age.iteritems() :
		cell_age[cid] = age + dt

def redraw (*args) :
	sc.redraw()
###################################################
#
#	simulation loop
#
###################################################
from openalea.pglviewer import QApplication,Viewer
from openalea.pglviewer.data import InfiniteSimu,InfiniteSimuGUI

simu = InfiniteSimu(0.,0.1)
simu.add_process(expand,"expand")
simu.add_process(divide,"divide")
simu.add_process(update_age,"update_age")
simu.add_process(redraw,"redraw")

qapp = QApplication([])
v = Viewer(vars())
v.set_world(sc)
v.set_loop(simu)
v.add_gui(InfiniteSimuGUI(simu))
v.add_gui(gui)
v.show()
v.set_2D()
qapp.exec_()


