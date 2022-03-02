execfile("local_params.py")

#############################
#
print "compute delaunay"
#
#############################
execfile("delaunay_simple.py")

cpos = dict( (pid,tuple(vec) ) for pid,vec in pos.iteritems() )
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

#############################
#
print "compute voronoi"
#
#############################
execfile("voronoi_projected.py")

#############################
#
print "compute centers"
#
#############################
from openalea.tissueshape import tovec,totup,centroid

pos = tovec(pos)

cell_centers = dict( (cid,centroid(mesh,pos,3,cid) ) \
                     for cid in mesh.wisps(3) )

#############################
#
print "compute distance"
#
#############################
from vplants.plantgl.math import norm

V = load(open("cell size.all.pkl",'rb') )

err= {}
for cid,vec in cpos.iteritems() :
	e = norm(cell_centers[cid] - vec)
	R = V[cell_seg_id[cid] ] ** 0.33
	err[cid] = e / R

#############################
#
print "find cell groups"
#
#############################
L1 = set()
for fid in mesh.wisps(2) :
	if mesh.nb_regions(2,fid) == 1 :
		L1.update(mesh.regions(2,fid) )

L2 = set()
for cid in L1 :
	L2.update(mesh.border_neighbors(3,cid) )
L2 -= L1

L3 = set(mesh.wisps(3) ) - L2 - L1

#############################
#
print "plot error"
#
#############################
from pylab import hist,plot,show,legend,\
                  xlabel,savefig,figure

data = [[err[cid] for cid in L1],
        [err[cid] for cid in L2],
        [err[cid] for cid in L3] ]

hist(data,
     label = ["L1","L2","L3"],
     histtype='barstacked',
     normed = False)
legend(loc = 'upper right')
xlabel("Relative error: e = d / R")
show()

fig = figure(figsize = (8,6) )
hist(data,
     label = ["L1","L2","L3"],
     histtype='barstacked',
     normed = False)
legend(loc = 'upper right')
xlabel("Relative error: e = d / R")

savefig("test_cell_center_err.png")

#############################
#
print "draw result"
#
#############################
from vplants.plantgl.scenegraph import Shape,Material,Translated,\
                                       Polyline,Sphere,Box
from openalea.pglviewer import SceneView


sc = SceneView()

sph = Sphere(2)

mat = Material( (255,0,0) )
for cid,vec in cpos.iteritems() :
	geom = Translated(vec,sph)
	sc.add(Shape(geom,mat) )

mat = Material( (0,0,0) )
for cid,vec in cell_centers.iteritems() :
	geom = Translated(vec,sph)
	sc.add(Shape(geom,mat) )

mat = Material( (0,0,0) )
for cid,vec in cpos.iteritems() :
	geom = Polyline([vec,cell_centers[cid] ])
	sc.add(Shape(geom,mat) )

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

qapp = QApplication([])
v = Viewer()
v.add_world(sc)
v.add_world(scb)

v.add_gui(ViewerGUI(vars() ) )
v.add_gui(View3DGUI() )
v.add_gui(SceneGUI(sc) )

v.show()
v.view().show_entire_world()

bb = scb.bounding_box()
v.view().cursor().set_position(bb.getCenter() )

qapp.exec_()










