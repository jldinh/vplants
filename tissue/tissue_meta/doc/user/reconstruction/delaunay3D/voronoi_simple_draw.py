execfile("local_params.py")

#############################
#
print "compute delaunay"
#
#############################
execfile("delaunay_simple.py")

cell_pos = dict( (pid,tuple(vec) ) for pid,vec in pos.iteritems() )
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
print "compute voronoi"
#
#############################
execfile("voronoi_simple.py")

#put point in infinity
from openalea.tissueshape import tovec,totup

pos = tovec(pos)
bary = reduce(lambda x,y : x + y,pos.itervalues() ) / len(pos)

for pid in dangling_pids :
	seg_ori = pos[pid] - bary
	seg_ori.normalize()
	pos[pid] += seg_ori * 300

pos = totup(pos)
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
	
	col = (randint(0,255),randint(0,255),randint(0,255) )
	coli = tuple(v / 4 for v in col)
	sc.add(Shape(geom,Material(col)) )
	sc.add(Shape(geomi,Material(coli)) )

sph = Sphere(1)
mat = Material( (0,0,0) )
for pid in mesh.wisps(0) :
	geom = Translated(pos[pid],sph)
	shp = Shape(geom,mat)
	shp.id = pid
	sc.add(shp)

mat = Material( (255,0,0) )
for pid,vec in cell_pos.iteritems() :
	geom = Translated(vec,sph)
	shp = Shape(geom,mat)
	shp.id = pid
	sc.add(shp)

#scb = SceneView()
#scb.set_display_mode(scb.DISPLAY.WIREFRAME)

#scb.add(Shape(outer_boundary,Material( (255,0,0) ) ) )

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

bb = scb.bounding_box()
v.view().cursor().set_position(bb.getCenter() )

qapp.exec_()


