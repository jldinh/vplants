from openalea.svgdraw import SVGPath

def cell_corners_cycle (mesh, cid) :
	"""List the corners of the cell arranged in cycle.
	"""
	borders = set(mesh.borders(2,cid) )
	wid = borders.pop()
	pid0,extr = mesh.borders(1,wid)
	path = [pid0]
	for i in xrange(len(borders) ) :
		path.append(extr)
		wid, = (set(mesh.regions(0,extr) ) & borders) - set([wid])
		extr, = set(mesh.borders(1,wid) ) - set([extr])
	
	return path

def cell_walls_cycle (mesh, cid) :
	"""List the walls of the cell arranged in cycle.
	"""
	borders = set(mesh.borders(2,cid) )
	wid = borders.pop()
	pid0,extr = mesh.borders(1,wid)
	path = [wid]
	for i in xrange(len(borders) ) :
		wid, = (set(mesh.regions(0,extr) ) & borders) - set([wid])
		extr, = set(mesh.borders(1,wid) ) - set([extr])
		path.append(wid)
	
	return path

def cell_geom (mesh, pos, cid, shape_id) :
	"""Create a path sourrounding the cell.
	
	return an SVGPath
	"""
	corners = cell_corners_cycle(mesh,cid)
	pth = SVGPath(shape_id)
	pth.move_to(pos[corners[0] ].x,pos[corners[0] ].y)
	for pid in corners[1:] :
		pth.line_to(pos[pid].x,pos[pid].y)
	pth.close()
	
	return pth

