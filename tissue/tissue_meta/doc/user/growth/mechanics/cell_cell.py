########################################
#
print "read tissue"
#
########################################
from openalea.celltissue import TissueDB

db = TissueDB()
db.read("tissue.zip")

mesh = db.get_topology("mesh_id")
pos = db.get_property("position")

#########################################
#
print "mechanics"
#
#########################################
from numpy.linalg import norm
from openalea.mechanics import (Particule2D,
                                LinearSpring2D,ViscousDamper2D,
                                ForwardEuler2D)
from openalea.tissueshape import centroid

K = 1. #(N) #stiffness of springs
dt_meca = 0.1 #(s) #time step used for computation

pts = dict( (cid,Particule2D(1.,centroid(mesh,pos,2,cid) ) ) \
             for cid in mesh.wisps(2) )

damp = ViscousDamper2D(pts.keys(),0.2)

spring = {}
for wid in mesh.wisps(1) :
	if mesh.nb_regions(1,wid) == 2 :
		cid1,cid2 = mesh.regions(1,wid)
		l0 = norm(pts[cid2].position() - pts[cid1].position() )
		spring[wid] = LinearSpring2D(cid1,cid2,K,l0)

def bound (solver) :
	return

def meca () :
	algo = ForwardEuler2D(pts,spring.values() + [damp],bound)
	for i in xrange(10) :
		algo.deform(dt_meca)

#########################################
#
print "growth"
#
#########################################
gamma = 1.1 #(None) #growth rate

def grow (cid) :
	print cid
	if mesh.has_wisp(2,cid) :
		print "grow"
		for wid in mesh.borders(2,cid) :
			if wid in spring :
				sp = spring[wid]
				sp.set_ref_length(sp.ref_length() * gamma)

#########################################
#
print "display"
#
#########################################
from vplants.plantgl.math import Vector3
from vplants.plantgl.scenegraph import (Sphere,Polyline,Translated,
                                        Material,Shape,Scene)
from openalea.pglviewer import SceneView

cmat = Material( (0,255,0) )
wmat = Material( (0,0,0) )
sph = Sphere(20)

sc = SceneView()
sc.idmode = sc.IDMODE.SHAPE
sc.set_line_width(4)

def redraw () :
	lsc = Scene()
	for cid,pt in pts.iteritems() :
		geom = Translated(Vector3(pt.position() ),sph)
		shp = Shape(geom,cmat)
		shp.id = cid
		lsc.add(shp)
	
	for wid,sp in spring.iteritems() :
		geom = Polyline([Vector3(pts[cid].position() ) \
		                 for cid in sp.extremities()] )
		lsc.add(Shape(geom,wmat) )
	
	sc.clear(False)
	sc.merge(lsc)

#########################################
#
print "simulation"
#
#########################################
from openalea.scheduler import Scheduler,Task

sch = Scheduler()
sch.register(Task(meca,1,0,"meca") )
sch.register(Task(redraw,1,0,"redraw") )

#########################################
#
print "launch"
#
#########################################
from openalea.pglviewer import (QApplication,Viewer,
                                LoopView,LoopGUI,
                                TemplateGUI,
                                ViewerGUI)

loop = LoopView(sch)
redraw()

gui = TemplateGUI("growth")
gui.add_tool_descr("grow cell",grow,sc.selection_draw)

qapp = QApplication([])
v = Viewer()

v.add_world(sc)

v.add_gui(ViewerGUI(vars() ) )
v.add_gui(LoopGUI(loop) )
v.add_gui(gui)

v.show()
v.view().show_entire_world()

qapp.exec_()














