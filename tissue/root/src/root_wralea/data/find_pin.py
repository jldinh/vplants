def main (sc, mesh, props, verbose = True) :
	from vplants.plantgl.math import Vector2
	
	pos = {}
	X, = (prop[1] for prop in props[0] \
	      if prop[0] == 'X')
	Y, = (prop[1] for prop in props[0] \
	      if prop[0] == 'Y')
	for pid in mesh.wisps(0) :
		pos[pid] = Vector2(X[pid],Y[pid])
	
	##########################################
	#
	print "read PIN"
	#
	##########################################
	from openalea.svgdraw import SVGPath
	
	PIN_seg = {}
	lay = sc.get_layer("PIN")
	for elm in lay.elements() :
		if isinstance(elm,SVGPath) :
			seg = tuple(Vector2(*elm.scene_pos(vec) ) \
			            for vec in elm.polyline_ctrl_points() )
			assert len(seg) == 2
			PIN_seg[elm.id()] = seg
	
	##########################################
	#
	print "associate PIN with walls"
	#
	##########################################
	from vplants.plantgl.math import norm
	from openalea.tissueshape import centroid
	
	PIN = dict( (cid,[]) for cid in mesh.wisps(2) )
	
	wall_cent = dict( (wid,centroid(mesh,pos,1,wid) ) for wid in mesh.wisps(1) )
	cell_cent = dict( (cid,centroid(mesh,pos,2,cid) ) for cid in mesh.wisps(2) )
	
	for elmid,(vec_start,vec_end) in PIN_seg.iteritems() :
		print elmid,vec_start,vec_end
		#find wall corresponding to vec_end
		dist = [(norm(vec_end - wall_cent[wid]),wid) for wid in mesh.wisps(1)]
		dist.sort()
		wid = dist[0][1]
		print wid
		#find starting cell
		pin_dir = vec_end - vec_start
		dist = [(pin_dir * (vec_start - cell_cent[cid]),cid) for cid in mesh.regions(1,wid)]
		dist.sort(reverse = True)
		cid = dist[0][1]
		print cid
		#register
		PIN[cid].append(wid)
	
	##########################################
	#
	print "return"
	#
	##########################################
	return PIN

if __name__ == '__main__' :
	import sys
	from os.path import splitext
	from pickle import dump
	from openalea.container import read_topomesh,write_topomesh
	from openalea.svgdraw import open_svg
	
	filename = sys.argv[1]
	
	f = open_svg(filename,'r')
	sc = f.read()
	f.close()

	#read mesh
	meshname = "%s.msh" % splitext(filename)[0]
	try :
		mesh,descr,props = read_topomesh(meshname,'max')
	except IOError :
		import create_mesh
		mesh,props = create_mesh.main(sc)
		
		write_topomesh(meshname,
		               mesh,
		               "mesh extract from an svg drawing",
		               props)
	
	PIN = main(sc,mesh,props)
	
	outname = "%s.PIN.pkl" % splitext(filename)[0]
	dump(PIN,open(outname,'w') )


