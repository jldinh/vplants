#########################################
#
print "read curves"
#
#########################################
from pickle import load
from vplants.plantgl.math import Vector4

crv_pt = load(open("surface curves.pkl",'rb') )

crv_pt = [ [Vector4(*pt) for pt in pts] \
           for name,pts in crv_pt.iteritems() ]

nb = len(crv_pt[0])
for crv in crv_pt :
	assert len(crv) == nb

#########################################
#
print "find global frame"
#
#########################################
from vplants.plantgl.math import Vector3

top_point = sum( (pts[0] for pts in crv_pt), Vector4() ) / len(crv_pt)
bottom_point = sum( (pts[-1] for pts in crv_pt), Vector4() ) / len(crv_pt)

O = Vector3(bottom_point.x,bottom_point.y,bottom_point.z)

Oz = Vector3(top_point.x,top_point.y,top_point.z) - O
Oz.normalize()

pt = crv_pt[0][nb / 2]
Oy = Oz ^ Vector3(pt.x,pt.y,pt.z)
Oy.normalize()

Ox = Oy ^ Oz
Ox.normalize()

#########################################
#
print "find angle and projection for each curve"
#
#########################################
from math import pi,atan2,degrees
from vplants.plantgl.math import Vector2
from vplants.plantgl.scenegraph import NurbsCurve2D

crvs = []
angles = []

for pts in crv_pt :
	#find local frame
	pt = Vector3(pts[nb / 2].x,pts[nb / 2].y,pts[nb / 2].z)
	crv_dir_x = pt * Ox
	crv_dir_y = pt * Oy
	
	lOx = Ox * crv_dir_x + Oy * crv_dir_y
	lOx.normalize()
	lOy = Oz
	
	#find angle
	alpha = atan2(crv_dir_y,crv_dir_x)
	angles.append(alpha)
	
	#find profile
	crv2D = []
	for ctrl_pt in pts :
		pt = Vector3(ctrl_pt.x,ctrl_pt.y,ctrl_pt.z)
		lpt = Vector3( (pt - O) * lOx,
		               (pt - O) * lOy,
		               ctrl_pt.w)
		crv2D.append(lpt)
	
	crvs.append(NurbsCurve2D(crv2D) )

#renormalize angles
alpha_ref = angles[0]

profiles = []
for i,a in enumerate(angles) :
	a -= alpha_ref
	if a < 0 :
		a += 2 * pi
	profiles.append( (a,crvs[i]) )

profiles.sort()
print profiles
print [degrees(a) for a,crv in profiles]

#########################################
#
print "create swung"
#
#########################################
from vplants.plantgl.scenegraph import Swung

#close curve
profiles.append( (2 * pi,profiles[0][1]) )

swung = Swung([crv for a,crv in profiles],
              [a for a,crv in profiles],
              16 * 12,
              False,
              3,
              16 * 6)

swungfew = Swung([crv for a,crv in profiles],
              [a for a,crv in profiles],
              16,
              False,
              3,
              16)

#########################################
#
print "display"
#
#########################################
from openalea.pglviewer import Vec,Frame,Quaternion,SceneView,\
                               QApplication,Viewer,View3DGUI
from vplants.plantgl.scenegraph import Shape,Material,\
                                       NurbsCurve,\
                                       Translated,Scaled,AxisRotated,\
                                       Sphere, Polyline

#blender curves
sc = SceneView()
sc.set_line_width(3)

for crv in crv_pt :
	geom = NurbsCurve(crv)
	mat = Material( (0,0,255) )
	sc.add(Shape(geom,mat) )

geom = Translated(O,Sphere() )
sc.add(Shape(geom,Material( (0,255,0) ) ) )

geom = Polyline([O,O + Ox * 10])
sc.add(Shape(geom,Material( (255,0,0) ) ) )

geom = Polyline([O,O + Oy * 10])
sc.add(Shape(geom,Material( (0,255,0) ) ) )

geom = Polyline([O,O + Oz * 10])
sc.add(Shape(geom,Material( (0,0,255) ) ) )

#computed profiles
sca = SceneView()

mat = Material( (0,255,0) )
for a,crv in profiles :
	sca.add(Shape(crv,mat) )

#computed swung
scb = SceneView()
scb.set_display_mode(sc.DISPLAY.WIREFRAME)
q = Quaternion()
q.setFromRotatedBasis(Vec(*Ox),Vec(*Oy),Vec(*Oz) )

swung = Translated(O,AxisRotated(q.axis(),q.angle(),swung) )
swungfew = Translated(O,AxisRotated(q.axis(),q.angle(),swungfew) )

scb.add(Shape(swung,Material() ) )

#blender points
scc = SceneView()
pts = load(open("bldvtx.pkl",'rb') )

sph = Sphere(0.3)
mat = Material( (0,255,0) )
for pid,pt in pts.iteritems() :
	geom = Translated(pt,sph)
	scc.add(Shape(geom,mat) )

#comparison with initial points
vtx = load(open("vertices.pkl",'rb') )

bary,scaling = load(open("bldtransform.pkl",'rb') )
scale = (1. / scaling,) * 3

scd = SceneView()
scd.set_display_mode(scd.DISPLAY.WIREFRAME)

surf_geom = Translated(bary,Scaled(scale,swung) )
surf_geom_few = Translated(bary,Scaled(scale,swungfew) )
scd.add(Shape(surf_geom,Material( (0,0,255) ) ) )

sph = Sphere(3)
mat = Material( (255,0,0) )
for vec in vtx :
	geom = Translated(vec,sph)
	scd.add(Shape(geom,mat) )

qapp = QApplication([])
v = Viewer()
v.add_world(sc)
v.add_world(sca)
v.add_world(scb)
v.add_world(scc)
v.add_world(scd)

v.add_gui(View3DGUI() )

v.show()
v.view().show_entire_world()

qapp.exec_()

#########################################
#
print "write surface"
#
#########################################
from vplants.plantgl.algo import Discretizer
from pickle import dump

#surface
d = Discretizer()
surf_geom.apply(d)

print d.result

pts = [tuple(vec) for vec in d.result.pointList]
trs = [tuple(inds) for inds in d.result.indexList]

dump( (pts,trs),open("../surface mesh.pkl",'w') )

#surface few
d = Discretizer()
surf_geom_few.apply(d)

print d.result

pts = [tuple(vec) for vec in d.result.pointList]
trs = [tuple(inds) for inds in d.result.indexList]

dump( (pts,trs),open("../surface mesh.few.pkl",'w') )












