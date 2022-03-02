from openalea.svgdraw import open_svg
from openalea.vmanalysis import delaunay2D

f = open_svg("data.svg",'r')
sc = f.read()
f.close()

lay = sc.get_layer("cell centers")

cell_centers = []
for elm in lay.elements() :
	pos = sc.natural_pos(*elm.scene_pos(elm.center() ) )
	cell_centers.append(pos)

mesh,pos = delaunay2D(cell_centers)
