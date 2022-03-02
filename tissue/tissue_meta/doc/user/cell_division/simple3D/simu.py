###############################################
#
print "read tissue"
#
###############################################
#begin read tissue
from openalea.celltissue import TissueDB
from openalea.tissueshape import tovec

db = TissueDB()
db.read("tissue.zip")
t = db.tissue()

assert len(tuple(t.relations() ) ) == 1

mesh = db.get_topology("mesh_id")
pos = tovec(db.get_property("position") )

#center tissue
bary = reduce(lambda x,y: x + y,pos.itervalues() ) / len(pos)
pos = dict( (pid,vec - bary) for pid,vec in pos.iteritems() )

#end read tissue
###############################################
#
print "add property"
#
###############################################
#begin add property
from random import random

prop = dict( (cid,random() ) for cid in mesh.wisps(3) )

#end add property
###############################################
#
print "division algo"
#
###############################################
#begin division algo
from openalea.tissueshape import centroid,divide_cell

def is_internal_point (pid) :
	for eid in mesh.regions(0,pid) :
		for fid in mesh.regions(1,eid) :
			if mesh.nb_regions(2,fid) == 1 :
				return False
	return True

def is_external_edge (eid) :
	for fid in mesh.regions(1,eid) :
		if mesh.nb_regions(2,fid) == 1 :
			return True
	return False

def cell_division (cid, point, normal, shrink) :
	#perform division
	lineage = divide_cell(mesh,pos,cid,point,normal)
	
	#shrink newly formed separation wall
	sca = (100 - shrink) / 100.
	wid, = lineage[2][None]
	bary = centroid(mesh,pos,2,wid)
	for pid in mesh.borders(2,wid,2) :
		if is_internal_point(pid) :
			pos[pid] = bary + (pos[pid] - bary) * sca
	
	for eid in mesh.borders(2,wid) :
		if is_external_edge(eid) :
			bary = centroid(mesh,pos,1,eid)
			for pid in mesh.borders(1,eid) :
				pos[pid] = bary + (pos[pid] - bary) * sca
	
	#update properties
	val = prop.pop(cid)
	for did in lineage[3][cid] :
		prop[did] = val

#end division algo
###############################################
#
print "division plane"
#
###############################################
#begin division plane
from openalea.tissueshape import cell_main_axes

def find_division_plane (cid) :
	bary,V1,V2,V3 = cell_main_axes(mesh,pos,cid)
	
	return bary,V1

#end division plane
###############################################
#
print "display tissue"
#
###############################################
#begin display tissue
from vplants.plantgl.scenegraph import Material
from vplants.plantgl.ext.color import JetMap
from openalea.tissueview import MeshView,ScalarPropView

cmap = JetMap(0.,1.)
wall_mat = Material( (0,0,0) )

prop_sc = ScalarPropView(mesh,pos,3,prop,10,cmap)
wall_sc = MeshView(mesh,pos,2,20,wall_mat)

prop_sc.redraw(send_signal = False)
wall_sc.redraw()
#end display tissue
###############################################
#
print "retrieve parameters"
#
###############################################
#begin retrieve parameters
def retrieve_parameters () :
	ui = param_widget
	
	shrink = ui.shrinkSlider.value()
	
	return shrink

#end retrieve parameters
###############################################
#
print "define action"
#
###############################################
#begin define action
from random import shuffle

def divide_all () :
	#get parameters
	shrink = retrieve_parameters()
	
	#walk randomly through each cell
	cells = list(mesh.wisps(3) )
	shuffle(cells)
	
	for cid in cells :
		print "divide",cid
		point,axis = find_division_plane(cid)
		cell_division(cid,point,axis,shrink)
	
	#redraw
	prop_sc.redraw(send_signal = False)
	wall_sc.redraw()

#end define action
###############################################
#
print "define tool"
#
###############################################
#begin define tool
def divide_single_cell (cid) :
	if cid is not None and mesh.has_wisp(3,cid) :
		print "divide",cid
		#get parameters
		shrink = retrieve_parameters()
	
		#perform division
		point,axis = find_division_plane(cid)
		cell_division(cid,point,axis,shrink)
		
		#redraw
		prop_sc.redraw(send_signal = False)
		wall_sc.redraw()

#end define tool
###############################################
#
print "launch simu"
#
###############################################
#begin launch simu
from PyQt4.QtCore import QObject,SIGNAL
from PyQt4.uic import loadUi
from openalea.pglviewer import QApplication,Viewer,\
                               TemplateGUI,View3DGUI,\
                               ClippingProbeView,ClippingProbeGUI

pb = ClippingProbeView(size = 70)
pb.add_world(prop_sc)
pb.add_world(wall_sc)

qapp = QApplication([])

param_widget = loadUi("simu.ui")

gui = TemplateGUI("division")
#gui.add_action_descr("divide all",divide_all)
gui.add_tool_descr("divide cell",divide_single_cell,pb.selection_draw)

v = Viewer()
v.add_world(pb)

v.add_gui(gui)
v.add_gui(View3DGUI() )
v.add_gui(ClippingProbeGUI(pb) )

v.show()
v.view().show_entire_world()

param_widget.show()

QObject.connect(v,
                SIGNAL("close"),
                param_widget.close)

qapp.exec_()

#end launch simu






