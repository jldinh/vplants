from random import uniform,randint
from vplants.plantgl.scenegraph import *
from openalea.pglviewer import SceneView,display

sc = SceneView()

for i in xrange(10) :
	pos = (uniform(-10,10),
	       uniform(-10,10),
	       uniform(-10,10) )
	
	sph = Sphere(uniform(0.5,2) )
	geom = Translated(pos,sph)
	mat = Material( (randint(0,255),
	                 randint(0,255),
	                 randint(0,255) ) )
	sc.add(Shape(geom,mat) )

display(sc)


