from random import uniform,randint
from vplants.plantgl.scenegraph import Sphere,Translated,\
                               Shape,Material
from openalea.pglviewer import QApplication,Viewer,SceneView

sc = SceneView()

for i in xrange(10) :
	vec = (uniform(-1,1),
	       uniform(-1,1),
	       uniform(-1,1) )
	sph = Sphere(uniform(0.1,1) )
	geom = Translated(vec,sph)
	col = (randint(0,255),
	       randint(0,255),
	       randint(0,255) )
	mat = Material(col)
	
	sc.add(Shape(geom,mat) )

qapp = QApplication([])
v = Viewer()
v.add_world(sc)
v.show()
v.view().show_entire_world()

qapp.exec_()

