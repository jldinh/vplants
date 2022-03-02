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
print "draw tissue"
#
#############################
from vplants.plantgl.scenegraph import Material,Shape,\
                                       Translated,Scaled
from openalea.tissueshape import tovec,centroid
from openalea.tissueview import cell_geom
from openalea.pglviewer import SceneView

sc = SceneView()
sc.set_lightning(False)

pos = tovec(pos)
mat = Material( (255,255,255) )

for cid in mesh.wisps(3) :
	geom = cell_geom(mesh,pos,cid)
	sc.add(Shape(geom,mat) )
	
	bary = centroid(mesh,pos,3,cid)
	for sca in (0.98,0.99,1.01,1.02) :
		g = Translated(bary,
			Scaled( (sca,sca,sca),
			Translated(- bary,geom)
			)
			)
		sc.add(Shape(g,mat) )

#############################
#
print "draw bounding box"
#
#############################
from vplants.plantgl.scenegraph import Box,Translated

scb = SceneView()
scb.set_name("bb")
scb.set_display_mode(scb.DISPLAY.WIREFRAME)
scb.set_line_width(2)

mat = Material( (255,255,255) )
geom = Translated( (Xsize / 2.,Ysize / 2., Zsize / 2.),
                  Box( (Xsize / 2.,Ysize / 2., Zsize / 2.) ) )
scb.add(Shape(geom,mat) )

#############################
#
print "clipping planes"
#
#############################
from openalea.pglviewer import Vec,Quaternion,ClippingProbeView

pb = ClippingProbeView(sc,size = Xsize * 2)
pb.set_visible(False)
#pb.set_slice_size(10.)
pb.setPosition(Vec(Xsize / 2.,Ysize / 2.,Zsize / 2.) )

pb2 = ClippingProbeView(pb,size = Xsize * 2)
pb2.set_visible(False)
pb2.setPosition(Vec(Xsize / 2.,Ysize / 2.,Zsize / 2. - 1) )
q = Quaternion()
q.setFromRotatedBasis(Vec(1,0,0),Vec(0,-1,0),Vec(0,0,-1) )
pb2.setOrientation(q)

#############################
#
print "display tissue"
#
#############################
from PyQt4.QtCore import QSize,Qt,QObject,SIGNAL
from PyQt4.QtGui import QColor
from openalea.pglviewer import Vec,QApplication,Viewer,\
                               ViewerGUI
from numpy import zeros,uint8
from openalea.vmanalysis import write_inrimage

w,h = Xsize * 8,Ysize * 8

qapp = QApplication([])
v = Viewer()
v.add_world(pb2)
v.add_world(scb)
gui = ViewerGUI(vars() )
v.add_gui(gui)
v.show()

v.view().setFixedSize(w,h)
#v.view().setBackgroundColor(QColor(0,0,0) )

cam = v.view().camera()
cam.setType(cam.ORTHOGRAPHIC)
#cam.setPosition(Vec(Xsize / 2.,Ysize / 2.,1000) )
cam.fitBoundingBox(Vec(0,0,0),Vec(Xsize,Ysize,Zsize) )

pb.activate(v.view(),True)
pb2.activate(v.view(),True)


info = {}
info["SCALE"] = "2**0"
info["VX"] = "%.6f" % Xres
info["VY"] = "%.6f" % Yres
info["VZ"] = "%.6f" % Zres
info["VDIM"] = "1"
info["CPU"] = "decm"
info["#GEOMETRY"] = "CARTESIAN"

def snap () :
	mat = zeros( (Xsize,Ysize,Zsize),uint8)
	
	for z in xrange(90,207) : #Zsize) :
		print z
		pb.setPosition(Vec(Xsize / 2.,Ysize / 2.,z + 1) )
		pb2.setPosition(Vec(Xsize / 2.,Ysize / 2.,z) )
		v.view().updateGL()
		pix = v.view().renderPixmap(w,h)
		pix = pix.scaled(QSize(Xsize,Ysize),
			             Qt.IgnoreAspectRatio,
			             Qt.SmoothTransformation)
		pix.save("im/slice%.4d.png" % z)
		im = pix.toImage()
		for x in xrange(Xsize) :
			for y in xrange(Ysize) :
				mat[x,y,z] = QColor.fromRgb(im.pixel(x,y) ).red()
	
	write_inrimage(mat,info,"test_geometry.inr.gz")

ac = gui._action_bar.addAction("snap")
QObject.connect(ac,
                SIGNAL("triggered(bool)"),
                snap)




qapp.exec_()


