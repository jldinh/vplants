execfile("local_params.py")

#############################
#
print "read mesh"
#
#############################
from openalea.container import read_topomesh

mesh,descr,props = read_topomesh("tissue.msh")

p =  dict(props[0])
pos = dict( (pid,(x,p["Y"][pid],p["Z"][pid]) ) \
           for pid,x in p["X"].iteritems() )

p =  dict(props[3])
cell_seg_id = p["SEGID"]

#############################
#
print "compute geom"
#
#############################
from openalea.tissueshape import tovec
from openalea.tissueview import cell_geom
from vplants.plantgl.algo import BBoxComputer,Discretizer

pos = tovec(pos)

cgeom = dict( (cid,cell_geom(mesh,pos,cid) ) for cid in mesh.wisps(3) )

cbb = {}
d = Discretizer()
bbc = BBoxComputer(d)
for cid,geom in cgeom.iteritems() :
	geom.apply(bbc)
	cbb[cid] = bbc.result


from openalea.pglviewer import QApplication,SceneView,Viewer
from vplants.plantgl.scenegraph import Material,Shape,Translated,Box
from vplants.plantgl.ext.color import random

sc = SceneView()
for cid,geom in cgeom.iteritems() :
	sc.add(Shape(geom,Material(random().i3tuple() ) ) )

scb = SceneView()
scb.set_display_mode(scb.DISPLAY.WIREFRAME)
mat = Material( (0,0,0) )
for cid,bb in cbb.iteritems() :
	geom = Translated(bb.getCenter(),Box(bb.getSize() ) )
	scb.add(Shape(geom,mat) )

qapp = QApplication([])
v = Viewer()
v.add_world(sc)
v.add_world(scb)
v.show()
v.view().show_entire_world()
qapp.exec_()

#############################
#
print "create inrimage"
#
#############################
import sys
from numpy import ones,uint16
from vplants.plantgl.math import Vector3
from openalea.vmanalysis import is_inside_mesh

mat = ones( (Xsize,Ysize,Zsize),uint16)

ind = 0
print len(cbb)
for cid,bb in cbb.iteritems() :
	print ind,
	ind += 1
	sys.stdout.flush()
	xmin = int(bb.getXMin() )
	xmax = int(bb.getXMax() ) + 2
	ymin = int(bb.getYMin() )
	ymax = int(bb.getYMax() ) + 2
	zmin = int(bb.getZMin() )
	zmax = int(bb.getZMax() ) + 2
	
	pts = {}
	for i in xrange(xmin,xmax) :
		for j in xrange(ymin,ymax) :
			for k in xrange(zmin,zmax) :
				pts[(i,Ysize - j,Zsize - k)] = Vector3(i,j,k)
	
	inside = tuple(is_inside_mesh(cgeom[cid],pts) )
	
	for i,j,k in inside :
		mat[i,j,k] = cell_seg_id[cid]

#############################
#
print "display result"
#
#############################
from openalea.vmanalysis import write_inrimage

h = {}
h["SCALE"] = "2**0"
h["VX"] = "%.6f" % Xres
h["VY"] = "%.6f" % Yres
h["VZ"] = "%.6f" % Zres
h["VDIM"] = "1"
h["CPU"] = "decm"
h["#GEOMETRY"] = "CARTESIAN"

write_inrimage(mat,h,"seg_reconstructed.inr.gz")







