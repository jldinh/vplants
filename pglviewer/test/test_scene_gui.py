from random import uniform, randint
from PyQt4.QtGui import QColor
from vplants.plantgl.scenegraph import *
from vplants.plantgl.algo import GLRenderer
from openalea.pglviewer import QApplication, Viewer, \
                               SceneView, SceneGUI, \
                               View3DGUI

sc = SceneView()
sc.idmode = GLRenderer.ShapeId

for i in xrange(10) :
	pos = (uniform(-10, 10),
	       uniform(-10, 10),
	       uniform(-10, 10))

	sph = Sphere(uniform(0.5, 2))
	geom = Translated(pos, sph)
	mat = Material((randint(0, 255),
	                 randint(0, 255),
	                 randint(0, 255)))

	shp = Shape(geom, mat)
	shp.id = i

	sc.add(shp)

qapp = QApplication([])
v = Viewer()
v.add_world(sc)
v.add_gui(SceneGUI(sc))
v.add_gui(View3DGUI())
v.show()
v.view().show_entire_world()

qapp.exec_()



