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
print "find flat triangles"
#
#############################
from pickle import dump
from openalea.vmanalysis import centroid,circum_center3D,mesh_intersect
from vplants.plantgl.scenegraph import TriangleSet

#read outer boundary mesh
pts,trs = load(open("surface mesh.few.pkl",'rb') )
outer_boundary = TriangleSet(pts,trs)

#find all circum centers
segs = {}

for cid in mesh.wisps(3) :
	tet = tuple(pos[pid] for pid in mesh.borders(3,cid,3) )
	G = centroid(mesh,pos,3,cid)
	H = circum_center3D(*tet)
	segs[cid] = (G,H)

try :
	flat_tet = load(open("flat tet.pkl",'rb') )
except IOError :
	#test intersection with surface
	flat_tet = set(mesh_intersect(outer_boundary,segs) )
	dump(flat_tet,open("flat tet.pkl",'w') )

regular_tr = set(mesh.wisps(3) ) - flat_tet

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

for cid in flat_tet :
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

scs = SceneView()
scs.set_name("surface")
scs.set_display_mode(scs.DISPLAY.WIREFRAME)

sph = Sphere(3)
mat = Material( (0,0,0) )

for cid in flat_tet :
	H = segs[cid][1]
	geom = Translated(H,sph)
	scs.add(Shape(geom,mat) )

scs.add(Shape(outer_boundary,Material( (255,0,0) ) ) )

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
                ClippingProbeView,ClippingProbeGUI

pb = ClippingProbeView(sc,size = 250)

qapp = QApplication([])
v = Viewer()
v.add_world(pb)
v.add_world(scb)
v.add_world(scs)

v.add_gui(ViewerGUI(vars() ) )
v.add_gui(View3DGUI() )
v.add_gui(ClippingProbeGUI(pb) )

v.show()
v.view().show_entire_world()

bb = sc.bounding_box()
v.view().cursor().set_position(bb.getCenter() )

qapp.exec_()






