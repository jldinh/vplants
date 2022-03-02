from openalea.celltissue import Tissue

t = Tissue()

CELL = t.add_type("cell")

t.add_element(CELL)

t.add_relation("graph",(CELL,None) )



t = Tissue()
nbcells=10
nbneigh=5

CELL = t.add_type("cell")
WALL = t.add_type("wall")
EDGE = t.add_type("edge")
VERTEX = t.add_type("vertex")

CELL_WALL = t.add_relation("mesh",(CELL,WALL) )
WALL_EDGE = t.add_relation("mesh",(WALL, EDGE) )
EDGE_VERTEX = t.add_relation("mesh",(EDGE,VERTEX) )

for i in range(0, nbcells):
	t.add_wisp(2,CELL)

for c in t.elements(CELL):
	rel=t.relation(CELL_WALL)
	for i in range(0,nbneigh):
		w=t.add_wisp(1,WALL)
		print w
		rel.link(2,c,w)





















