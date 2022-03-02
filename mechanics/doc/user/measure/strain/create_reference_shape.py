from openalea.svgdraw import open_svg,SVGScene,SVGSphere,SVGBox

f = open_svg("shapes.svg",'r')
sc = f.read()
f.close()

shp = sc.get_by_id("rect_ref")
shp.translate(*tuple(-val for val in shp.scene_pos(shp.center() ) ) )

