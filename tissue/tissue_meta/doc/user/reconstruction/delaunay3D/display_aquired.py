execfile("local_params.py")

######################################
#
print "read infos"
#
######################################
from pickle import load
from vplants.plantgl.scenegraph import TriangleSet

cell_cent = load(open("cell centers.pkl",'rb') )
pts,trs = load(open("surface mesh.few.pkl",'rb') )

outer_boundary = TriangleSet(pts,trs)

######################################
#
print "draw cell centers"
#
######################################
from vplants.plantgl.scenegraph import Shape,Material,Sphere,\
                                       Translated,Box
from openalea.pglviewer import SceneView

sc = SceneView()
sc.set_name("cellcenters")

mat = Material( (0,255,0) )
sph = Sphere(2)

for cid,vec in cell_cent.iteritems() :
	geom = Translated(vec,sph)
	shp = Shape(geom,mat)
	shp.id = cid
	sc.add(shp)

######################################
#
print "draw surface"
#
######################################
from vplants.plantgl.scenegraph import Shape,Material,Sphere,\
                                       Translated,Box
from openalea.pglviewer import SceneView

scs = SceneView()
scs.set_name("surface")
scs.set_display_mode(sc.DISPLAY.WIREFRAME)

mat = Material( (0,0,255) )
scs.add(Shape(outer_boundary,mat) )

scb = SceneView()
scb.set_name("bb")
scb.set_display_mode(scb.DISPLAY.WIREFRAME)

mat = Material( (0,0,0) )
geom = Translated( (Xsize / 2.,Ysize / 2., Zsize / 2.),
                  Box( (Xsize / 2.,Ysize / 2., Zsize / 2.) ) )
scb.add(Shape(geom,mat) )

######################################
#
print "display cell centers"
#
######################################
from openalea.pglviewer import QApplication,Viewer,ViewerGUI,View3DGUI

qapp = QApplication([])
v = Viewer()
v.add_world(sc)
v.add_world(scs)
v.add_world(scb)

v.add_gui(ViewerGUI(vars() ) )
v.add_gui(View3DGUI() )

v.show()
v.view().show_entire_world()

qapp.exec_()


