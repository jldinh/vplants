from vplants.plantgl.scenegraph import Material
from openalea.tissueshape import tovec,hexagonal_grid
from openalea.tissueview import draw_mesh2D
from openalea.pglviewer import SceneView,display2D

tdb = hexagonal_grid( (4,5),shape_geom="hexa")
pos = tovec(tdb.get_property("position") )

sc = draw_mesh2D(tdb.get_topology("mesh_id"),
                 pos,
                 0,
                 Material( (0,0,0) ),
                 10,
                 0)

scv = SceneView()
scv.merge(sc)
display2D(scv)

