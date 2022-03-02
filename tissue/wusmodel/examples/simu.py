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
pos = tovec(db.get_property("position") )
mesh = db.get_topology("mesh_id")

bary = reduce(lambda x,y : x + y,pos.itervalues() ) / len(pos)
pos = dict( (pid,vec - bary) for pid,vec in pos.iteritems() )

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

algo = RepressorModel(mesh,pos,p,L1,STEM)

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

#===============================================================================
# 
print "compute"
#
#===============================================================================
from openalea.scheduler import Scheduler,Task

def physio () :
	algo.react(Y1,Y2,WUS,10.)

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

gui = TemplateGUI("display")
gui.add_action_descr("Y1",displayY1)
gui.add_action_descr("Y2",displayY2)
gui.add_action_descr("WUS",displayWUS)

loop = LoopView(sch)

bb = sc.bounding_box()

pb = ClippingProbeView(sc,size = max(bb.getSize()) * 1.5 )
pb.set_visible(False)

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
