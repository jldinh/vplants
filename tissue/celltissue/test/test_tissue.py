from openalea.celltissue import Tissue

t = Tissue()

def estr (eid) :
	return "%s (%d)" % (t.type_name(t.type(eid) ), eid)

CELL = t.add_type("cell")
WALL = t.add_type("wall")

print tuple(t.types() )
print [t.type_name(tid) for tid in t.types()]

DMY = t.add_type("dmy")
print [t.type_name(tid) for tid in t.types()]
t.set_type_name(DMY, "toto")
print [t.type_name(tid) for tid in t.types()]

t.remove_type(DMY)
print [t.type_name(tid) for tid in t.types()]


cid1 = t.add_element(CELL)
cid2 = t.add_element(CELL)
wid = t.add_element(WALL)

print [estr(eid) for eid in t.elements()]
print t.nb_elements()
print [estr(eid) for eid in t.elements(CELL)]
print t.nb_elements(CELL)

dmy = t.add_element(CELL)
print [estr(eid) for eid in t.elements(CELL)]
t.remove_element(dmy)
print [estr(eid) for eid in t.elements(CELL)]


rel = t.add_relation("c2c", CELL, CELL, WALL)
print rel
print tuple(t.relations(CELL) )
print tuple(t.relations(WALL) )

print [estr(vid) for vid in rel.vertices()]
print [estr(eid) for eid in rel.edges()]

rel.add_edge(cid1, cid2, wid)
print [estr(vid) for vid in rel.vertices()]
print [estr(eid) for eid in rel.edges()]

dmy = rel.add_vertex()
print [estr(vid) for vid in rel.vertices()]
print [estr(eid) for eid in rel.edges()]

dmy_eid = rel.add_edge(cid1, dmy)
print [estr(vid) for vid in rel.vertices()]
print [estr(eid) for eid in rel.edges()]

rel.remove_vertex(dmy)
print [estr(vid) for vid in rel.vertices()]
print [estr(eid) for eid in rel.edges()]

print [estr(eid) for eid in t.elements(CELL)]
print [estr(eid) for eid in t.elements(WALL)]
t.remove_element(dmy_eid)
print [estr(eid) for eid in t.elements(CELL)]
print [estr(eid) for eid in t.elements(WALL)]













