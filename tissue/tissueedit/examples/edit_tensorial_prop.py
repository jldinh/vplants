from math import sin,cos,pi
from random import random
from PyQt4.QtCore import SIGNAL
from vplants.plantgl.scenegraph import Material
from vplants.plantgl.ext.color import JetMap
from vplants.plantgl.algo import GLRenderer
from openalea.pglviewer import SceneView,QApplication,Viewer, \
                               ViewerGUI,UndoGUI
from openalea.tissueshape import tovec,hexagonal_grid
from openalea.tissueview import MeshView,TensorialPropView
from openalea.tissueedit import TensorialPropEditGUI

tdb = hexagonal_grid( (4,5),shape_geom="hexa")
mesh = tdb.get_topology("mesh_id")
pos = tovec(tdb.get_property("position") )
bary = reduce(lambda x,y: x + y,pos.itervalues() ) / len(pos)
pos.set_value(dict( (pid,vec - bary) for pid,vec in pos.iteritems() ) )

prop = {}
for cid in mesh.wisps(2) :
	angle = random() * pi / 2.
	v1 = (cos(angle),sin(angle) )
	v2 = (-sin(angle),cos(angle) )
	prop[cid] = (v1,v2)

mv = MeshView(mesh,pos,1,0,Material( (0,0,0) ) )
mv.redraw()

sc = TensorialPropView(mesh,pos,2,prop,0.4)
sc.redraw()

select = MeshView(mesh,pos,2,0,Material() )
select.idmode = GLRenderer.SelectionId.ShapeId
select.redraw()

gui = TensorialPropEditGUI(sc,select.selection_draw)

qapp = QApplication([])
v = Viewer()
v.add_world(mv)
v.add_world(sc)
v.add_gui(ViewerGUI(vars() ) )
v.add_gui(gui)
v.add_gui(UndoGUI() )
v.show()
v.view().set_dimension(2)
v.view().show_entire_world()

qapp.exec_()


