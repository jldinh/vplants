from openalea.container import regular_grid
from openalea.celltissue import topen
from openalea.tissueshape import from_mesh, add_graph_from_mesh

############################################################
#
print "write"
#
############################################################
t1, (WALL, CELL) = from_mesh(regular_grid( (2,3) ), [(1, "wall"), (2, "cell")] )
add_graph_from_mesh(t1, "c2c", CELL)
g1 = t1.relation("c2c")

f = topen("test.zip", 'w')
f.write(t1)
f.close()


############################################################
#
print "read"
#
############################################################
f = topen("test.zip", 'r')
t2 = f.read()
f.close()


assert t2.type_name(WALL) == "wall"
assert t2.type_name(CELL) == "cell"

assert set(t1.elements(WALL) ) == set(t2.elements(WALL) )
assert set(t1.elements(CELL) ) == set(t2.elements(CELL) )

g2 = t2.relation("c2c")

assert set(g1.vertices() ) == set(g2.vertices() )
assert set(g1.edges() ) == set(g2.edges() )






