from vplants.plantgl.scenegraph import Material
from openalea.pglviewer import (QApplication, Viewer, ViewerGUI, View3DGUI
                              , SceneGUI)
from openalea.celltissue import topen
from openalea.tissueshape import tovec
from openalea.tissuepainter import TissueView, TissuePainterGUI

#f = topen("cell.zip", 'r')
#t = f.read()
##WUS, dmy = f.read("pattern_WUS")
#f.close()

#t.geometry().apply_geom_transfo(tovec)

tv = TissueView()
#tv.set_tissue(t)

#color_id = tv.add_color(Material( (255,0,0) ) )
#for cid in WUS :
#	tv.set_color(cid, color_id)

qapp = QApplication([])
v = Viewer()
v.set_world(tv)
gui = TissuePainterGUI(tv)
v.add_gui(gui)
v.add_gui(ViewerGUI(vars() ) )
v.add_gui(View3DGUI() )
#v.add_gui(SceneGUI(tv) )
v.show()
v.view().show_entire_world()

gui.open_tissue("cell.zip")

qapp.exec_()

