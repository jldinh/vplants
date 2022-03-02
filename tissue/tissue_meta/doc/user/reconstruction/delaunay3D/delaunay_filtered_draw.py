execfile("local_params.py")

#############################
#
print "compute delaunay"
#
#############################
execfile("delaunay_simple.py")

#############################
#
print "constrain delaunay"
#
#############################
execfile("delaunay_constrained.py")

#############################
#
print "filter delaunay"
#
#############################
execfile("delaunay_filtered.py")

#############################
#
print "draw result"
#
#############################
from random import randint
from vplants.plantgl.scenegraph import Shape,Material,\
                                    Translated,Scaled,\
                                    TriangleSet,Sphere,Box
from openalea.pglviewer import SceneView
from openalea.pglviewer.constants import FACE
from openalea.tissueshape import tovec,centroid
from openalea.tissueview import cell_geom

pos = tovec(pos)

sc = SceneView()
sc.set_face_culling(FACE.BACK)

for cid in mesh.wisps(3) :
	geom = cell_geom(mesh,pos,cid)
	inv_tr = []
	for pid1,pid2,pid3 in geom.indexList :
		inv_tr.append( (pid1,pid3,pid2) )
	
	geomi = TriangleSet(geom.pointList,inv_tr)
	
	bary = centroid(mesh,pos,3,cid)
	geom = Translated(bary,
	       Scaled( (0.95,0.95,0.95),
	       Translated(-bary,geom) ) )
	geomi = Translated(bary,
	       Scaled( (0.95,0.95,0.95),
	       Translated(-bary,geomi) ) )
	
	if cid == 2832 :
		col = (0,0,0)
		coli = col
	else :
		col = (randint(100,255),randint(100,255),randint(100,255) )
		coli = tuple(v / 4 for v in col)
	
	shp = Shape(geom,Material(col))
	shp.id = cid
	sc.add(shp)
	shp = Shape(geomi,Material(coli))
	shp.id = cid
	sc.add(shp)

scb = SceneView()
scb.set_name("bb")
scb.set_display_mode(scb.DISPLAY.WIREFRAME)
scb.set_line_width(2)

mat = Material( (0,0,0) )
geom = Translated( (Xsize / 2.,Ysize / 2., Zsize / 2.),
                  Box( (Xsize / 2.,Ysize / 2., Zsize / 2.) ) )
scb.add(Shape(geom,mat) )

#############################
#
print "display result"
#
#############################
from openalea.pglviewer import QApplication,Viewer, \
                               ViewerGUI,View3DGUI, \
                ClippingProbeView,ClippingProbeGUI, \
                SceneGUI

pb = ClippingProbeView(sc,size = 250)

qapp = QApplication([])
v = Viewer()
v.add_world(pb)
v.add_world(scb)

v.add_gui(ViewerGUI(vars() ) )
v.add_gui(View3DGUI() )
v.add_gui(ClippingProbeGUI(pb) )
v.add_gui(SceneGUI(sc) )

v.show()
v.view().show_entire_world()

bb = sc.bounding_box()
v.view().cursor().set_position(bb.getCenter() )

qapp.exec_()


