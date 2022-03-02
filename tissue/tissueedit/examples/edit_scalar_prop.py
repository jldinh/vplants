from random import random
from PyQt4.QtCore import SIGNAL
from vplants.plantgl.scenegraph import Material
from vplants.plantgl.ext.color import JetMap
from openalea.pglviewer import SceneView,QApplication,Viewer, \
                               ViewerGUI,UndoGUI
from openalea.tissueshape import tovec,hexagonal_grid
from openalea.tissueview import ScalarPropView
from openalea.tissueedit import ScalarPropEditGUI,PropEditGUI

tdb = hexagonal_grid( (4,5),shape_geom="hexa")
mesh = tdb.get_topology("mesh_id")
pos = tovec(tdb.get_property("position") )

prop = dict( (cid,random() ) for cid in mesh.wisps(2) )

cmap = JetMap(0.,1.,outside_values = True)

sc = ScalarPropView(mesh,pos,2,prop,10,cmap)
sc.redraw()

gui = ScalarPropEditGUI(sc,float)

qapp = QApplication([])
v = Viewer()
v.set_world(sc)
v.add_gui(ViewerGUI(vars() ) )
v.add_gui(PropEditGUI(prop) )
v.add_gui(gui)
v.add_gui(UndoGUI() )
v.show()
v.view().set_dimension(2)
v.view().show_entire_world()

qapp.exec_()


