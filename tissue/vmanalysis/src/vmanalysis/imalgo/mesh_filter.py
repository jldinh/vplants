from math import radians,cos
from vplants.plantgl.math import Vector4,norm
from vplants.plantgl.scenegraph import NurbsCurve

###############################################################
#
#	mesh edition
#
###############################################################
def is_collapse_geom_allowed (mesh, pos, eid) :
	"""Test wether the edge can be safely collapsed.
	
	call is_collapse_topo_allowed first
	"""
	return True

def is_flip_geom_allowed (mesh, pos, eid) :
	"""	test wether the flipping of the edge is geometrically allowed.
	
	call is_flip_topo_allowed before
	return True if the two faces are in a plane
	"""
	#find points
	pts = set()
	for fid in mesh.regions(1,eid) :
		pts.update(mesh.borders(2,fid,2) )
	pid1,pid2 = mesh.borders(1,eid)
	pid3,pid4 = pts - set( (pid1,pid2) )
	#test wether the flipped edge is inside the
	#two triangles
	flipped_edge_dir = pos[pid4] - pos[pid3]
	v1 = (pos[pid1] - pos[pid3]) ^ flipped_edge_dir
	v2 = flipped_edge_dir ^ (pos[pid2] - pos[pid3])
	if v1 * v2 < 0 :
		return False
	#test the angle between the two triangles
	#find angle
	n1 = (pos[pid1] - pos[pid3]) ^ (pos[pid2] - pos[pid3])
	if n1.normalize() < 1e-3 :
		return True
	n2 = (pos[pid1] - pos[pid4]) ^ (pos[pid2] - pos[pid4])
	if n2.normalize() < 1e-3 :
		return True
	if (n1 * n2) < cos(radians(30)) :
		return False
	#return
	return True

###############################################################
#
#	find super wisp
#
###############################################################
def edge_points (mesh, ordered_edge_list) :
	"""
	return a list of ordered pids
	"""
	if len(ordered_edge_list) == 1 :
		return list(mesh.borders(1,ordered_edge_list[0]) )
	pid1, = set(mesh.borders(1,ordered_edge_list[0])) - set(mesh.borders(1,ordered_edge_list[1]))
	pts = [pid1]
	for eid in ordered_edge_list :
		pid, = set(mesh.borders(1,eid)) - set([pts[-1]])
		pts.append(pid)
	return pts

def edge_curve (pos, pids) :
	"""
	return the nurbs that represent these edges
	"""
	if len(pids) == 1 :
		raise UserWarning("not enough points")
	deg = min(3,len(pids) - 1)
	return NurbsCurve([Vector4(pos[pid],1.) for pid in pids],deg)

def crv_dist (crv1, crv2) :
	"""
	euclidian mean distance between two curves
	"""
	nb = 100.
	g1 = crv1.getArcLengthToUMapping()
	g2 = crv2.getArcLengthToUMapping()
	d = [(crv1.getPointAt(g1(i/nb)) - crv2.getPointAt(g2(i/nb))) for i in xrange(int(nb) + 1)]
	return sum(norm(v) for v in d) / nb

def simplify_border (mesh, pos, ordered_edge_list, tol) :
	"""
	collapse some edges in edge_list
	with respect to overall geometry
	and the given tolerance
	"""
	edges = list(ordered_edge_list)
	#find initial geometry
	initial_crv = edge_curve(pos,edge_points(mesh,edges))
	#compute
	err = 0.
	while err < tol and len(edges) > 2 :
		print edges
		#order edges by increasing errors
		edge_err = []
		pids = edge_points(mesh,edges)
		for i,eid in enumerate(edges[1:-1]) :
			tmp_pids = pids[:(i+1)] + pids[(i+2):]
			crv = edge_curve(pos,tmp_pids)
			edge_err.append( (crv_dist(initial_crv,crv),eid) )
		edge_err.sort()
		err = edge_err[0][0]
		print "err",err,edge_err[0][1]
		if err < tol :
			eid = edge_err[0][1]
			edges.remove(eid)
			collapse_edge(mesh,pos,eid)
			#remove other edges if also remove by collapse algorithm
			for i in xrange(len(edges)-1,-1,-1) :
				if not mesh.has_wisp(1,edges[i]) :
					pid1 = pids[i]
					if not mesh.has_wisp(0,pid1) :
						pid1 = pids[i-1]
					pid2 = pids[i+1]
					if not mesh.has_wisp(0,pid2) :
						pid2 = pids[i+2]
					neid, = set(mesh.regions(0,pid1)) & set(mesh.regions(0,pid2))
					print "remove %d by %d" % (edges[i],neid)
					edges[i] = neid
	return edges
		



