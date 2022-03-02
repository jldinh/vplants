from math import sin,cos,radians
from numpy import zeros
from vplants.plantgl.math import Vector3
from openalea.growth import apply_strain2D
from openalea.mechanics import triangle_frame

shape = (1.,0.5,1.)
G = zeros( (2,2) )

print apply_strain2D(shape,G)

G[0,0] = 0.2
G[1,1] = 0.

print apply_strain2D(shape,G)

alpha = radians(10)
pt0 = Vector3(0,0,0)
pt1 = Vector3(cos(alpha),sin(alpha),0)
pt2 = Vector3(-sin(alpha),cos(alpha),0)

fr = triangle_frame(pt0,pt1,pt2)

G = fr.global_tensor2(G)

print apply_strain2D(shape,G)

#display
from vplants.plantgl.scenegraph import Shape,Material,TriangleSet, \
                                       Translated,Polyline
from openalea.pglviewer import display2D,SceneView

sc = SceneView()

R1,R2,S2 = shape

mat = Material( (0,0,255) )
t1 = TriangleSet([(0,0,0),(R1,0,0),(R2,S2,0)],[(0,1,2)])
sc.add(Shape(Translated( (0,0,-0.1),t1),mat) )

r1,r2,s2 = apply_strain2D(shape,G)

mat = Material( (0,255,0) )
p = Polyline([(0,0,0),(r1,0,0),(r2,s2,0),(0,0,0)])
sc.add(Shape(p,mat) )

mat = Material( (255,0,0) )
p = Polyline([(0,0,0),pt1 * 2])
sc.add(Shape(p,mat) )

display2D(sc)

