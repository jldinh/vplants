# -*- python -*-
#
#       simulation.template: example simulation package
#
#       Copyright 2006 INRIA - CIRAD - INRA  
#
#       File author(s): Jerome Chopard <jerome.chopard@sophia.inria.fr>
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
# 
#       OpenAlea WebSite : http://openalea.gforge.inria.fr
#

__doc__="""
non mandatory file to create a tissue
"""

__license__= "Cecill-C"
__revision__=" $Id: $ "
######################################
#
print "tissue creation"
#
######################################
from openalea.celltissue import Tissue

t=Tissue()

point = t.add_type("point")
wall = t.add_type("wall")
cell = t.add_type("cell")

wall_graph = t.add_relation("graph",(point,wall))
cell_graph = t.add_relation("graph",(cell,None))
mesh_id = t.add_relation("mesh",(point,wall,cell))

#properties
pos = {}
######################################
#
print "read coleochaete.svg"
#
######################################
from openalea.svgdraw import open_svg

f = open_svg("coleochaete.svg",'r')
sc = f.read()
f.close()
######################################
#
print "wall graph structure extraction"
#
######################################
g = t.relation(wall_graph)

vertex = {}

layer = sc.get_layer("vertices")
for elm in layer.elements() :
	vid = g.add_vertex()
	vertex[elm.id()] = vid
	pos[vid] = layer.global_pos2D(elm.center())

layer = sc.get_layer("walls")
for elm in layer.elements() :
	sid = vertex[elm.source()]
	tid = vertex[elm.target()]
	eid = g.add_edge(sid,tid)

######################################
#
print "cell graph structure extraction"
#
######################################
g = t.relation(cell_graph)

cellname = {}

layer = sc.get_layer("cells")
for elm in layer.elements() :
	cid = g.add_vertex()
	cellname[elm.id()] = cid
	pos[cid] = layer.global_pos2D(elm.center())

######################################
#
print "cycles extraction to create mesh"
#
######################################
from vplants.plantgl.math import Vector3,norm

g = t.relation(wall_graph)
order_max = 7
raw_cycles = set()
for pid in g.vertices() :
	paths = [[pid]]
	for i in xrange(order_max) :
		for j in xrange(len(paths)) :
			path = paths.pop(0)
			neighbors = set(g.neighbors(path[-1]))
			if len(path)>1 :
				neighbors.remove(path[-2])
			for nid in neighbors :
				if nid == path[0] :
					pth = list(path)
					pth.sort()
					raw_cycles.add( tuple(pth) )
				else :
					paths.append(path + [nid])

cycle_list = [(len(cycle),set(cycle)) for cycle in raw_cycles]
cycle_list.sort()

for ind,(l,cycle) in enumerate(cycle_list) :
	to_remove = []
	for i in xrange(ind+1,len(cycle_list)) :
		if len(cycle - cycle_list[i][1]) == 0 :
			to_remove.insert(0,i)
	for i in to_remove :
		del cycle_list[i]

cycles = []
for l,cycle in cycle_list :
	wall_cycle = set()
	for pid in cycle :
		for wid in g.out_edges(pid) :
			if g.target(wid) in cycle :
				wall_cycle.add(wid)
	cycles.append( (wall_cycle,cycle) )

mesh = t.relation(mesh_id)
#wall point link
for wid in g.edges() :
	mesh.link(1,wid,g.source(wid))
	mesh.link(1,wid,g.target(wid))

g = t.relation(cell_graph)
#cell wall link
for wall_cycle,cycle in cycles :
	bary = sum((pos[pid] for pid in cycle),Vector3())/len(cycle)
	dist = [(norm(pos[cid]-bary),cid) for cid in g.vertices()]
	dist.sort()
	cid = dist[0][1]
	for wid in wall_cycle :
		mesh.link(2,cid,wid)

#cell cell edge
g = t.relation(cell_graph)

for wid in mesh.wisps(1) :
	if mesh.nb_regions(1,wid) == 2 :
		cid1,cid2 = mesh.regions(1,wid)
		g.add_edge(cid1,cid2,wid)
######################################
#
print "tissue writing"
#
######################################
from openalea.celltissue import topen,ConfigFormat

#semantic associated with the tissue
cfg=ConfigFormat(globals())
cfg.add_section("tissue descr")
cfg.add("point")
cfg.add("wall")
cfg.add("cell")
cfg.add("wall_graph")
cfg.add("cell_graph")
cfg.add("mesh_id")

#formattage of positions to remove pgl.Vector2 dependency
pos = dict( (elmid,(vec[0],vec[1])) for elmid,vec in pos.iteritems() )

#writing
f=topen("tissue.zip",'w')
f.write(t)
f.write_config(cfg.config(),"config")
f.write(pos,"position","position of elements in the tissue")
f.close()


