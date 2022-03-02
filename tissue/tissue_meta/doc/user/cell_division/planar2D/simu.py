################################################
#
print "open tissue"
#
################################################
#begin open tissue
from openalea.celltissue import TissueDB
from openalea.tissueshape import tovec

db = TissueDB()
db.read("coleochaete.zip")
t = db.tissue()

assert len(tuple(t.relations() ) ) == 1

mesh = db.get_topology("mesh_id")
pos = tovec(db.get_property("position") )

#center tissue
bary = reduce(lambda x,y: x + y,pos.itervalues() ) / len(pos)
pos = dict( (pid,vec - bary) for pid,vec in pos.iteritems() )

#end open tissue
################################################
#
print "add properties"
#
################################################
#begin add properties
from random import random

prop = dict( (cid,random() ) for cid in mesh.wisps(2) )

#end add properties
################################################
#
print "division algo"
#
################################################
#begin division algo
from openalea.tissueshape import centroid,divide_face

def is_internal_point (pid) :
	for eid in mesh.regions(0,pid) :
		if mesh.nb_regions(1,eid) == 1 :
			return False
	return True

def cell_division (cid, point, normal, shrink) :
	#perform division
	lineage = divide_face(mesh,pos,cid,point,normal)
	
	#shrink newly formed separation wall
	sca = (100 - shrink) / 100.
	wid, = lineage[1][None]
	bary = centroid(mesh,pos,1,wid)
	for pid in mesh.borders(1,wid) :
		if is_internal_point(pid) :
			pos[pid] = bary + (pos[pid] - bary) * sca
	
	#update properties
	val = prop.pop(cid)
	for did in lineage[2][cid] :
		prop[did] = val

#end division algo
################################################
#
print "find division plane"
#
################################################
#begin find division plane
from math import radians,sin,cos
from numpy import array,dot
from numpy.linalg import norm
from openalea.tissueshape import face_main_axes_2D,face_surface_2D
from openalea.container import clone_mesh,ordered_pids

def find_division_plane (cid,
                         main_axis_weight,
                         smallest_wall_weight,
                         perp_wall_weight,
                         daughter_size_weight) :
	#normalize weights
	tot = float(main_axis_weight \
	          + smallest_wall_weight \
	          + perp_wall_weight \
	          + daughter_size_weight)
	main_axis_weight /= tot
	smallest_wall_weight /= tot
	perp_wall_weight /= tot
	daughter_size_weight /= tot
	
	#find main axis
	bary,main_axis,main_axis2 = face_main_axes_2D(mesh,pos,cid)
	
	wall_length = []
	wall_normal = []
	daughter_size = []
	for angle in xrange(0,180) :
		axis = array([cos(radians(angle) ),sin(radians(angle) )])
		cmesh = clone_mesh(mesh,[cid])
		cpos = dict( (pid,pos[pid]) for pid in cmesh.wisps(0) )
		
		#fake division
		lineage = divide_face(cmesh,cpos,cid,bary,axis)
		
		#wall length
		wid, = lineage[1][None]
		pid1,pid2 = cmesh.borders(1,wid)
		separation_dir = cpos[pid2] - cpos[pid1]
		sep_length = norm(separation_dir)
		wall_length.append( (sep_length,angle) )
		
		#wall perpendicularity
		separation_dir /= sep_length
		perp = 0.
		extr = set( (pid1,pid2) )
		for pid in extr :
			pid1,pid2 = set(cmesh.region_neighbors(0,pid) ) - extr
			seg = cpos[pid2] - cpos[pid1]
			perp += dot(separation_dir,seg / norm(seg) )
		wall_normal.append( (perp / 2.,angle) )
		
		#daughter size
		S1,S2 = (face_surface_2D(cmesh,cpos,did) \
		         for did in lineage[2][cid])
		daughter_size.append( (abs(S2 - S1) / (S1 + S2),angle) )
	
	wall_length.sort()
	angle = wall_length[0][1]
	wall_length_axis = array([cos(radians(angle) ),sin(radians(angle) )])
	
	wall_normal.sort()
	angle = wall_normal[0][1]
	wall_normal_axis = array([cos(radians(angle) ),sin(radians(angle) )])
	
	daughter_size.sort()
	angle = daughter_size[0][1]
	daughter_size_axis = array([cos(radians(angle) ),sin(radians(angle) )])
	
	#linear combination
	return bary,main_axis * main_axis_weight \
	          + wall_length_axis * smallest_wall_weight \
	          + wall_normal_axis * perp_wall_weight \
	          + daughter_size_axis * daughter_size_weight

#end find division plane
################################################
#
print "display tissue"
#
################################################
#begin display tissue
from vplants.plantgl.scenegraph import Material
from vplants.plantgl.ext.color import JetMap
from openalea.tissueview import MeshView2D,ScalarPropView

cmap = JetMap(0.,1.)
wall_mat = Material( (0,0,0) )

prop_sc = ScalarPropView(mesh,pos,2,prop,0,cmap)
wall_sc = MeshView2D(mesh,pos,1,0,wall_mat,1)

prop_sc.redraw()
wall_sc.redraw()

#end display tissue
################################################
#
print "retrieve parameters"
#
################################################
#begin retrieve parameters
def retrieve_parameters () :
	ui = param_widget
	
	shrink = ui.shrinkSlider.value()
	maw = ui.mainAxisSlider.value()
	sww = ui.smallWallSlider.value()
	pww = ui.perpendicularSlider.value()
	dsw = ui.daughtersSizeSlider.value()
	
	return shrink,maw,sww,pww,dsw

#end retrieve parameters
################################################
#
print "define actions"
#
################################################
#begin define actions
from random import shuffle

def divide_all () :
	#get parameters
	shrink,maw,sww,pww,dsw = retrieve_parameters()
	
	#walk randomly through each cell
	cells = list(mesh.wisps(2) )
	shuffle(cells)
	
	for cid in cells :
		point,axis = find_division_plane(cid,maw,sww,pww,dsw)
		cell_division(cid,point,axis,shrink)
	
	#redraw
	prop_sc.redraw()
	wall_sc.redraw()

#end define actions
################################################
#
print "define tools"
#
################################################
#begin define tools
def divide_single_cell (cid) :
	print cid
	if cid is not None :
		#get parameters
		shrink,maw,sww,pww,dsw = retrieve_parameters()
	
		#perform division
		point,axis = find_division_plane(cid,maw,sww,pww,dsw)
		cell_division(cid,point,axis,shrink)
		
		#redraw
		prop_sc.redraw()
		wall_sc.redraw()

#end define tools
################################################
#
print "launch GUI"
#
################################################
#begin launch GUI
from PyQt4.QtCore import QObject,SIGNAL
from PyQt4.uic import loadUi
from openalea.pglviewer import QApplication,Viewer,\
                               TemplateGUI,View3DGUI

qapp = QApplication([])

param_widget = loadUi("simu.ui")

gui = TemplateGUI("division")
gui.add_action_descr("divide all",divide_all)
gui.add_tool_descr("divide cell",divide_single_cell,prop_sc.selection_draw)

v = Viewer()
v.add_world(prop_sc)
v.add_world(wall_sc)

v.add_gui(gui)
v.add_gui(View3DGUI() )

v.show()
v.view().set_dimension(2)

param_widget.show()

QObject.connect(v,
                SIGNAL("close"),
                param_widget.close)

qapp.exec_()




