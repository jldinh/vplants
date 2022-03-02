execfile("initialise.py")

size = sc.size()

execfile("read_cell_centers.py")
execfile("read_vertex_positions.py")
execfile("read_walls.py")
execfile("detect_wall_cycles.py")

#############################
#
print "draw result"
#
#############################
from random import randint
from openalea.tissueshape import ordered_pids
from openalea.svgdraw import to_xml, \
                             SVGScene,SVGLayer,\
                             SVGSphere,SVGPath,\
                             display,save_png

sc = SVGScene(*size)

pos = dict( (pid,sc.svg_pos(*vec) ) \
            for pid,vec in vertex_pos.iteritems() )

lay = SVGLayer("cells",size[0],size[1],"layer0")
sc.append(lay)

for fid in mesh.wisps(2) :
	coords = [pos[pid] for pid in ordered_pids(mesh,fid)]
	elm = SVGPath("cell%.4d" % fid)
	elm.move_to(*coords[0])
	for x,y in coords[1:] :
		elm.line_to(x,y)
	elm.close()
	elm.set_fill( (randint(50,255),randint(50,255),randint(50,255) ) )
	lay.append(elm)
	
	x,y = sc.svg_pos(*cell_pos[fid])
	elm = SVGSphere(x,y,10,10,"cell_cent%.4d" % fid)
	elm.set_fill( (0,0,0) )
	lay.append(elm)

lay = SVGLayer("walls",size[0],size[1],"layer1")
sc.append(lay)

for eid in mesh.wisps(1) :
	(x0,y0),(x1,y1) = (pos[pid] for pid in mesh.borders(1,eid) )
	elm = SVGPath("wall%.4d" % eid)
	elm.move_to(x0,y0)
	elm.line_to(x1,y1)
	elm.set_fill(None)
	elm.set_stroke( (0,0,0) )
	elm.set_stroke_width(2)
	lay.append(elm)

display(sc)
save_png("reconstructed_mesh.png",sc)









