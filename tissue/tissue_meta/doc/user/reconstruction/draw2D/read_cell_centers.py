from openalea.svgdraw import SVGSphere

cell_pos = {}
cell_svg_id = {}
lay = sc.get_layer("cells")
for elm in lay.elements() :
	if isinstance(elm,SVGSphere) :
		cid = mesh.add_wisp(2)
		cell_svg_id[elm.id()] = cid
		cell_pos[cid] = Vector2(*sc.natural_pos(*elm.scene_pos(elm.center() ) ) )


