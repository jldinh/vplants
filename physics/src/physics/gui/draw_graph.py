from openalea.plantgl.scenegraph import Shape,Polyline,Sphere,Translated,Material

edge_mat=Material( (0,0,0) )
vertex_mat=Material( (0,0,255) )

def draw_graph2D (stage, graph, vertex_positions,\
				vertex_property=None, colormap=None,\
				edge_property=None, ecolormap=None) :
	vp=vertex_positions
	pos=dict( (vid,(vec.x,vec.y,0.)) for vid,vec in vp.iteritems() )
	edge_length={}
	if edge_property is None :
		emat=dict( (eid,edge_mat) for eid in graph.edges() )
	else :
		emat=dict( (eid,Material(ecolormap(edge_property[eid]).i3tuple())) \
					for eid in graph.edges() )
	for eid in graph.edges() :
		edge_length[eid]=(vp[graph.target(eid)]-vp[graph.source(eid)]).norm()
		line=Polyline([pos[graph.source(eid)],pos[graph.target(eid)]])
		stage+=Shape(line,emat[eid])
	
	if vertex_property is None :
		vmat=dict( (vid,vertex_mat) for vid in graph.vertices() )
	else :
		vmat=dict( (vid,Material(colormap(vertex_property[vid]).i3tuple())) \
					for vid in graph.vertices() )
	r=min(edge_length.itervalues())/3.
	for vid in graph.vertices() :
		geom=Translated(pos[vid],Sphere(r))
		stage+=Shape(geom,vmat[vid])
