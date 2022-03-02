execfile("initialise.py")

size = sc.size()

execfile("read_cell_centers.py")
execfile("read_vertex_positions.py")
execfile("read_walls.py")

#############################
#
print "draw result"
#
#############################
from openalea.svgdraw import to_xml, \
                             SVGScene,SVGLayer,\
                             SVGSphere,SVGPath,\
                             display,save_png

sc = SVGScene(*size)

pos = dict( (pid,sc.svg_pos(*vec) ) \
            for pid,vec in vertex_pos.iteritems() )

lay = SVGLayer("cells",size[0],size[1],"layer0")
sc.append(lay)

for cid in mesh.wisps(2) :
	x,y = sc.svg_pos(*cell_pos[cid])
	elm = SVGSphere(x,y,20,20,"cell%.4d" % cid)
	elm.set_fill( (255,0,255) )
	lay.append(elm)

lay = SVGLayer("walls",size[0],size[1],"layer1")
sc.append(lay)

for eid in mesh.wisps(1) :
	(x0,y0),(x1,y1) = (pos[pid] for pid in mesh.borders(1,eid) )
	elm = SVGPath("wall%.4d" % eid)
	elm.move_to(x0,y0)
	elm.line_to(x1,y1)
	elm.set_fill(None)
	elm.set_stroke( (0,255,0) )
	elm.set_stroke_width(2)
	lay.append(elm)

for pid in mesh.wisps(0) :
	x,y = pos[pid]
	elm = SVGSphere(x,y,6,6,"vertex%.4d" % pid)
	elm.set_fill( (255,255,0) )
	lay.append(elm)

display(sc)
save_png("centers_plus_walls.png",sc)








