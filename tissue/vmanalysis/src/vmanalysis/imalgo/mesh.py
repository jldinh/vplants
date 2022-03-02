from openalea.container import Topomesh,DataProp

def find_edge (edges, pid1, pid2, current_edge_list) :
	if pid1 not in point_vertex :
		eid, = set(mesh.regions(0,pid1)) & edges
		current_edge_list.insert(0,eid)
		edges.remove(eid)
		pid, = set(mesh.borders(1,eid)) - set([pid1])
		return find_edge(edges,pid,pid2,current_edge_list)
	elif pid2 not in point_vertex :
		eid, = set(mesh.regions(0,pid2)) & edges
		current_edge_list.append(eid)
		edges.remove(eid)
		pid, = set(mesh.borders(1,eid)) - set([pid2])
		return find_edge(edges,pid1,pid,current_edge_list)
	else :
		return pid1,pid2

def ordered_pids (mesh, edges) :
	"""
	order points jumping from on edge to another
	hopefuly, all edges in edges are connected
	"""
	edges = set(edges)
	#take a seed
	eid = edges.pop()
	pid_list = list(mesh.borders(1,eid))
	#go on one side
	front = [pid_list[-1]]
	while len(front) > 0 :
		pid = front.pop(0)
		for eid in mesh.regions(0,pid) :
			if eid in edges :
				npid, = set(mesh.borders(1,eid) ) - set([pid])
				front.append(npid)
				edges.remove(eid)
				pid_list.append(npid)
	#go on the other side
	front = [pid_list[0]]
	while len(front) > 0 :
		pid = front.pop(0)
		for eid in mesh.regions(0,pid) :
			if eid in edges :
				npid, = set(mesh.borders(1,eid) ) - set([pid])
				front.append(npid)
				edges.remove(eid)
				pid_list.insert(0,npid)
	#test
	assert len(edges) == 0
	#return
	return pid_list

def ordered_eids (mesh, pids) :
	"""Find ordered list of edges connecting given pids.
	
	assert pids is a sorted list of pids
	"""
	pids = list(pids)
	cur_pid = pids.pop(0)
	eids = []
	
	while len(pids) > 0 :
		next_pid = pids.pop(0)
		eid, = set(mesh.regions(0,cur_pid) ) & set(mesh.regions(0,next_pid) )
		eids.append(eid)
		cur_pid = next_pid
		
	return eids

def _connex_part (mesh, edges) :
	front = [edges[0]]
	part = set(front)
	while len(front) > 0 :
		eid = front.pop(0)
		for neid in mesh.border_neighbors(1,eid) :
			if (neid in edges) and (neid not in part) :
				part.add(neid)
				front.append(neid)
	return part

def connex_components (mesh, edges) :
	edges = list(edges)
	while len(edges) > 0 :
		part = _connex_part(mesh,edges)
		for eid in part :
			edges.remove(eid)
		yield part

def subdivide_edge (mesh, edges, pid1, pid2, pid3) :
	"""Subdivide the list of edges
	in 2 components, one between pid1 and pid2
	the other between pid2 and pid3.
	"""
	edges = set(edges)
	#part1
	eid1, = set(mesh.regions(0,pid1) ) & edges#TODO what if > 1
	pid, = set(mesh.borders(1,eid1) ) - set([pid1])
	part1 = set([eid1])
	if pid != pid2 :
		front = [(eid1,pid)]
		while len(front) > 0 :
			eid,pid = front.pop(0)
			neid, = (set(mesh.regions(0,pid) ) & edges) - part1
			npid, = set(mesh.borders(1,neid) ) - set([pid])
			part1.add(neid)
			if npid != pid2 :
				front.append( (neid,npid) )
	
	#part2
	eid1, = set(mesh.regions(0,pid3) ) & edges#TODO what if > 1
	pid, = set(mesh.borders(1,eid1) ) - set([pid3])
	part2 = set([eid1])
	if pid != pid2 :
		front = [(eid1,pid)]
		while len(front) > 0 :
			eid,pid = front.pop(0)
			neid, = (set(mesh.regions(0,pid) ) & edges) - part2
			npid, = set(mesh.borders(1,neid) ) - set([pid])
			part2.add(neid)
			if npid != pid2 :
				front.append( (neid,npid) )
	
	#return
	return part1,part2

def subdivide_circular_edge (mesh, ordered_edges, pid1, pid2, pid3) :
	"""Subdivide the list of edges
	edges must be ordered so that pid1 is in border of ordered_edges[0]
	in 3 components, one between pid1 and pid2
	another between pid2 and pid3
	the last between pid2 and pid3
	"""
	assert pid1 in mesh.borders(1,ordered_edges[0])
	
	#part1
	part = [pid1]
	cur_pid = pid1
	for eid in ordered_edges :
		pid, = set(mesh.borders(1,eid) ) - set([cur_pid])
		part.append(pid)
		if pid in (pid2,pid3,pid1) :
			yield part
			part = [pid]
		cur_pid = pid

def get_point (mesh, coords, pos_to_pid, X, Y, Z) :
	try :
		pid = pos_to_pid[coords]
	except KeyError :
		pid = mesh.add_wisp(0)
		pos_to_pid[coords] = pid
		X[pid] = coords[0]
		Y[pid] = coords[1]
		Z[pid] = coords[2]
	
	return pid

def get_edge (mesh, pid1, pid2, pt_to_edge) :
	key = (min(pid1,pid2),max(pid1,pid2) )
	try :
		eid = pt_to_edge[key]
	except KeyError :
		eid = mesh.add_wisp(1)
		mesh.link(1,eid,pid1)
		mesh.link(1,eid,pid2)
		pt_to_edge[key] = eid
	
	return eid

def make_edges (mesh, fid, pid_list, pt_to_edge) :
	pid_list.append(pid_list[0])
	for i in xrange(4) :
		eid = get_edge(mesh,
		               pid_list[i],
		               pid_list[i + 1],
		               pt_to_edge)
		mesh.link(2,fid,eid)

def cell_mesh (mat, cid, logout, cell_coords = None) :
	"""Construct the mesh for a given cell
	"""
	imax,jmax,kmax = mat.shape
	
	if cell_coords is None :
		logout.write("find cell coords\n")
		logout.write("nb slices: %d\n" % kmax)
		cell_coords = []
		for z in xrange(kmax) :
			logout.write("%d," % z)
			logout.flush()
			for x in xrange(imax) :
				for y in xrange(jmax) :
					if mat[x,y,z] == cid :
						cell_coords.append( (x,y,z) )
		logout.write("\n")
		
	mesh = Topomesh(2,"max")
	X = DataProp(type='int',unit='pix')
	Y = DataProp(type='int',unit='pix')
	Z = DataProp(type='int',unit='pix')
	face_index = DataProp(type='int',unit='cid')
	pos_to_pid = {}
	pt_to_edge = {}
	for x,y,z in cell_coords :
		##########################
		#
		#	X
		#
		##########################
		if (x == 0) \
		   or (x > 0 and mat[x - 1,y,z] != cid) :
			#add face
			fid = mesh.add_wisp(2)
			if x == 0 :
				face_index[fid] = 0
			else :
				face_index[fid] = mat[x - 1,y,z] + 5
			#add points
			pid_list = []
			for coords in [(x,y,z),
			               (x,y + 1,z),
			               (x,y + 1,z + 1),
			               (x,y,z + 1)] :
				pid = get_point(mesh,coords,pos_to_pid,X,Y,Z)
				pid_list.append(pid)
			#add edges
			make_edges(mesh,fid,pid_list,pt_to_edge)
	
		if (x == (imax - 1) ) \
		   or (x < (imax - 1) and mat[x + 1,y,z] != cid) :
			#add face
			fid = mesh.add_wisp(2)
			if x == (imax - 1) :
				face_index[fid] = 1
			else :
				face_index[fid] = mat[x + 1,y,z] + 5
			#add points
			pid_list = []
			for coords in [(x + 1,y,z),
			               (x + 1,y + 1,z),
			               (x + 1,y + 1,z + 1),
			               (x + 1,y,z + 1)] :
				pid = get_point(mesh,coords,pos_to_pid,X,Y,Z)
				pid_list.append(pid)
			#add edges
			make_edges(mesh,fid,pid_list,pt_to_edge)
		##########################
		#
		#	Y
		#
		##########################
		if (y == 0) \
		   or (y > 0 and mat[x,y - 1,z] != cid) :
			#add face
			fid = mesh.add_wisp(2)
			if y == 0 :
				face_index[fid] = 2
			else :
				face_index[fid] = mat[x,y - 1,z] + 5
			#add points
			pid_list = []
			for coords in [(x,y,z),
			               (x + 1,y,z),
			               (x + 1,y,z + 1),
			               (x,y,z + 1)] :
				pid = get_point(mesh,coords,pos_to_pid,X,Y,Z)
				pid_list.append(pid)
			#add edges
			make_edges(mesh,fid,pid_list,pt_to_edge)
	
		if (y == (jmax - 1) ) \
		   or (y < (jmax - 1) and mat[x,y + 1,z] != cid) :
			#add face
			fid = mesh.add_wisp(2)
			if y == (jmax - 1) :
				face_index[fid] = 3
			else :
				face_index[fid] = mat[x,y + 1,z] + 5
			#add points
			pid_list = []
			for coords in [(x,y + 1,z),
			               (x + 1,y + 1,z),
			               (x + 1,y + 1,z + 1),
			               (x,y + 1,z + 1)] :
				pid = get_point(mesh,coords,pos_to_pid,X,Y,Z)
				pid_list.append(pid)
			#add edges
			make_edges(mesh,fid,pid_list,pt_to_edge)
	
		##########################
		#
		#	Z
		#
		##########################
		if (z == 0) \
		   or (z > 0 and mat[x,y,z - 1] != cid) :
			#add face
			fid = mesh.add_wisp(2)
			if z == 0 :
				face_index[fid] = 4
			else :
				face_index[fid] = mat[x,y,z - 1] + 5
			#add points
			pid_list = []
			for coords in [(x,y,z),
			               (x + 1,y,z),
			               (x + 1,y + 1,z),
			               (x,y + 1,z)] :
				pid = get_point(mesh,coords,pos_to_pid,X,Y,Z)
				pid_list.append(pid)
			#add edges
			make_edges(mesh,fid,pid_list,pt_to_edge)
	
		if (z == (kmax - 1) ) \
		   or (z < (kmax - 1) and mat[x,y,z + 1] != cid) :
			#add face
			fid = mesh.add_wisp(2)
			if z == (kmax - 1) :
				face_index[fid] = 5
			else :
				face_index[fid] = mat[x,y,z + 1] + 5
			#add points
			pid_list = []
			for coords in [(x,y,z + 1),
			               (x + 1,y,z + 1),
			               (x + 1,y + 1,z + 1),
			               (x,y + 1,z + 1)] :
				pid = get_point(mesh,coords,pos_to_pid,X,Y,Z)
				pid_list.append(pid)
			#add edges
			make_edges(mesh,fid,pid_list,pt_to_edge)
	
	props = [[("X",X),("Y",Y),("Z",Z)]
	         ,[]
	         ,[("face_index",face_index)] ]
	return mesh,props

