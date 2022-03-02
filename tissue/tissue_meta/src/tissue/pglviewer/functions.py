from random import uniform,randint
from vplants.plantgl.scenegraph import Scene,Shape,Material,\
                       Sphere,Translated
from openalea.pglviewer import Vec

def function_generate_scene():
	"""Generate a random pgl scene filled with spheres.
	"""
	sc = Scene()
	for i in xrange(10) :
		pos = (uniform(-1,1),
		       uniform(-1,1),
		       uniform(-1,1) )
		mat = Material( (randint(0,255),
		                 randint(0,255),
		                 randint(0,255) ) )
		geom = Sphere(uniform(0.2,0.3) )
		sc.add(Shape(Translated(pos,geom),mat) )
	
	return sc,

def function_move_scene(scene):
	"""Move globally a scene using a random displacement.
	"""
	disp = Vec(uniform(-0.1,0.1),
	           uniform(-0.1,0.1),
	           uniform(-0.1,0.1) )
	
	scene.set_draw_frame(True)
	fr = scene.frame()
	fr.setPosition(fr.position() + disp)
	
	return scene,

