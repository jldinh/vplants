from openalea.container import Quantity
from openalea.celltissue import Tissue

t = Tissue()
POINT = t.add_type("point")
WALL = t.add_type("wall")
CELL = t.add_type("cell")

mesh_id = t.add_relation("mesh",(POINT,WALL,CELL) )
tmesh = t.relation(mesh_id)

#properties
pos = Quantity({},"pix","tuple","position of vertices")

#fill mesh
trans = {}
for pid in mesh.wisps(0) :
	tpid = tmesh.add_wisp(0)
	trans[pid] = tpid
	pos[tpid] = tuple(vertex_pos[pid])

for deg in (1,2) :
	tr = {}
	for wid in mesh.wisps(deg) :
		twid = tmesh.add_wisp(deg)
		tr[wid] = twid
		for bid in mesh.borders(deg,wid) :
			tmesh.link(deg,twid,trans[bid])
	trans = tr

