##########################################
#
print "create tissue"
#
##########################################
from openalea.celltissue import Tissue

t = Tissue()
ctyp = t.add_type("cell")
wtyp = t.add_type("wall")
ptyp = t.add_type("point")

mesh_id = t.add_relation("mesh",(ptyp,wtyp,ctyp) )
mesh = t.relation(mesh_id)

##########################################
#
print "open svg file"
#
##########################################
from openalea.svgdraw import open_svg

f = open_svg("tissue.svg",'r')
sc = f.read()
f.close()

trans = {}

##########################################
#
print "find cell centers"
#
##########################################
from openalea.svgdraw import SVGSphere

cell_pos = {}
lay = sc.get_layer("cells")
for elm in lay.elements() :
	if isinstance(elm,SVGSphere) :
		cid = mesh.add_wisp(2)
		trans[elm.id()] = cid
		cell_pos[cid] = sc.natural_pos(*elm.scene_pos(elm.center() ) )

##########################################
#
print "read vertices"
#
##########################################
from openalea.svgdraw import SVGSphere

pos = {}
lay = sc.get_layer("walls")
for elm in lay.elements() :
	if isinstance(elm,SVGSphere) :
		pid = mesh.add_wisp(0)
		trans[elm.id()] = pid
		pos[pid] = sc.natural_pos(*elm.scene_pos(elm.center() ) )

##########################################
#
print "read walls"
#
##########################################
from openalea.svgdraw import SVGConnector

lay = sc.get_layer("walls")
for elm in lay.elements() :
	if isinstance(elm,SVGConnector) :
		wid = mesh.add_wisp(1)
		trans[elm.id()] = wid
		mesh.link(1,wid,trans[elm.source()])
		mesh.link(1,wid,trans[elm.target()])

##########################################
#
print "find cells as cycles in the mesh"
#
##########################################
from openalea.tissueshape import edge_loop_around

for cid,ref_point in cell_pos.iteritems() :
	for eid in edge_loop_around(mesh,pos,ref_point) :
		mesh.link(2,cid,eid)

##########################################
#
print "save tissue"
#
##########################################
from openalea.celltissue import topen,Config,ConfigItem

cfg = Config("topology")
cfg.add_item(ConfigItem("cell",ctyp) )
cfg.add_item(ConfigItem("wall",wtyp) )
cfg.add_item(ConfigItem("point",ptyp) )
cfg.add_item(ConfigItem("mesh_id",mesh_id) )

f = topen("tissue.zip",'w')
f.write(t)
f.write_config(cfg,"config")
f.write(cell_pos,"cell_pos","position of the center of cells")
f.write(pos,"position","position of points")
f.close()









