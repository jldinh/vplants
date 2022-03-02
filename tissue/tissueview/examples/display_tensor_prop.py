from random import random
from vplants.plantgl.scenegraph import Material
from vplants.plantgl.ext.color import JetMap
from openalea.tissueshape import tovec,hexagonal_grid
from openalea.tissueview import draw_mesh,draw_tensorial_prop
from openalea.pglviewer import SceneView,display2D

tdb = hexagonal_grid( (4,5),shape_geom="hexa")
mesh = tdb.get_topology("mesh_id")
pos = tovec(tdb.get_property("position") )

def rvec () :
	return (random(),random() )

prop = dict( (cid,[rvec()] ) for cid in mesh.wisps(2) )
prop2 = {}
for cid in mesh.wisps(2) :
	v1 = rvec()
	v2 = (v1[1],-v1[0])
	prop2[cid] = [v1,v2]

scv = SceneView()

sc = draw_tensorial_prop(mesh,
                 pos,
                 2,
                 prop2,
                 0.2)
scv.merge(sc)

sc = draw_mesh(mesh,pos,1,Material( (0,0,0) ),0)
scv.merge(sc)

display2D(scv)

