from numpy import array
from openalea.container import Graph
from openalea.tissueview import vertex_geom
from vplants.plantgl.scenegraph import Shape,Material
from openalea.pglviewer import SceneView,display

g = Graph()

pos = {0:array([0,0,0])}
scaling = array([(1,0,0),(0,2,0),(0,0,3)])

geom = vertex_geom(g,pos,0,scaling)

sc = SceneView()

sc.add(Shape(geom,Material() ) )

display(sc)

