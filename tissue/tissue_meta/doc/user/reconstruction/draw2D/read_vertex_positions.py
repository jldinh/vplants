vertex_pos = {}
vertex_svg_id = {}
lay = sc.get_layer("walls")
for elm in lay.elements() :
	if isinstance(elm,SVGSphere) :
		pid = mesh.add_wisp(0)
		vertex_svg_id[elm.id()] = pid
		vertex_pos[pid] = Vector2(*sc.natural_pos(*elm.scene_pos(elm.center() ) ) )

