###################################################
#
#	cell division
#
###################################################
from openalea.tissueshape import main_axis_2D,divide_segment_2D,divide_cell_2D,face_surface_2D,edge_length

def divide_cell (mesh, graph, pos, cid, shrink_factor, param) :
	"""
	divide a cell according to its main axis
	"""
	#local
	mesh = mesh
	graph = graph
	pos = pos
	#main axis
	bary,axis = main_axis_2D(mesh,pos,cid)
	#division
	mid_pts,divided_edges,eid,cid1,cid2 = divide_cell_2D(mesh,pos,cid,bary,axis)
	#update graph
	graph.add_edge(cid1,cid2,eid)
	for did in (cid1,cid2) :
		for wid in set(mesh.borders(2,did)) - set([eid]) :
			assert not graph.has_edge(wid)
			if mesh.nb_regions(1,wid) == 2 :
				rid1,rid2 = mesh.regions(1,wid)
				graph.add_edge(rid1,rid2,wid)
	#update cell properties
	del param.cell_age[cid]
	param.cell_age[cid1] = 0.
	param.cell_age[cid2] = 0.
	for prop in (param.morphogen,param.alpha,param.beta,param.turgor,param.gamma) :
		val = prop.pop(cid)
		prop[cid1] = val
		prop[cid2] = val
	#update wall properties
	for wid,(wid1,wid2) in divided_edges.iteritems() :
		length_wid1 = edge_length(mesh,pos,wid1)
		length_wid2 = edge_length(mesh,pos,wid2)
		length_wid = length_wid1 + length_wid2
		ref_l0 = param.l0.pop(wid)
		param.l0[wid1] = ref_l0 * max(0.1,min(0.9,length_wid1 / length_wid))
		param.l0[wid2] = ref_l0 * max(0.1,min(0.9,length_wid2 / length_wid))
		for prop in (param.D,param.K) :
			try : #D defined for internal walls only
				val = prop.pop(wid)
				prop[wid1] = val
				prop[wid2] = val
			except KeyError :
				pass
	param.l0[eid] = edge_length(mesh,pos,eid) * shrink_factor
	edges = (set(mesh.borders(2,cid1)) | set(mesh.borders(2,cid2)) ) - set([eid])
	param.K[eid] = min( param.K[wid] for wid in edges )
	param.D[eid] = sum( param.D[wid] for wid in edges if graph.has_edge(wid) ) / len(edges)
	#update points properties
	for pid in mesh.borders(1,eid) :
		param.weight[pid] = 1.

def divide (mesh, graph, pos, Vmax, shrink_factor, param) :
	for cid in list(mesh.wisps(2)) :
		V = face_surface_2D(mesh,pos,cid)
		if V > Vmax :
			divide_cell(mesh,graph,pos,cid,shrink_factor,param)

def init_division (param) :
	param.mesh = None
	param.graph = None
	param.pos = None
	
	param.Vmax = 1.
	param.shrink_factor = 0.8
	return param,

def division_process (param) :
	def process (time, dt) :
		divide(param.mesh,param.graph,param.pos,param.Vmax,param.shrink_factor,param)
	return (process,"divide"),


