"""Triangulate a set of points
"""

from openalea.container import Topomesh
from delaunay import Triangulation

from geometry import centroid,\
                     circum_center2D,circum_center3D

def delaunay2D (points) :
	"""Construct a delaunay triangulation
	
	:Parameters:
	 - `points` (list of Vector) - a list
	   of points in space.
	
	:Return:
	 - a topomesh to access neighborhood of points
	 - a map of points position in space
	
	:Returns Type: :class:`Topomesh`,dict of (pid,Vector)
	"""
	#call delaunay algo
	t = Triangulation(points)
	triangles = t.get_elements_indices()
	
	#construct topomesh
	dmesh = Topomesh(2)
	dpos = {}
	pid2dpid = {}
	eid2deid = {}
	fid2dfid = {}
	
	#add points
	for pid,vec in enumerate(points) :
		dpid = dmesh.add_wisp(0)
		pid2dpid[pid] = dpid
		dpos[dpid] = tuple(vec)
	
	#add edges and faces
	for fid,tr in enumerate(triangles) :
		dfid = dmesh.add_wisp(2)
		fid2dfid[fid] = dfid
		
		for i in xrange(3) :
			pid1 = tr[i]
			pid2 = tr[(i + 1) % 3]
			eid = (min(pid1,pid2),max(pid1,pid2) )
			try :
				deid = eid2deid[eid]
			except KeyError :
				deid = dmesh.add_wisp(1)
				eid2deid[eid] = deid
				dmesh.link(1,deid,pid1)
				dmesh.link(1,deid,pid2)
			dmesh.link(2,dfid,deid)
	
	#return
	return dmesh,dpos

def delaunay3D (points) :
	"""Construct a delaunay triangulation
	
	:Parameters:
	 - `points` (list of Vector) - a list
	   of points in space.
	
	:Return:
	 - a topomesh to access neighborhood of points
	 - a map of points position in space
	
	:Returns Type: :class:`Topomesh`,dict of (pid,Vector)
	"""
	#call delaunay algo
	t = Triangulation(points)
	tetrahedrons = t.get_elements_indices()
	
	#construct topomesh
	mesh = Topomesh(3)
	pos = {}
	pid2dpid = {}
	eid2deid = {}
	fid2dfid = {}
	cid2dcid = {}
	
	#add points
	for pid,vec in enumerate(points) :
		dpid = mesh.add_wisp(0)
		pid2dpid[dpid] = pid
		pos[dpid] = vec
	
	#add edges faces and cells
	for cid,tetra in enumerate(tetrahedrons) :
		#add cell
		dcid = mesh.add_wisp(3)
		cid2dcid[cid] = dcid
		
		#add faces
		for tup in [(0,1,2),(0,2,3),(0,3,1),(1,2,3)] :
			pids = [tetra[i] for i in tup]
			pids.sort()
			fid = tuple(pids)
			try :
				dfid = fid2dfid[fid]
			except KeyError :
				dfid = mesh.add_wisp(2)
				fid2dfid[fid] = dfid
				
				#add edges
				for i in xrange(3) :
					pid1 = pids[i]
					pid2 = pids[(i + 1) % 3]
					eid = (min(pid1,pid2),max(pid1,pid2) )
					try :
						deid = eid2deid[eid]
					except KeyError :
						deid = mesh.add_wisp(1)
						eid2deid[eid] = deid
						mesh.link(1,deid,pid1)
						mesh.link(1,deid,pid2)
					mesh.link(2,dfid,deid)
			
			mesh.link(3,dcid,dfid)
	
	#return
	return mesh,pos

def voronoi2D (dmesh, dpos) :
	"""Construct a voronoi mesh
	from a Delaunay tesselation.
	
	:Parameters:
	 - `dmesh` (:class:`Topomesh`) -
	    a delaunay mesh
	 - `dpos` (dict of (pid,(x,y) ) ) - positions
	    of points in space
	
	:Return:
	 - the constructed mesh
	 - the position of voronoi points
	 - a set of infinite points
	   as a property
	
	:Returns Type: :class:Topomesh,pos,set of pid
	"""
	#
	#create voronoi mesh
	#
	vmesh = Topomesh(2)
	vpos = {}
	dfid2vpid = {}
	deid2veid = {}
	dpid2vfid = {}
	dangling_pids = set()
	
	#delaunay faces to voronoi points
	for dfid in dmesh.wisps(2) :
		vpid = vmesh.add_wisp(0)
		dfid2vpid[dfid] = vpid
		#vpos[vpid] = centroid(dmesh,dpos,2,dfid)
		tr = tuple(dpos[dpid] for dpid in dmesh.borders(2,dfid,2) )
		vpos[vpid] = circum_center2D(*tr)
	
	#delaunay points to voronoi faces
	for dpid in dmesh.wisps(0) :
		vfid = vmesh.add_wisp(2)
		dpid2vfid[dpid] = vfid
	
	#delaunay edges to voronoi edges
	for deid in dmesh.wisps(1) :
		if dmesh.nb_regions(1,deid) == 1 :
			#edge on the boundary
			
			#add point to infinity
			vpid = vmesh.add_wisp(0)
			dangling_pids.add(vpid)
			vpos[vpid] = centroid(dmesh,dpos,1,deid)
			
			#create voronoi edge
			dfid, = dmesh.regions(1,deid)
			veid = vmesh.add_wisp(1)
			deid2veid[deid] = veid
			vmesh.link(1,veid,dfid2vpid[dfid])
			vmesh.link(1,veid,vpid)
			for dpid in dmesh.borders(1,deid) :
				vmesh.link(2,dpid2vfid[dpid],veid)
		elif dmesh.nb_regions(1,deid) == 2 :
			#internal edge
			
			dfid1,dfid2 = dmesh.regions(1,deid)
			veid = vmesh.add_wisp(1)
			deid2veid[deid] = veid
			vmesh.link(1,veid,dfid2vpid[dfid1])
			vmesh.link(1,veid,dfid2vpid[dfid2])
			for dpid in dmesh.borders(1,deid) :
				vmesh.link(2,dpid2vfid[dpid],veid)
		else :
			raise UserWarning("bad bad edge, %d" % deid)
	
	#create external walls for external cells
	for fid in vmesh.wisps(2) :
		local_dangling_pids = set(vmesh.borders(2,fid,2) ) \
		                      & dangling_pids
		if len(local_dangling_pids) > 0 :
			pid1,pid2 = local_dangling_pids
			#simple solution
			eid = vmesh.add_wisp(1)
			vmesh.link(1,eid,pid1)
			vmesh.link(1,eid,pid2)
			vmesh.link(2,fid,eid)
	
	#
	#	return
	#
	return vmesh,vpos,dangling_pids

def voronoi3D (mesh, pos) :
	"""Construct the dual mesh
	
	Construct the voronoi tesselation
	given a delaunay mesh
	
	:Parameters:
	 - `mesh` (:class:`Topomesh`) - Delaunay mesh
	 - `pos` (dict of (pid,Vector) ) - position
	    of points in space
	
	:Return:
	 - the voronoi mesh
	 - the position of voronoi points in space
	 - a set of dangling points
	"""
	#create voronoi mesh
	vmesh = Topomesh(3)
	vpos = {}
	dcid2vpid = {}
	dfid2veid = {}
	deid2vfid = {}
	dpid2vcid = {}
	dangling_pids = set()
	dangling_eids = {}
	
	#delaunay cells to voronoi points
	for dcid in mesh.wisps(3) :
		vpid = vmesh.add_wisp(0,dcid)
		dcid2vpid[dcid] = vpid
		tet = tuple(pos[dpid] for dpid in mesh.borders(3,dcid,3) )
		vpos[vpid] = circum_center3D(*tet)
	
	#delaunay faces to voronoi edges
	for dfid in mesh.wisps(2) :
		veid = vmesh.add_wisp(1)
		dfid2veid[dfid] = veid
		
		if mesh.nb_regions(2,dfid) == 1 :
			#face on the boundary
			
			#add point to infinity
			vpid = vmesh.add_wisp(0)
			dangling_pids.add(vpid)
			vpos[vpid] = centroid(mesh,pos,2,dfid)
			
			#link voronoi edge to points
			dcid, = mesh.regions(2,dfid)
			vmesh.link(1,veid,dcid2vpid[dcid])
			vmesh.link(1,veid,vpid)
		elif mesh.nb_regions(2,dfid) == 2 :
			#internal face
			
			dcid1,dcid2 = mesh.regions(2,dfid)
			vmesh.link(1,veid,dcid2vpid[dcid1])
			vmesh.link(1,veid,dcid2vpid[dcid2])
		else :
			raise UserWarning("bad bad face: %d" % dfid)
	
	#delaunay edges to voronoi faces
	for deid in mesh.wisps(1) :
		vfid = vmesh.add_wisp(2)
		deid2vfid[deid] = vfid
		for dfid in mesh.regions(1,deid) :
			vmesh.link(2,vfid,dfid2veid[dfid])
		
		local_dangling_pids = set(vmesh.borders(2,vfid,2) ) \
		                      & dangling_pids
		if len(local_dangling_pids) > 0 :
			vpid1,vpid2 = local_dangling_pids
			key = (min(vpid1,vpid2),max(vpid1,vpid2) )
			try :
				veid = dangling_eids[key]
			except KeyError :
				veid = vmesh.add_wisp(1)
				dangling_eids[key] = veid
				vmesh.link(1,veid,vpid1)
				vmesh.link(1,veid,vpid2)
			vmesh.link(2,vfid,veid)
	
	#delaunay points to voronoi cells
	dangling_eids = set(dangling_eids.itervalues() )
	
	for dpid in mesh.wisps(0) :
		vcid = vmesh.add_wisp(3)
		dpid2vcid[dpid] = vcid
		for deid in mesh.regions(0,dpid) :
			vmesh.link(3,vcid,deid2vfid[deid])
		
		local_dangling_eids = set(vmesh.borders(3,vcid,2) ) \
		                      & dangling_eids
		if len(local_dangling_eids) > 0 :
			vfid = vmesh.add_wisp(2)
			for veid in local_dangling_eids :
				vmesh.link(2,vfid,veid)
			vmesh.link(3,vcid,vfid)
	
	#return
	return vmesh,vpos,dangling_pids

	

