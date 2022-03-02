from math import atan2,pi
from vplants.plantgl.math import Vector2,norm
from vplants.plantgl.algo import segmentIntersect

def find_cycles (mesh, scale, wid, cycle_len) :
	"""Find all cycles of len cycle_len and containing wid.
	
	A cycle is a list of elements at the given scale
	connected by regions such as the first element
	of the cycle is connected to the last element
	
	mesh: a topomesh
	scale: scale of elements that will form the cycles
	wid: common element to all returned cycles
	cycle_len: length of returned cycles
	"""
	cycles = set()
	#create a path for each region of the given element
	paths = [([wid],rid) for rid in mesh.regions(scale,wid)]
	
	#increase the size of each path up to cycle_len
	for i in xrange(cycle_len) :
		if len(paths) == 0 :
			return cycles
		#walk trough each path
		for j in xrange(len(paths) ) :
			path,extr = paths.pop(0)
			neighbors = set(mesh.borders(scale + 1,extr) )
			neighbors.remove(path[-1])
			#create as many path as there is of
			#new neighbor direction
			for nid in neighbors :
				if nid in path :#closed path
					if nid == path[0] and len(path) == cycle_len :
						path.sort() #necessary to avoid duplicated paths
						cycles.add(tuple(path) )
					else :#closed path but too small
						pass
				else :
					extrs = set(mesh.regions(scale,nid) )
					extrs.remove(extr)
					for rid in extrs :
						paths.append( (path + [nid],rid) )#new path
	
	#return
	return cycles
	
def find_smallest_cycle_around (mesh, pos, ref_point) :
	"""Find the smallest cycle in mesh around ref_point.

	A cycle is a list of elements at the given scale
	connected by borders such as the first element
	of the cycle is connected to the last element
	
	mesh: a topomesh
	pos: position of vertices of the mesh
	ref_point: a vector in space
	"""
	#find most proximal vertex of the mesh
	dist = [(norm(pos[pid] - ref_point),pid) for pid in mesh.wisps(0)]
	dist.sort()
	min_dist,min_pid = dist[0]
	
	#find most proximal edge connected to this vertex
	#TODO
	
	#try to find cycle strating from small ones
	cycle_len = 2
	while cycle_len < mesh.nb_wisps(0) :
		for cycle in find_cycles(mesh,0,eid,cycle_len) :
			pass

def is_intersection_2D (seg1, seg2) :
	"""Test wether an intersection exist
	between the two segments.
	
	seg1: a tuple (pt,pt)
	seg2: a tuple (pt,pt)
	"""
	return segmentIntersect(seg1[0],seg1[1],seg2[0],seg2[1])

def find_closed_path (mesh, point_cycle) :
	"""Test wether the cycle is closed.
	
	return the cycle of edges if successful
	"""
	if len(point_cycle) < 3 :
		return None
	
	pid_cycle = set(point_cycle)
	#init algo
	current_pid = iter(point_cycle).next()
	con_edges = [eid for eid in mesh.regions(0,current_pid) \
	             if len(set(mesh.borders(1,eid) ) & pid_cycle) == 2]
	if len(con_edges) != 2 :
		return None
	current_eid = con_edges[0]
	next_pid, = (pid for pid in mesh.borders(1,current_eid) \
	             if pid != current_pid)
	
	#walk
	first_pid = current_pid
	edge_cycle = [current_eid]
	while next_pid != first_pid :
		old_pid = current_pid
		current_pid = next_pid
		con_edges = [eid for eid in mesh.regions(0,current_pid) \
		             if len(set(mesh.borders(1,eid) ) & pid_cycle) == 2]
		if len(con_edges) != 2 :
			return None
		next_pid, = (pid for pid in mesh.borders(1,con_edges[0]) \
		             if pid != current_pid)
		if next_pid == old_pid :
			next_pid, = (pid for pid in mesh.borders(1,con_edges[1]) \
			             if pid != current_pid)
			edge_cycle.append(con_edges[1])
		else :
			edge_cycle.append(con_edges[0])
	
	#return
	return edge_cycle

def find_smallest_cycle_around (mesh, pos, ref_point, max_cycle_radius, seg_size_increase) :
	"""Find the smallest cycle in mesh around ref_point.

	A cycle is a list of elements at the given scale
	connected by borders such as the first element
	of the cycle is connected to the last element
	
	mesh: a topomesh
	pos: position of vertices of the mesh
	ref_point: a vector in space
	max_cycle_radius: this algorithm will consider only
	                  points at a distance smaller than
	                  this value to ref_point
	"""
	#change into natural coordinates instead of draw ones
	pos = dict( (pid,Vector2(vec[0],-vec[1]) ) for pid,vec in pos.iteritems() )
	ref_point = Vector2(ref_point[0],-ref_point[1])
	
	distances = dict( (pid,norm(vec - ref_point) ) for pid,vec in pos.iteritems() )
	
	radii = [int(i * max_cycle_radius / 10.) for i in xrange(11)]
	for radius in radii :
		#find proximal points
		pids = [pid for pid,d in distances.iteritems() if d < radius]
		
		#find all segments linking these points
		eids = set()
		for pid in pids :
			eids.update(mesh.regions(0,pid) )
		
		segments = {}
		for eid in eids :
			pid1,pid2 = mesh.borders(1,eid)
			seg_dir = pos[pid2] - pos[pid1]
			seg_dir.normalize()
			segments[eid] = (pos[pid1] - seg_dir * seg_size_increase,
			                 pos[pid2] + seg_dir * seg_size_increase)
		
		#for each point
		cycle = []
		for pid in pids :
			ref_seg = (ref_point,pos[pid])
			tested_segments = [seg for eid,seg in segments.iteritems() \
			                   if eid not in set(mesh.regions(0,pid) )]
			#test wether any segment intersect
			if any(is_intersection_2D(ref_seg,seg) for seg in tested_segments) :
				pass
			else :
				cycle.append(pid)
		#test wether this is a closed cycle
		edge_cycle = find_closed_path(mesh,cycle)
		if edge_cycle is not None :
			return edge_cycle
	
	#go for a geometrical solution
	print "geom",ref_point
	##########
	#find edges that still are good
	edges = set()
	last_cycle = set(cycle)
	for pid in last_cycle :
		for eid in mesh.regions(0,pid) :
			if len(set(mesh.borders(1,eid) ) & last_cycle) == 2 :
				edges.add(eid)
	
	if len(edges) == 0 :
		return None
	
	#sort according to cross product
	edge_prox = []
	for eid in edges :
		pid1,pid2 = mesh.borders(1,eid)
		prod = abs( (pos[pid1] - ref_point) ^ (pos[pid2] - ref_point) )
		edge_prox.append( (prod,eid) )
	
	edge_prox.sort(reverse = True)
	starting_eid = edge_prox[0][1]
	
	#rotation clockwise
	pid1,pid2 = mesh.borders(1,starting_eid)
	prod = (pos[pid1] - ref_point) ^ (pos[pid2] - ref_point)
	if prod < 0 :
		cycle = [pid1]
		front = (starting_eid,pid2,pid1)
	else :
		cycle = [pid2]
		front = (starting_eid,pid1,pid2)
	
	while front[1] != cycle[0] :
		last_eid,last_pid,prev_pid = front
		cycle.append(last_pid)
		#sort all possible paths to find the one
		#that makes the smallest angle
		angles = []
		ref_dir = pos[prev_pid] - pos[last_pid]
		for eid in mesh.regions(0,last_pid) :
			if eid != last_eid :
				pid, = set(mesh.borders(1,eid) ) - set([last_pid])
				cur_dir = pos[pid] - pos[last_pid]
				alpha = atan2(ref_dir ^ cur_dir,ref_dir * cur_dir)
				if alpha < 0 :
					alpha += 2 * pi
				angles.append( (alpha,eid) )
		
		angles.sort()
		last_eid = angles[0][1]
		prev_pid = last_pid
		last_pid, = set(mesh.borders(1,last_eid) ) - set([last_pid])
		front = (last_eid,last_pid,prev_pid)
	
	edge_cycle = find_closed_path(mesh,cycle)
	if edge_cycle is not None :
		return edge_cycle
	return None


