from math import radians,sin,cos
from vplants.plantgl.math import Vector3
from openalea.container import Topomesh

R = 1. #(m) #radius of the shape
thickness = 0.01 #(m)

#create mesh
mesh = Topomesh(2)
pos = {}

#create points
for i in (0,1,2,3,4,5) :
	pid = mesh.add_wisp(0,i)
	pos[pid] = Vector3(R * cos(radians(30 + i * 60) ),
	                   R * sin(radians(30 + i * 60) ),
	                   0)

#create edges
for i,(pid1,pid2) in enumerate([(0,1),(1,2),(2,3),
                                (3,4),(4,5),(5,0)]) :
	eid = mesh.add_wisp(1,i)
	mesh.link(1,eid,pid1)
	mesh.link(1,eid,pid2)

#create face
fid = mesh.add_wisp(2)
for eid in mesh.wisps(1) :
	mesh.link(2,fid,eid)

