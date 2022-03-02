from random import random
from vplants.plantgl.scenegraph import Material
from vplants.plantgl.ext.color import JetMap
from openalea.tissueshape import tovec,hexagonal_grid
from openalea.tissueview import draw_scalar_prop2D
from openalea.pglviewer import SceneView,display2D

tdb = hexagonal_grid( (4,5),shape_geom="hexa")
mesh = tdb.get_topology("mesh_id")
pos = tovec(tdb.get_property("position") )

prop = dict( (cid,random() ) for cid in mesh.wisps(2) )

cmap = JetMap(0.,1.,outside_values = True)

sc = draw_scalar_prop2D(mesh,
                 pos,
                 2,
                 prop,
                 10,
                 cmap,
                 0)

scv = SceneView()
scv.merge(sc)
display2D(scv)

