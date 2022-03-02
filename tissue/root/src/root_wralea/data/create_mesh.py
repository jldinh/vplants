def main (sc, verbose = True) :
	##########################################
	#
	if verbose : print "find cell centers"
	#
	##########################################
	from openalea.svgdraw import SVGSphere
	
	cell_pos = {}
	lay = sc.get_layer("cells")
	for elm in lay.elements() :
		if isinstance(elm,SVGSphere) :
			cell_pos[elm.id()] = elm.scene_pos(elm.center() )
	
	##########################################
	#
	if verbose : print "read vertices"
	#
	##########################################
	from openalea.svgdraw import SVGSphere
	
	vertex_pos = {}
	lay = sc.get_layer("walls")
	for elm in lay.elements() :
		if isinstance(elm,SVGSphere) :
			vertex_pos[elm.id()] = elm.scene_pos(elm.center() )
	
	##########################################
	#
	if verbose : print "read walls"
	#
	##########################################
	from openalea.svgdraw import SVGConnector
	
	walls = {}
	lay = sc.get_layer("walls")
	for elm in lay.elements() :
		if isinstance(elm,SVGConnector) :
			assert elm.source() in vertex_pos
			assert elm.target() in vertex_pos
			k = (elm.source(),elm.target() )
			if k in walls or (k[1],k[0]) in walls :
				raise UserWarning("element %s duplicated" % elm.id() )
			walls[k] = elm.id()
	
	##########################################
	#
	if verbose : print "create wall mesh"
	#
	##########################################
	from openalea.container import Topomesh
	
	mesh = Topomesh(2) 
	pos = {}
	trans = {}
	
	#add vertices
	for elmid,vec in vertex_pos.iteritems() :
		pid = mesh.add_wisp(0)
		pos[pid] = vec
		trans[elmid] = pid
	
	#add edges
	wall_id = {}
	for (sid,tid),elmid in walls.iteritems() :
		eid = mesh.add_wisp(1)
		mesh.link(1,eid,trans[sid])
		mesh.link(1,eid,trans[tid])
		wall_id[eid] = elmid
	
	##########################################
	#
	if verbose : print "find cells as cycles in the mesh"
	#
	##########################################
	from time import time
	from cycles import find_smallest_cycle_around
	
	tinit = time()
	max_radius = 3000
	
	cell_id = {}
	for elmid,ref_point in cell_pos.iteritems() :
		cid = mesh.add_wisp(2)
		cell_id[cid] = elmid
		#find edges around cell
		cycle = find_smallest_cycle_around(mesh,
		                                   pos,
		                                   ref_point,
		                                   max_radius,
		                                   0.1)
		if cycle is None :
			print "cell %d is not geometricaly defined (%s)" % (cid,elmid)
		else : #link cell to edges
			for eid in cycle :
				mesh.link(2,cid,eid)
	
	print "tot",time() - tinit
	#verification
	cont = True
	for wid in mesh.wisps(1) :
		if mesh.nb_regions(1,wid) == 0 :
			print "wall",wall_id[wid]
			cont = False
	
	for cid in mesh.wisps(2) :
		if mesh.nb_borders(2,cid) < 3 :
			print "cell %d with svg id of %s" % (cid,cell_id[cid])
			cont = False
	
	assert cont
	##########################################
	#
	if verbose : print "return"
	#
	##########################################
	from openalea.container import DataProp
	
	X = DataProp(type='float',unit='pix')
	Y = DataProp(type='float',unit='pix')
	
	svg_id = DataProp(cell_id,type='str',unit='pix')
	
	for pid,vec in pos.iteritems() :
		X[pid],Y[pid] = vec
	
	props = [[("X",X),("Y",Y)]
	         ,[]
	         ,[("svg_id",svg_id)] ]
	
	return mesh,props

if __name__ == '__main__' :
	import sys
	from os.path import splitext
	from openalea.container import write_topomesh
	from openalea.svgdraw import open_svg
	
	filename = sys.argv[1]
	
	f = open_svg(filename,'r')
	sc = f.read()
	f.close()

	mesh,props = main(sc)
	
	write_topomesh("%s.msh" % splitext(filename)[0],
	               mesh,
	               "mesh extract from an svg drawing",
	               props)



