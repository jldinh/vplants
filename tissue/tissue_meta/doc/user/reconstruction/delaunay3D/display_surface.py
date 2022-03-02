execfile("local_params.py")

######################################
#
print "read surface"
#
######################################
from pickle import load
from vplants.plantgl.scenegraph import TriangleSet

pts,trs = load(open("surface mesh.few.pkl",'rb') )
outer_boundary = TriangleSet(pts,trs)

######################################
#
print "draw surface"
#
######################################
from vplants.plantgl.scenegraph import Shape,Material,Sphere,\
                                       Translated,Box
from openalea.pglviewer import SceneView

sc = SceneView()
sc.set_name("surface")
sc.set_display_mode(sc.DISPLAY.WIREFRAME)

mat = Material( (0,0,255) )
sc.add(Shape(outer_boundary,mat) )

scb = SceneView()
scb.set_name("bb")
scb.set_display_mode(scb.DISPLAY.WIREFRAME)

mat = Material( (0,0,0) )
geom = Translated( (Xsize / 2.,Ysize / 2., Zsize / 2.),
                  Box( (Xsize / 2.,Ysize / 2., Zsize / 2.) ) )
scb.add(Shape(geom,mat) )

######################################
#
print "display surface"
#
######################################
from openalea.pglviewer import QApplication,Viewer,ViewerGUI,View3DGUI

qapp = QApplication([])
v = Viewer()
v.add_world(sc)
v.add_world(scb)

v.add_gui(ViewerGUI(vars() ) )
v.add_gui(View3DGUI() )

v.show()
v.view().show_entire_world()

qapp.exec_()


