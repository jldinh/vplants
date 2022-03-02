#===============================================================================
# 
print "open tissue"
#
#===============================================================================
from openalea.celltissue import TissueDB
from openalea.tissueshape import tovec

db = TissueDB()
db.read("tissue.zip")

STEM = db.get_property("pattern_STEM")
L1 = db.get_property("pattern_L1")
pos = tovec(db.get_property("position"),centered = True)
mesh = db.get_topology("mesh_id")

#===============================================================================
# 
print "repressor model"
#
#===============================================================================
from openalea.wusmodel import Parameters,RepressorModel

Y1 = dict( (cid,0.) for cid in mesh.wisps(3) )
Y2 = dict( (cid,0.) for cid in mesh.wisps(3) )
WUS = dict( (cid,0.) for cid in mesh.wisps(3) )

p = Parameters()

algo = None
modified = True

def physio () :
	global algo,modified
	if modified :
		algo = RepressorModel(mesh,pos,p,L1,STEM)
		modified = False
	algo.react(Y1,Y2,WUS,10.)

#===============================================================================
# 
print "draw"
#
#===============================================================================
from vplants.plantgl.scenegraph import Shape,Material,Translated,Scaled
from vplants.plantgl.ext.color import JetMap
from openalea.pglviewer import SceneView
from openalea.tissueshape import centroid
from openalea.tissueview import cell_geom,ScalarPropView

prop = {}

cmap = JetMap(0.,1.,outside_values = True)
sc = ScalarPropView(mesh,pos,3,prop,10,cmap)
sc.redraw()
sc.cache_geometry()

#===============================================================================
# 
print "compute"
#
#===============================================================================
from openalea.scheduler import Scheduler,Task

def redraw () :
	prop.update(WUS)
	sc.redraw()

sch = Scheduler()
sch.register(Task(physio,1,10,"physio") )
sch.register(Task(redraw,10,0,"redraw") )

#===============================================================================
# 
print "display"
#
#===============================================================================
from openalea.pglviewer import QApplication,Viewer,Vec,Quaternion
from openalea.pglviewer import ClippingProbeView,ClippingProbeGUI,\
                               TemplateGUI,LoopView,LoopGUI
from openalea.container import clean_remove

def displayY1 () :
	prop.update(Y1)
	sc.redraw()

def displayY2 () :
	prop.update(Y2)
	sc.redraw()

def displayWUS () :
	prop.update(WUS)
	sc.redraw()

displayWUS()

loop = LoopView(sch)

bb = sc.bounding_box()
pb = ClippingProbeView(sc,size = max(bb.getSize() ) * 1.5 )
pb.set_visible(False)

def kill (elmid) :
	global modified
	if elmid is not None :
		if mesh.has_wisp(3,elmid) :
			cid = elmid
			#properties
			prop[cid] = None
			del Y1[cid]
			del Y2[cid]
			del WUS[cid]
			L1.pop(cid,None)
			STEM.pop(cid,None)
			pids = tuple(mesh.borders(3,cid,3) )
			clean_remove(mesh,3,cid)
			for pid in pids :
				if not mesh.has_wisp(0,pid) :
					del pos[pid]
			
			modified = True
			redraw()

def set_L1 (elmid) :
	global modified
	if elmid is not None :
		if mesh.has_wisp(3,elmid) :
			cid = elmid
			STEM.pop(cid,None)
			L1[cid] = 1.
			modified = True

gui = TemplateGUI("display")
gui.add_action_descr("Y1",displayY1)
gui.add_action_descr("Y2",displayY2)
gui.add_action_descr("WUS",displayWUS)

gui.add_tool_descr("kill",kill,pb.selection_draw)
gui.add_tool_descr("defL1",set_L1,pb.selection_draw)

qapp = QApplication([])
v = Viewer()
#cam=v.view().camera()
#cam.setPosition(Vec(102.063,-43.2236,41.9204))
#cam.setOrientation(Quaternion(0.448465,0.349287,0.400549,0.718637))
#pb.setPosition(Vec(1.10563,2.11675,-2.0438))
#pb.setOrientation(Quaternion(-0.0259682,0.658813,-0.00453761,0.751845))
v.set_world(pb)
pb.activate(v.view(),True)

v.add_gui(LoopGUI(loop) )
v.add_gui(ClippingProbeGUI(pb) )
v.add_gui(gui)

v.show()
v.view().show_entire_world()
qapp.exec_()
