############################################
#
print "read mesh"
#
############################################
from numpy import array
from numpy.linalg import norm
from openalea.container import read_topomesh
from vplants.plantgl.math import Vector3

mesh,descr,props = read_topomesh("sphere.msh")

p = dict(props[0])

pos = dict( (pid,array([p['X'][pid],p['Y'][pid],p['Z'][pid]]) ) for pid in mesh.wisps(0) )

for pid,vec in pos.iteritems() :
	pos[pid] = Vector3(vec * (1. / norm(vec) ) )

############################################
#
print "draw mesh"
#
############################################
from vplants.plantgl.scenegraph import (Font,Text,Translated,
                                        Polyline,Material,Shape)
from openalea.pglviewer import SceneView,display

sc = SceneView()

mat = Material( (0,0,255) )
font = Font("ariana",8)

for eid in mesh.wisps(1) :
	geom = Polyline([pos[pid] for pid in mesh.borders(1,eid)])
	sc.add(Shape(geom,mat) )

for pid in mesh.wisps(0) :
	geom = Text("%d" % pid,pos[pid] * 1.1,False,font)
	sc.add(Shape(geom,mat) )

############################################
#
print "display mesh"
#
############################################
from openalea.pglviewer import display

display(sc)

