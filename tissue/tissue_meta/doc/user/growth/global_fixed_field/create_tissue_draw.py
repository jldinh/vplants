from openalea.deploy import execfile_partial

execfile_partial(vars(),"simu.py",None,"#end create tissue")

################################################
#
print "draw"
#
################################################
from math import pi,sin,cos
from vplants.plantgl.math import Vector3
from vplants.plantgl.scenegraph import Material,Shape,\
                                       NurbsPatch,Translated,Sphere
from openalea.pglviewer import SceneView
from openalea.tissueview import edge_geom3D,face_geom3D

angles = [2 * pi * i / 10. for i in xrange(11)]
mat = [[(pt[0] * cos(a),pt[0] * sin(a),pt[2],pt[3]) for pt in ctrl_pts] for a in angles]

patch = NurbsPatch(mat)

pos = dict( (pid,cartesian(Gfield,uv) ) for pid,uv in uvpos.iteritems() )

sc = SceneView()
sc.set_display_mode(sc.DISPLAY.WIREFRAME)
sc.add(Shape(patch,Material( (0,0,255) ) ) )

tsc = SceneView()
tsc.set_line_width(2.)

geom = face_geom3D(mesh,pos,cid,Vector3(0,0,1) )
geom = Translated( (0,0,-0.01),geom)
tsc.add(Shape(geom,Material( (0,0,200) ) ) )

sph = Sphere(0.02)
mat = Material( (0,255,0) )
for pid,vec in pos.iteritems() :
	geom = Translated(vec,sph)
	tsc.add(Shape(geom,mat) )

mat = Material( (0,0,0) )
for eid in mesh.wisps(1) :
	geom = edge_geom3D(mesh,pos,eid)
	tsc.add(Shape(geom,mat) )

################################################
#
print "display"
#
################################################
from openalea.pglviewer import QApplication,Viewer,View3DGUI

qapp = QApplication([])
v = Viewer()
v.add_world(sc)
v.add_world(tsc)
v.add_gui(View3DGUI() )

v.show()
v.view().show_entire_world()

qapp.exec_()

