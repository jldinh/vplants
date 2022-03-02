#############################
#
print "compute delaunay"
#
#############################
execfile("delaunay_simple.py")

#############################
#
print "constrain delaunay"
#
#############################
execfile("delaunay_constrained.py")

#############################
#
print "filter delaunay"
#
#############################
execfile("delaunay_filtered.py")

#############################
#
print "compute voronoi"
#
#############################
execfile("voronoi_simple.py")

#############################
#
print "compute voronoi"
#
#############################
execfile("voronoi_projected.py")

#############################
#
print "draw result"
#
#############################
from openalea.svgdraw import to_xml, \
                             SVGScene,SVGLayer,\
                             SVGSphere,SVGImage,\
                             SVGPath

pos = dict( (pid,sc.svg_pos(*vec) ) \
        for pid,vec in pos.iteritems() )

sc = SVGScene(*sc.size() )

lay = SVGLayer("background",lay.width(),lay.height(),"layer0")
sc.append(lay)

img = SVGImage(0,0,557,298,"data_microscope.png","immicro")
lay.append(img)

lay = SVGLayer("voronoi walls",lay.width(),lay.height(),"layer1")
sc.append(lay)

for eid in mesh.wisps(1) :
	coords = [pos[pid] for pid in mesh.borders(1,eid)]
	elm = SVGPath("wall%.4d" % eid)
	elm.move_to(*coords[0])
	elm.line_to(*coords[1])
	elm.set_fill(None)
	elm.set_stroke( (255,0,0) )
	elm.set_stroke_width(1)
	
	lay.append(elm)

#############################
#
print "display result"
#
#############################
f = open_svg("result.svg",'w')
f.write(sc)
f.close()








