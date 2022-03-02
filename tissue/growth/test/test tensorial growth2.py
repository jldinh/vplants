##############################
#
print "create reference shape"
#
##############################
from math import radians,sin,cos
from vplants.plantgl.math import Vector2

NB = 8
shp = {}
for i in xrange(NB) :
	a = radians(360. * i / NB)
	shp[i] = Vector2(cos(a),sin(a) )

##############################
#
print "create growth tensors"
#
##############################
from copy import deepcopy
from numpy import array
from numpy.linalg import eig
from openalea.growth import apply_strain2D

G1 = array([[0.,0.],[0.,0.]])
shp1 = deepcopy(shp)
apply_strain2D(shp1,G1)
w,v = eig(G1)
print w,v[0,:],v[1,:]

G2 = array([[0.2,0.],[0.,0.6]])
shp2 = deepcopy(shp)
apply_strain2D(shp2,G2)
w,v = eig(G2)
print w,v[0,:],v[1,:]

G3 = array([[0.,0.1],[0.1,0.]])
shp3 = deepcopy(shp)
apply_strain2D(shp3,G3)
w,v = eig(G3)
print w,v[0,:],v[1,:]

##############################
#
print "display"
#
##############################
from vplants.plantgl.math import Vector3
from vplants.plantgl.scenegraph import Shape,Material,Polyline
from openalea.pglviewer import SceneView,display2D

sc = SceneView()

#ref
geom = Polyline([Vector3(shp[i],0.) for i in [NB - 1] + range(NB)])
sc.add(Shape(geom,Material( (0,0,255) ) ) )

#shp1
geom = Polyline([Vector3(shp1[i],0.1) for i in [NB - 1] + range(NB)])
sc.add(Shape(geom,Material( (0,255,0) ) ) )

#shp2
geom = Polyline([Vector3(shp2[i],0.1) for i in [NB - 1] + range(NB)])
sc.add(Shape(geom,Material( (255,0,0) ) ) )

#shp3
geom = Polyline([Vector3(shp3[i],0.1) for i in [NB - 1] + range(NB)])
sc.add(Shape(geom,Material( (0,255,255) ) ) )

#display
display2D(sc)

