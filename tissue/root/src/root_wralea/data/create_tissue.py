import sys
from os.path import splitext

filename = sys.argv[1]
outname = "%s.zip" % splitext(filename)[0]
##########################################
#
print "read svg file"
#
##########################################
from openalea.svgdraw import open_svg

f = open_svg(filename,'r')
sc = f.read()
f.close()

##########################################
#
print "read raw_mesh"
#
##########################################
from numpy import array
from openalea.container import read_topomesh,write_topomesh,Quantity

meshname = "%s.msh" % splitext(filename)[0]
try :
	raw_mesh,descr,props = read_topomesh(meshname,'max')
except IOError :
	import create_mesh
	raw_mesh,props = create_mesh.main(sc)
	
	write_topomesh(meshname,
	               raw_mesh,
	               "mesh extract from an svg drawing",
	               props)

X, = (prop[1] for prop in props[0] \
      if prop[0] == 'X')
Y, = (prop[1] for prop in props[0] \
      if prop[0] == 'Y')

raw_pos = Quantity(dict( (pid,array([X[pid],Y[pid] ]) ) \
                              for pid in raw_mesh.wisps(0) ),
                   X.unit(),
                   "array",
                   "position of points")

raw_svg_id, = (prop[1] for prop in props[2] \
               if prop[0] == 'svg_id')
##########################################
#
print "read PIN"
#
##########################################
from pickle import load,dump

PINname = "%s.PIN.pkl" % splitext(filename)[0]

try :
	PIN = load(open(PINname,'rb') )
except IOError :
	import find_pin
	PIN = find_pin.main(sc,raw_mesh,props)
	
	dump(PIN,open(PINname,'w') )

##########################################
#
print "create tissue"
#
##########################################
from openalea.celltissue import Tissue

tissue = Tissue()
POINT = tissue.add_type("point")
WALL = tissue.add_type("wall")
CELL = tissue.add_type("cell")
EDGE = tissue.add_type("edge")

mesh_id = tissue.add_relation("mesh",(POINT,WALL,CELL) )
graph_id = tissue.add_relation("graph",(CELL,EDGE) )

##########################################
#
print "fill mesh"
#
##########################################
mesh = tissue.relation(mesh_id)

trans = [{} for deg in xrange(3)]

#add wisps
for deg in xrange(3) :
	for wid in raw_mesh.wisps(deg) :
		trans[deg][wid] = mesh.add_wisp(deg)

#link wisps
for deg in xrange(1,3) :
	for wid in raw_mesh.wisps(deg) :
		for bid in raw_mesh.borders(deg,wid) :
			mesh.link(deg,trans[deg][wid],trans[deg - 1][bid])

pos = Quantity(dict( (trans[0][pid],vec) for pid,vec in raw_pos.iteritems() ),
               raw_pos.unit(),
               raw_pos.type(),
               raw_pos.description() )

svg_id = dict( (trans[2][cid],elmid) for cid,elmid in raw_svg_id.iteritems() )

##########################################
#
print "fill graph"
#
##########################################
graph = tissue.relation(graph_id)

wall = {}

for wid in mesh.wisps(1) :
	if mesh.nb_regions(1,wid) == 2 :
		cid1,cid2 = mesh.regions(1,wid)
		eid1 = graph.add_edge(cid1,cid2)
		wall[eid1] = wid
		eid2 = graph.add_edge(cid2,cid1)
		wall[eid2] = wid

##########################################
#
print "read legend"
#
##########################################
from numpy.linalg import norm
from openalea.svgdraw import SVGGroup,SVGSphere,SVGText,SVGPath

type_descr = None
scale = None

lay = sc.get_layer("legend")
if lay is not None :
	type_descr = {}
	for i,gr in enumerate(lay.elements() ) :
		if isinstance(gr,SVGGroup) :
			geom = None
			txt = None
			for elm in gr.elements() :
				if isinstance(elm,SVGText) :
					txt = elm.text()
				else :
					geom = elm
			if (geom is not None) \
			   and (txt is not None) :
				if "scale" in txt :
					if isinstance(geom,SVGPath) :
						pt0,pt1 = (array(tup) \
						   for tup in geom.polyline_ctrl_points() )
						length = norm(pt1 - pt0)
						scale_txt = txt.split(":")[1].strip().split(" ")
						sca = float(scale_txt[0])
						sca_unit = scale_txt[1]
						scale = (sca / length,sca_unit)
						print "scale",scale
					else :
						raise NotImplementedError("scale, don't know how to handle %s" % str(geom) )
				elif isinstance(geom,SVGSphere) :
					type_descr[geom.fill()] = (i,txt)
				else :
					print "legend",geom,txt

print type_descr
##########################################
#
print "read cell type"
#
##########################################
lay = sc.get_layer("cells")
inv_id = dict( (elmid,cid) for cid,elmid in svg_id.iteritems() )

cell_type = {}
cell_types = {}
cell_center = {}

for elm in lay.elements() :
	if isinstance(elm,SVGSphere) :
		cid = inv_id[elm.id()]
		state = elm.fill()
		if type_descr is None :
			cell_type[cid] = state
		else :
			typ,name = type_descr[state]
			cell_type[cid] = typ
			cell_types[typ] = name
		
		cell_center[cid] = array(elm.scene_pos(elm.center() ) )

##########################################
#
print "read other informations"
#
##########################################

def find_proximal_cell (point) :
	dist = [(norm(cent - point),cid) for cid,cent in cell_center.iteritems()]
	dist.sort()
	return dist[0][1]

props = {}
for lay in sc.layers() :
	if lay.name() not in ("background","legend","cells","walls","PIN") :
		prop = {}
		prop_types = {}
		for elm in lay.elements() :
			if isinstance(elm,SVGSphere) :
				print elm.scene_pos(elm.center() )
				cid = find_proximal_cell(elm.scene_pos(elm.center() ) )
				state = elm.fill()
				if type_descr is None :
					prop[cid] = state
				else :
					try :
						typ,name = type_descr[state]
						prop[cid] = typ
						prop_types[typ] = name
					except KeyError :
						prop[cid] = state
		props[lay.name()] = (prop,prop_types)

print props

##########################################
#
print "PIN"
#
##########################################
PINg = {}

for raw_cid,wids in PIN.iteritems() :
	cid = trans[2][raw_cid]
	for raw_wid in wids :
		wid = trans[1][raw_wid]
		for eid in graph.out_edges(cid) :
			if wall[eid] == wid :
				PINg[eid] = 1.

##########################################
#
print "geometry properties"
#
##########################################
from numpy import add
from openalea.tissueshape import face_surface_2D,edge_length

#change orientation of axes
for pid,vec in pos.iteritems() :
	pos[pid] = array(sc.natural_pos(vec[0],vec[1]) )

#center tissue and scale
sca = scale[0]
bary = reduce(add,(pos.itervalues() ) ) / len(pos)
pos = dict( (pid,(vec - bary) * sca) for pid,vec in pos.iteritems() )

#compute geometrical various properties
V = dict( (cid,face_surface_2D(mesh,pos,cid) ) for cid in mesh.wisps(2) )
S = dict( (wid,edge_length(mesh,pos,wid) ) for wid in mesh.wisps(1) )

##########################################
#
print "visual description"
#
##########################################
from openalea.svgdraw import to_xml,from_xml
from openalea.tissueshape import planar_mesh,add_graph_layer

sc = planar_mesh()
add_graph_layer(sc)
svg_data = to_xml(sc)

##########################################
#
print "create config"
#
##########################################
from openalea.celltissue import ConfigFormat,ConfigItem

cfg = ConfigFormat(vars() )
cfg.add_section("elements types")
cfg.add("POINT")
cfg.add("WALL")
cfg.add("CELL")
cfg.add("EDGE")
cfg.add("mesh_id")
cfg.add("graph_id")

cfg.add_section("prop types")
cfg.add("cell_types")

for propname,(prop,prop_type) in props.iteritems() :
	cfg.add_item(ConfigItem(propname,prop_type) )

cfg = cfg.config()

##########################################
#
print "write tissue file"
#
##########################################
from openalea.celltissue import topen
from openalea.tissueshape import totup

qpos = totup(pos)
qpos.set_unit(scale[1])
qS = Quantity(S,scale[1])
qV = Quantity(V,"%s2" % scale[1])

f = topen(outname,'w')
f.write(tissue)
f.write_config(cfg,"config")
f.write(qpos,"position","position of points")
f.write(cell_type,"cell_type","type of each cell")
for propname,(prop,prop_types) in props.iteritems() :
	f.write(prop,propname,"see svg file")
f.write(wall,"wall","wall corresponding to a given edge")
f.write(PINg,"PIN","Defined to 1 for edges loaded with PIN pumps")
f.write(qV,"V","Volume of each cell")
f.write(qS,"S","Surface of each wall")
f.write_file(svg_data,"visual_descr.svg")
f.close()





