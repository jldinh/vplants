#open
from openalea.celltissue import TissueDB

db = TissueDB()
db.read("tissue.zip")

#tissue walk
tissue = db.tissue()
cfg = db.get_config("config")

for cid in tissue.elements(cfg.cell) :
	print cid

#graph walk
graph = tissue.relation(cfg.graph_id)

for cid in graph.vertices() :
	print cid

#mesh walk
mesh = tissue.relation(cfg.mesh_id)

for cid in mesh.wisps(2) :
	print cid

#property walk
water = db.get_property("water")

for elmid,q in water.iteritems() :
	if q > 0.5 :
		print elmid,tissue.type_name(tissue.type(elmid) )

#water wall content
for cid in tissue.elements(cfg.cell) :
	q = 0
	for wid in mesh.borders(2,cid) :
		q += water[wid]
	print cid,q
