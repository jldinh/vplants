from random import uniform
from vplants.plantgl.scenegraph import Material
from vplants.plantgl.ext.color import JetMap
from openalea.tissueshape import tovec,hexagonal_grid
from openalea.pglviewer import QApplication,Viewer
from openalea.tissueview import MeshView2D,ScalarPropView

db = hexagonal_grid( (4,8),"hexa")

mesh = db.get_topology("mesh_id")
pos = tovec(db.get_property("position") )
prop = dict( (cid,uniform(0,1) ) for cid in mesh.wisps(2) )

cmap = JetMap(0,1)

pv = ScalarPropView(mesh,
                    pos,
                    2,
                    prop,
                    0,
                    cmap)

wv = MeshView2D(mesh,
                pos,
                1,
                0,
                Material( (0,0,0) ),
                0.1)

pv.redraw()
wv.redraw()

qapp = QApplication([])
v = Viewer()
v.add_world(pv)
v.add_world(wv)
v.show()
v.view().set_dimension(2)

qapp.exec_()

