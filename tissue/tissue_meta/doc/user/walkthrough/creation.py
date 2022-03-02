#import
from openalea.celltissue import Tissue

#tissue object creation
t = Tissue()

#creation of new type of element
ctyp = t.add_type("cell")

#add elements of type 'ctyp'
cells = []
for i in xrange(3) :
	cid = t.add_element(ctyp)
	cells.append(cid)

#test element type
assert t.type(cells[0]) == ctyp

#create another type of element
wtyp = t.add_type("wall")

walls = []
for i in xrange(3) :
	wid = t.add_element(wtyp)
	walls.append(wid)

#remove element
wid = walls.pop(-1)
t.remove_element(wid)

#types walk
for typ in t.types() :
	print typ,t.type_name(typ)
#: 0 cell
#: 1 wall

#elements walk
for elmid in t.elements() :
	print elmid,t.type_name(t.type(elmid) )
#: 0 cell
#: 1 cell
#: 2 cell
#: 3 wall
#: 4 wall

#elements types walk
assert set(cells) == set(t.elements(ctyp) )
assert set(walls) == set(t.elements(wtyp) )

#graph: create the topological relation
graph_id = t.add_relation("graph",(ctyp,wtyp) )

#graph: create edges
graph = t.relation(graph_id)

for i in (0,1) :
	graph.add_edge(cells[i],cells[i + 1],walls[i])

#graph: walkthrough
#print vertices
print tuple(graph.vertices() )
#: (0,1,2)
assert set(graph.vertices() ) == set(t.elements(ctyp) )

#print edges
for eid in graph.edges() :
	print eid,graph.source(eid),graph.target(eid)
#: 3,0,1
#: 4,1,2

#print neighborhood
for cid in graph.vertices() :
	print cid,tuple(graph.neighbors(cid) )
#: 0,(1,)
#: 1,(0,2)
#: 2,(1,)

#point type creation
ptyp = t.add_type("point")

#mesh: create the topological relation
mesh_id = t.add_relation("mesh",(ptyp,wtyp,ctyp) )

#mesh: add points and walls
mesh = t.relation(mesh_id)

points = [mesh.add_wisp(0) for i in xrange(8)]
for i in xrange(8) :
	walls.append(mesh.add_wisp(1) )

#mesh: link elements
#link walls and points
for wind,pinds in [(0,(1,5) ),(1,(2,6) ),
                   (2,(0,4) ),(3,(3,7) ),
                   (4,(0,1) ),(5,(1,2) ),(6,(2,3) ),
                   (7,(4,5) ),(8,(5,6) ),(7,(6,7) )] :
	for pind in pinds :
		mesh.link(1,walls[wind],points[pind])

for cind,winds in [(0,(0,2,4,7) ),
                   (1,(0,1,5,8) ),
                   (2,(1,3,6,9) )] :
	for wind in winds :
		mesh.link(2,cells[cind],walls[wind])

#mesh: exploration
for cid in mesh.wisps(2) :
	print cid,tuple(mesh.borders(2,cid) )
#: 0 (3L, 14L, 16L, 19L)
#: 1 (3L, 4L, 17L, 20L)
#: 2 (4L, 15L, 18L, 21L)

wid = walls[0]
assert set([graph.source(wid),graph.target(wid)]) == set(mesh.regions(1,wid) )

wid = walls[1]
assert set([graph.source(wid),graph.target(wid)]) == set(mesh.regions(1,wid) )

#property: compound
compound = dict( (cid,0) for cid in t.elements(ctyp) )

#property: pos
pos = {}
for i in xrange(4) :
	pos[points[i] ] = (i,1)
	pos[points[i + 4] ] = (i,0)

#property: water
water = {}
for cid in t.elements(ctyp) :
	water[cid] = 0

for wid in t.elements(wtyp) :
	water[wid] = 1
