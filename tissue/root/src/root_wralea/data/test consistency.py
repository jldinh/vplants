import sys
from vplants.plantgl.math import Vector2,norm
from openalea.svgdraw import open_svg,SVGSphere,SVGConnector,SVGPath

filename = sys.argv[1]

###########################################
#
print "read"
#
###########################################
f = open_svg(filename,'r')
sc = f.read()
f.close()

###########################################
#
print "layers"
#
###########################################
for layer_name in ("walls","cells","PIN") :
	if sc.get_layer(layer_name) is None :
		print "\tlayer '%s' is not defined" % layer_name

###########################################
#
print "cells"
#
###########################################
lay = sc.get_layer("cells")

cell_pos = []

for elm in lay.elements() :
	if isinstance(elm,SVGSphere) :
		cell_pos.append( (elm.id(),Vector2(*elm.scene_pos(elm.center() ) ) ) )
	else :
		print "\telement '%s' is not in the right layer" % elm.id()

nb = len(cell_pos)

for i,(cid1,v1) in enumerate(cell_pos) :
	for j in xrange(i + 1,nb) :
		cid2,v2 = cell_pos[j]
		if norm(v2 - v1) < 1. :
			print "cell '%s' and cell '%s' are superposed" % (cid1,cid2)

###########################################
#
print "walls"
#
###########################################
lay = sc.get_layer("walls")

point_pos = {}
walls = []

for elm in lay.elements() :
	if isinstance(elm,SVGSphere) :
		point_pos[elm.id()] = Vector2(*elm.scene_pos(elm.center() ) )
	elif isinstance(elm,SVGConnector) :
		walls.append(elm)
	else :
		print "\telement '%s' is not in the right layer" % elm.id()

points = list(point_pos)
nb = len(point_pos)

for i,pid1 in enumerate(points) :
	v1 = point_pos[pid1]
	for j in xrange(i + 1,nb) :
		pid2 = points[j]
		v2 = point_pos[pid2]
		if norm(v2 - v1) < 1. :
			print "point '%s' and point '%s' are superposed" % (pid1,pid2)

for elm in walls :
	if elm.source() is None :
		print "\twall '%s' has no source" % elm.id()
	elif elm.source() not in point_pos :
		print "\tsource '%s' of element '%s' do not exist in this layer" % (elm.source(),elm.id() )
		#points.append(elm.source() )
	if elm.target() is None :
		print "\twall '%s' has no target" % elm.id()
	elif elm.target() not in point_pos :
		print "\ttarget '%s' of element '%s' do not exist in this layer" % (elm.target(),elm.id() )
		#points.append(elm.target() )
	
	if elm.source() == elm.target() :
		print "source and target superposed for '%s'" % elm.id()

wall_extr = {}
point_connections = dict( (pid,[]) for pid in points)

for elm in walls :
	sid = elm.source()
	tid = elm.target()
	if sid is not None and tid is not None :
		try :
			point_connections[sid].append(elm.id() )
		except KeyError :
			point_connections[sid] = [elm.id()]
		try :
			point_connections[tid].append(elm.id() )
		except KeyError :
			point_connections[tid] = [elm.id()]
		key = (min(sid,tid),max(sid,tid) )
		try :
			wid = wall_extr[key]
			print "\twall '%s' and wall '%s' are superposed" % (wid,elm.id() )
		except KeyError :
			wall_extr[key] = elm.id()

for pid,wids in point_connections.iteritems() :
	if len(wids) == 0 :
		print "\tpoint '%s' is not connected" % pid
	elif len(wids) == 1 :
		print "\tpoint '%s' is connected only to wall '%s'" % (pid,wids[0])

###########################################
#
print "PIN"
#
###########################################
lay = sc.get_layer("PIN")

path_extr = []

for elm in lay.elements() :
	if isinstance(elm,SVGPath) :
		#arrow cap
		try :
			marker = elm.get_style("marker-end")
			if marker == "none" :
				print "\tpump '%s' has no end marker" % elm.id()
			elif "arrow" not in marker.lower() :
				print "\tend marker of element '%s' is not an arrow" % elm.id()
		except KeyError :
			print "\tpump '%s' has no end marker" % elm.id()
		#segment definition
		seg = tuple(Vector2(*elm.scene_pos(pt) )  for pt in elm.polyline_ctrl_points() )
		if len(seg) != 2 :
			print "\tpump '%s' is not a segment" % elm.id()
		else :
			path_extr.append( (elm.id(),) + seg )
	else :
		print "\telement '%s' is not in the right layer" % elm.id()

nb = len(path_extr)

for i,(pid1,v1,v2) in enumerate(path_extr) :
	for j in xrange(i + 1,nb) :
		pid2,v3,v4 = path_extr[j]
		if (norm(v1 - v3) + norm(v2 - v4) ) < 1. :
			print "\tpump '%s' and pump '%s' are superposed" % (pid1,pid2)

###########################################
#
print "statistiques"
#
###########################################
print "nb cells: %d" % len(cell_pos)
print "nb walls: %d" % len(walls)
print "nb_points: %d" % len(points)

size_max = 0.
for pid1,pid2 in wall_extr :
	try :
		size_max = max(size_max,norm(point_pos[pid1] - point_pos[pid2]) )
	except KeyError :
		pass

print "max wall size %f" % size_max
