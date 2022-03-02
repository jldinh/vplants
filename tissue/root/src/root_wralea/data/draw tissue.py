import sys
from os.path import splitext

filename = sys.argv[1]
outname = "%s.test.svg" % splitext(filename)[0]

##########################################
#
print "read tissue file"
#
##########################################
from vplants.plantgl.math import Vector2,norm
from openalea.celltissue import topen
from openalea.tissueshape import tovec

f = topen(filename,'r')
t,descr = f.read()
cfg = f.read_config("config")
pos,descr = f.read("position")
ctype,descr = f.read("cell_type")
PIN,descr = f.read("PIN")
wall,descr = f.read("wall")
f.close()

mesh = t.relation(cfg.mesh_id)
graph = t.relation(cfg.graph_id)
pos = tovec(pos)
R = max(norm(vec) for vec in pos.itervalues() )
dsize = R * 2
pos = dict( (pid,Vector2(R + vec.x,R - vec.y) ) for pid,vec in pos.iteritems() )
##########################################
#
print "draw verification image"
#
##########################################
from random import randint
from openalea.svgdraw import open_svg,SVGScene,SVGPath,SVGLayer,SVGSphere
from openalea.tissueshape import centroid
from tools import cell_geom

sc = SVGScene()
sc.set_size(dsize,dsize)

cell_cent = {}
#draw cells
lay = SVGLayer("cells",dsize,dsize)
sc.append(lay)
for cid in mesh.wisps(2) :
	try :
		pth = cell_geom(mesh,pos,cid,"cell%d" % cid)
		pth.set_fill( (randint(0,255),randint(0,255),randint(0,255) ) )
		lay.append(pth)
		cell_cent[cid] = centroid(mesh,pos,2,cid)
	except Exception :
		print "undefined cell %d" % cid

for vec in cell_cent.itervalues() :
	geom = SVGSphere(vec.x,vec.y,2,2)
	geom.set_fill( (0,0,0) )
	lay.append(geom)

#draw cell type
lay = SVGLayer("cell type",dsize,dsize)
sc.append(lay)

type_col = dict( (typ,(randint(0,255),randint(0,255),randint(0,255) ) ) \
                  for typ in cfg.cell_types)

for cid,typ in ctype.iteritems() :
	pth = cell_geom(mesh,pos,cid,"stcell%d" % cid)
	pth.set_fill(type_col[typ])
	lay.append(pth)

#draw walls
lay = SVGLayer("walls",dsize,dsize)
sc.append(lay)
wall_ind = 0
black = (0,0,0)
for wid in mesh.wisps(1) :
	pos0,pos1 = (pos[pid] for pid in mesh.borders(1,wid) )
	pth = SVGPath("wall%.4d" % wall_ind)
	wall_ind += 1
	pth.move_to(pos0.x,pos0.y)
	pth.line_to(pos1.x,pos1.y)
	pth.set_stroke(black)
	pth.set_stroke_width(1)
	lay.append(pth)
	
#draw PIN
lay = SVGLayer("PIN",dsize,dsize)
sc.append(lay)
pin_ind = 0
red = (125,0,0)
for eid,pump in PIN.iteritems() :
	wid = wall[eid]
	cid = graph.source(eid)
	pos0,pos1 = (pos[pid] for pid in mesh.borders(1,wid) )
	pos2 = (pos1 * 3 + cell_cent[cid]) / 4.
	pos3 = (pos0 * 3 + cell_cent[cid]) / 4.
	pth = SVGPath("pin%.4d" % pin_ind)
	pin_ind += 1
	pth.move_to(pos0.x,pos0.y)
	for vec in (pos1,pos2,pos3) :
		pth.line_to(vec.x,vec.y)
	pth.close()
	pth.set_fill(red)
	lay.append(pth)

f = open_svg(outname,'w')
f.write(sc)
f.close()

