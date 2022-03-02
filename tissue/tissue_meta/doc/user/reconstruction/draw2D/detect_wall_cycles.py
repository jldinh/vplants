from openalea.tissueshape import edge_loop_around

for cid,ref_point in cell_pos.iteritems() :
	for eid in edge_loop_around(mesh,vertex_pos,ref_point) :
		mesh.link(2,cid,eid)

