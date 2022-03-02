execfile("creation.py")

#topen write
from openalea.celltissue import topen

f = topen("tissue.zip",'w')

#write tissue
f.write(t)

#write properties
f.write(pos,"position","position of points")
f.write(compound,"compound","concentration of compound in cells")
f.write(water,"water","amount of water")

#write config
from openalea.celltissue import Config,ConfigItem

cfg = Config("topology")
cfg.add_item(ConfigItem("cell",ctyp) )
cfg.add_item(ConfigItem("wall",wtyp) )
cfg.add_item(ConfigItem("point",ptyp) )
cfg.add_item(ConfigItem("graph_id",graph_id) )
cfg.add_item(ConfigItem("mesh_id",mesh_id) )


f.write_config(cfg,"config")

#close tissue write
f.close()

#topen append
f = topen("tissue.zip",'a')

prop = dict( (cid,0.) for cid in t.elements(ctyp) )
f.write(prop,"prop","null property")

f.close()

#topen read
f = topen("tissue.zip",'r')

#read tissue
t,descr = f.read()

#read properties
pos,descr = f.read("position")
water,descr = f.read("water")

#read config
cfg = f.read_config("config")

#close tissue read
f.close()

#explore
for cid in t.elements(0) :
	print cid

#use cfg
for cid in t.elements(cfg.cell) :
	print cid

#tissuedb read
from openalea.celltissue import TissueDB

db = TissueDB()
db.read("tissue.zip")

#tissuedb explore
t = db.tissue()
cfg = db.get_config('config')
compound = db.get_property("compound")
print db.description("compound")

#tissuedb modify
#this works well
for cid in t.elements(cfg.cell) :
	compound[cid] = 0

#this requires to store the property back in the tissuedb
compound = dict( (cid,0) for cid in t.elements(cfg.cell) )
db.set_property("compound",compound)

#tissuedb write
db.write("tissue2.zip")

