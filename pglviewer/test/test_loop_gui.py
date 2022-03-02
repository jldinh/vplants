from random import uniform,randint
from PyQt4.QtGui import QColor
from vplants.plantgl.math import Vector3
from vplants.plantgl.scenegraph import Scene,Shape,Material,\
                                       Sphere,Translated
from vplants.plantgl.algo import GLRenderer
from openalea.scheduler import Scheduler,Task
from openalea.pglviewer import QApplication,Viewer,\
                               SceneView,SceneGUI,\
                               View3DGUI,ViewerGUI,\
                               LoopView,LoopGUI

def rvec (R) :
	return Vector3(uniform(-R,R),
                   uniform(-R,R),
                   uniform(-R,R) )

ini_pos = [rvec(10) for i in xrange(10)]

pos = [Vector3() for vec in ini_pos]

pv = SceneView()

sph = Sphere(0.2)
mat = Material( (0,255,0) )

def redraw () :
	sc = Scene()
	
	for vec in pos :
		geom = Translated(vec,sph)
		sc.add(Shape(geom,mat) )
	
	pv.clear(False)
	pv.merge(sc)

def reinit () :
	for i,vec in enumerate(ini_pos) :
		pos[i] = Vector3(vec)
	redraw()

def move () :
	for i,vec in enumerate(pos) :
		pos[i] = vec + rvec(0.1)

sch = Scheduler()
sch.register(Task(move,1,1,"move") )
sch.register(Task(redraw,1,0,"redraw") )

loop = LoopView(sch,reinit)

qapp = QApplication([])
v = Viewer()

v.add_world(pv)
v.add_gui(ViewerGUI(vars() ) )
v.add_gui(LoopGUI(loop) )
v.add_gui(View3DGUI() )

v.show()
v.view().show_entire_world()

qapp.exec_()



