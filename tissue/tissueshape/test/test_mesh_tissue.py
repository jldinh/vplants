from numpy import array
from openalea.container import regular_grid
from openalea.tissueshape import tovec, from_mesh, add_graph_from_mesh


m = regular_grid( (2,3) )

t, (WALL, CELL) = from_mesh(m, [(1, "wall"), (2, "cell")] )
t.geometry().apply_geom_transfo(tovec)


for wid in t.elements(WALL) :
	print wid, t.position(wid)

for cid in t.elements(CELL) :
	print cid, t.position(cid)

add_graph_from_mesh(t, "c2c", CELL)
g = t.relation("c2c")

for vid in g :
	print vid

for eid in g.edges() :
	print eid, (g.source(eid), g.target(eid) )
