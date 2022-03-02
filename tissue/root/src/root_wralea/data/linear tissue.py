""""
This script produce a linear line of cells ranging from a basal cell to
an apical one. Each cell is 10 micron. Pumps exists between two cells and are
oriented from basal to apical
"""
import sys

try :
	nb_cells = int(sys.argv[1])
except IndexError :
	msg = "you must pass the number of cells as argument to the script"
	raise UserWarning(msg)
except TypeError :
	msg = "you must pass the number of cells as argument to the script"
	raise UserWarning(msg)

##################################################
#
print "create tissue"
#
##################################################
from openalea.tissueshape import regular_grid,centroid

db = regular_grid( (nb_cells,1) )

t = db.tissue()
cfg = db.get_config("config")
mesh = db.get_topology("mesh_id")
pos = db.get_property("position")

cells = [(centroid(mesh,pos,2,cid)[0],cid) for cid in mesh.wisps(2)]
cells.sort()
cells = [cid for l,cid in cells]

border = {cells[0]:0,cells[-1]:1}
border_types = {0:"basal",1:"apical"}

cell_type = dict( (cid,1) for cid in cells)
cell_types = {0:"epiderm",
              1:"cortex",
              2:"endoderm",
              3:"pericycle",
              4:"vasculature"}

##################################################
#
print "scaling"
#
##################################################
from openalea.container import Quantity

pos = Quantity(dict( (pid,tuple(v * 10 for v in vec) ) \
                      for pid,vec in pos.iteritems() ),
               unit = "mum",
               type = "tuple")

##################################################
#
print "pumps"
#
##################################################
edge = t.add_type("edge")

graph_id = t.add_relation("graph",(cfg.CELL,edge) )
graph = t.relation(graph_id)

wall = {}
PIN = {}
for wid in mesh.wisps(1) :
	if mesh.nb_regions(1,wid) == 2 :
		cids = [(cells.index(cid),cid) for cid in mesh.regions(1,wid)]
		cids.sort()
		(l1,cid1),(l2,cid2) = cids
		
		eid = graph.add_edge(cid1,cid2)
		wall[eid] = wid
		PIN[eid] = 1
		
		eid = graph.add_edge(cid2,cid1)
		wall[eid] = wid

##################################################
#
print "geometrical properties"
#
##################################################
V = Quantity(dict( (cid,100) for cid in cells),
             unit = "mum2",
             type = "float")

S = Quantity(dict( (wid,10) for wid in mesh.wisps(1) ),
             unit = "mum",
             type = "float")

##################################################
#
print "write"
#
##################################################
from openalea.svgdraw import to_xml,from_xml
from openalea.tissueshape import add_graph_layer
from openalea.celltissue import ConfigItem

sc = from_xml(db.get_external_data("visual_descr.svg") )
add_graph_layer(sc)
db.set_external_data("visual_descr.svg",to_xml(sc) )

cfg.add_item(ConfigItem("EDGE",edge) )
cfg.add_item(ConfigItem("graph_id",graph_id) )
cfg.add_item(ConfigItem("cell_types",cell_types) )
cfg.add_item(ConfigItem("border",border_types) )

db.set_property("position",pos)

db.set_property("border",border)
db.set_description("border","type of border cells")

db.set_property("cell_type",cell_type)
db.set_description("cell_type","type of cells")

db.set_property("PIN",PIN)
db.set_description("PIN","1 for edges that bear some PIN")

db.set_property("wall",wall)
db.set_description("wall","wall associated to each edge")

db.set_property("V",V)
db.set_description("V","volume of cells")

db.set_property("S",S)
db.set_description("S","surface of walls")

db.write("linear%d.zip" % nb_cells)

##################################################
#
print "create svg"
#
##################################################
from numpy import array
from openalea.svgdraw import (SVGScene,SVGLayer,SVGGroup,
                              SVGSphere,SVGConnector,SVGPath,SVGText,
                              expand_path)

sca = 20.
sx = 10 * nb_cells * sca
sy = 10 * sca

sc = SVGScene(sx,sy)

###############
#
#	background
#
###############
lay = SVGLayer("background",sx,sy,"lay00")
sc.append(lay)

###############
#
#	legend
#
###############
lay = SVGLayer("legend",sx,sy,"lay01")
sc.append(lay)

#scale
gr = SVGGroup(100,100,"scale")
gr.translate(0,-100)

shp = SVGText(0,0,"scale: 10 mum",40,"scale_txt")
shp.set_fill( (0,0,0) )
gr.append(shp)
shp = SVGPath("scale_pth")
shp.move_to(0,20)
shp.line_to(10 * sca,20)
shp.set_fill(None)
shp.set_stroke( (0,0,0) )
shp.set_stroke_width(10)
gr.append(shp)

lay.append(gr)

#basal
gr = SVGGroup(100,100,"leg_basal")
gr.translate(10 * sca + 100,-100)

shp = SVGSphere(0,0,sca,sca,"leg_basal_shp")
shp.set_fill( (155,0,0) )
gr.append(shp)
shp = SVGText(2 * sca,10,"basal",40,"leg_basal_txt")
shp.set_fill( (0,0,0) )
gr.append(shp)

lay.append(gr)

#basal
gr = SVGGroup(100,100,"leg_apical")
gr.translate(10 * sca + 100,-50)

shp = SVGSphere(0,0,sca,sca,"leg_apical_shp")
shp.set_fill( (0,0,155) )
gr.append(shp)
shp = SVGText(2 * sca,10,"apical",40,"leg_apical_txt")
shp.set_fill( (0,0,0) )
gr.append(shp)

lay.append(gr)

#cell types
typ_colors = [(255,255,0),(255,0,0),(0,0,255),(0,255,0),(255,0,255)]

for typ,name in cell_types.iteritems() :
	gr = SVGGroup(100,100,"leg_%s" % name)
	gr.translate(10 * sca + 400,-250 + 50 * typ)
	
	shp = SVGSphere(0,0,sca,sca,"leg_%s_shp" % name)
	shp.set_fill(typ_colors[typ])
	gr.append(shp)
	shp = SVGText(2 * sca,10,name,40,"leg_%s_txt" % name)
	shp.set_fill( (0,0,0) )
	gr.append(shp)
	
	lay.append(gr)

###############
#
#	border
#
###############
lay = SVGLayer("border",sx,sy,"lay02")
sc.append(lay)

for cid,typ in border.iteritems() :
	x,y = sc.svg_pos(*(centroid(mesh,pos,2,cid) *sca) )
	shp = SVGSphere(x,y,1.4 * sca,1.4 * sca,"cell%d" % cid)
	if typ == 0 :
		shp.set_fill( (155,0,0) )
	else :
		shp.set_fill( (0,0,155) )
	lay.append(shp)

###############
#
#	cells
#
###############
lay = SVGLayer("cells",sx,sy,"lay03")
sc.append(lay)

for cid in mesh.wisps(2) :
	x,y = sc.svg_pos(*(centroid(mesh,pos,2,cid) *sca) )
	shp = SVGSphere(x,y,sca,sca,"cell%d" % cid)
	shp.set_fill( (255,0,0) )
	lay.append(shp)

###############
#
#	walls
#
###############
lay = SVGLayer("walls",sx,sy,"lay04")
sc.append(lay)

for pid,vec in pos.iteritems() :
	x,y = sc.svg_pos(*(array(vec) * sca) )
	shp = SVGSphere(x,y,0.2 * sca,0.2 * sca,"point%d" % pid)
	shp.set_fill( (0,255,0) )
	lay.append(shp)

for wid in mesh.wisps(1) :
	pid1,pid2 = mesh.borders(1,wid)
	shp = SVGConnector("point%d" % pid1,"point%d" % pid2,"wall%d" % wid)
	shp.set_fill(None)
	shp.set_stroke( (0,0,0) )
	shp.set_stroke_width(1)
	lay.append(shp)

###############
#
#	PIN
#
###############
lay = SVGLayer("PIN",sx,sy,"lay05")
sc.append(lay)

for eid in PIN :
	end = centroid(mesh,pos,1,wall[eid]) * sca
	cent = centroid(mesh,pos,2,graph.source(eid) ) * sca
	beg = (cent + end * 2) / 3.
	shp = SVGPath("pin%d" % eid)
	shp.move_to(*sc.svg_pos(*beg) )
	shp.line_to(*sc.svg_pos(*end) )
	shp.set_fill(None)
	shp.set_stroke( (255,0,0) )
	shp.set_stroke_width(0.3 * sca)
	lay.append(shp)

expand_path(sc)

##################################################
#
print "write svg"
#
##################################################
from openalea.svgdraw import open_svg

f = open_svg("linear%d.svg" % nb_cells,'w')
f.write(sc)
f.close()


