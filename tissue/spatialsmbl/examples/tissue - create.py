#############################################
#
print "create tissue"
#
#############################################
from openalea.celltissue import Tissue

t = Tissue()

ctyp = t.add_type("cytoplasm")
wtyp = t.add_type("wall")
ptyp = t.add_type("point")

graph_id = t.add_relation("graph",(ctyp,wtyp) )
graph = t.relation(graph_id)

cells = [graph.add_vertex() for i in xrange(3)]
walls = [graph.add_edge(cells[i],cells[i + 1]) for i in (0,1)]

mesh_id = t.add_relation("mesh",(ptyp,wtyp,ctyp) )
mesh = t.relation(mesh_id)

for wid in graph.edges() :
	mesh.link(2,graph.source(wid),wid)
	mesh.link(2,graph.target(wid),wid)

#############################################
#
print "create properties"
#
#############################################
from random import random

#cytoplasm types
cell_types = ["endoderme","cortex"]
cell_type = dict( (cid,1) for cid in cells[1:])
cell_type[cells[0] ] = 0

#species
#A
A = dict( (cid,random() ) for cid in t.elements(ctyp) )
for wid in t.elements(wtyp) :
	A[wid] = random()

#B
B = dict( (cid,0) for cid,typ in cell_type.iteritems() if typ == 0)

#PIN
PIN = dict( (wid,random() ) for wid in t.elements(wtyp) )

#global parameters
#gamma

#local parameters
#alpha
alpha = dict( (cid,random() ) for cid in t.elements(ctyp) )

#beta
beta = dict( (cid,0.1) for cid in t.elements(ctyp) )

#S
S = dict( (wid,1.) for wid in t.elements(wtyp) )

#############################################
#
print "save tissue"
#
#############################################
from openalea.celltissue import topen,Config,ConfigItem

cfg = Config("topology")
cfg.add_item(ConfigItem("cell",ctyp) )
cfg.add_item(ConfigItem("wall",wtyp) )
cfg.add_item(ConfigItem("point",ptyp) )
cfg.add_item(ConfigItem("graph_id",graph_id) )
cfg.add_item(ConfigItem("mesh_id",mesh_id) )
cfg.add_item(ConfigItem("cell_types",cell_types) )

f = topen("tissue.zip",'w')
f.write(t)
f.write_config(cfg,"config")
f.write(cell_type,"cell_type","type of cells")
f.write(A,"A","quantities of A")
f.write(B,"B","quantities of B")
f.write(PIN,"PIN","quantities of PIN in wall")
f.write(alpha,"alpha","used for reaction")
f.write(beta,"beta","used for reaction")
f.write(S,"S","surface of walls")
f.close()

