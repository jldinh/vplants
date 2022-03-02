from openalea.container import Graph,Grid

def grid_graph2D (shape) :
	NBX,NBY=shape
	grid=Grid(shape)
	g=Graph()
	pos={}
	xincr=1./(NBX-1)
	yincr=1./(NBY-1)
	for vid in grid :
		i,j=grid.coordinates(vid)
		g.add_vertex(vid)
		pos[vid]=(i*xincr,j*yincr)
	for j in xrange(NBY) :
		for i in xrange(NBX) :
			if i<(NBX-1) :
				g.add_edge(grid.index((i,j)),grid.index((i+1,j)))
			if j<(NBY-1) :
				g.add_edge(grid.index((i,j)),grid.index((i,j+1)))
	return g,pos
	
