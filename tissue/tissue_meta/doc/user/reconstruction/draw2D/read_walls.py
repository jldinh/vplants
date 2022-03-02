from openalea.svgdraw import SVGConnector

lay = sc.get_layer("walls")
for elm in lay.elements() :
	if isinstance(elm,SVGConnector) :
		eid = mesh.add_wisp(1)
		mesh.link(1,eid,vertex_svg_id[elm.source()])
		mesh.link(1,eid,vertex_svg_id[elm.target()])

