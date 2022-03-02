##################################################
#
print "create tissue"
#
##################################################
from openalea.celltissue import Tissue

t = Tissue()
POINT = t.add_type("point")
CELL = t.add_type("cell")

mesh_id = t.add_relation("mesh",(POINT,CELL) )
m = t.relation(mesh_id)

pos = {}

point_id = {}
for i in xrange(6) :
	pid = m.add_wisp(0)
	pos[pid] =  i
	point_id[i] = pid

for i in xrange(5) :
	cid = m.add_wisp(1)
	for pid in (point_id[j] for j in (i,i + 1) ) :
		m.link(1,cid,pid)

###################################################
#
print "properties"
#
###################################################
gs = dict( (cid,cid * 0.1) for cid in m.wisps(1) )
V = dict( (cid,1.) for cid in m.wisps(1) )

###################################################
#
print "write tissue"
#
###################################################
from openalea.celltissue import ConfigFormat,topen

cfg = ConfigFormat(vars() )
cfg.add_section("elements types")
cfg.add("POINT")
cfg.add("CELL")
cfg.add("mesh_id")

f = topen("linear1D.zip",'w')
f.write(t)
f.write(pos,"position","position of points")
f.write(gs,"growth_speed","some property")
f.write(V,"volume","volume of each cell")
f.write_config(cfg.config(),"config")
f.close()

