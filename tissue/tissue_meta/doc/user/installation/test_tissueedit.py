from random import uniform
from openalea.container import Quantity
from vplants.plantgl.scenegraph import Material
from vplants.plantgl.ext.color import JetMap
from openalea.tissueshape import tovec,hexagonal_grid
from openalea.pglviewer import QApplication,Viewer
from openalea.tissueview import ScalarPropView
from openalea.tissueedit import ScalarPropEditGUI

db = hexagonal_grid( (4,8),"hexa")

mesh = db.get_topology("mesh_id")
pos = tovec(db.get_property("position") )
prop = Quantity(dict( (cid,uniform(0,1) ) for cid in mesh.wisps(2) ),
                unit = "mol.m-3",
                type = "float",
                description = "IAA concentration in cytoplasms")

cmap = JetMap(0,1)

pv = ScalarPropView(mesh,
                    pos,
                    2,
                    prop,
                    10,
                    cmap)

pv.redraw()

edit_gui = ScalarPropEditGUI(pv)

qapp = QApplication([])
v = Viewer()
v.add_world(pv)
v.add_gui(edit_gui)
v.show()
v.view().set_dimension(2)

qapp.exec_()

