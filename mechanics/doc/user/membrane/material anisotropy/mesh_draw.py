from openalea.deploy import execfile_partial

execfile_partial(vars(),"simu.py",None,"#end create mesh")

#############################
#
print "draw mesh"
#
#############################
from vplants.plantgl.math import norm
from openalea.svgdraw import (display,save_png,
                              SVGScene,SVGLayer,
                              SVGSphere,
                              SVGPath,SVGText)

sca = 200.
size = 2.5 * sca
fontsize = 24
fw = 10.5 / 2.
fh = 16.3 / 2.

def svg_pos (vec) :
	return size / 2. + vec[0] * sca,\
	       size / 2. - vec[1] * sca

sc = SVGScene(size,size)

#draw frame
frame_lay = SVGLayer("frame",size,size,"layer0")
sc.append(frame_lay)

elm = SVGPath("Ox")
elm.move_to(10,size - 10)
elm.line_to(10 + sca,size - 10)
elm.set_fill(None)
elm.set_stroke( (255,0,0) )
elm.set_stroke_width(3)
frame_lay.append(elm)

elm = SVGPath("Oxhead")
elm.move_to(sca,size - 15)
elm.line_to(10 + sca,size - 10)
elm.line_to(sca,size - 5)
elm.set_fill(None)
elm.set_stroke( (255,0,0) )
elm.set_stroke_width(3)
frame_lay.append(elm)

elm = SVGText(20 + sca - fw,size - 10 + fh,"x",fontsize,"xaxis")
elm.set_fill( (255,0,0) )
frame_lay.append(elm)

elm = SVGPath("Oy")
elm.move_to(10,size - 10)
elm.line_to(10,size - 10 - sca)
elm.set_fill(None)
elm.set_stroke( (0,255,0) )
elm.set_stroke_width(3)
frame_lay.append(elm)

elm = SVGPath("Oyhead")
elm.move_to(5,size - sca)
elm.line_to(10,size - 10 - sca)
elm.line_to(15,size - sca)
elm.set_fill(None)
elm.set_stroke( (0,255,0) )
elm.set_stroke_width(3)
frame_lay.append(elm)

elm = SVGText(10 - fw,size - 30 - sca + fh,"y",fontsize,"yaxis")
elm.set_fill( (0,255,0) )
frame_lay.append(elm)

#draw faces
lay = SVGLayer("faces",size,size,"layer1")
sc.append(lay)

for fid in mesh.wisps(2) :
	pt1,pt2,pt3 = (pos[pid] for pid in mesh.borders(2,fid,2) )
	cent = (pt1 + pt2 + pt3) / 3.
	pt1 = cent + (pt1 - cent) * 0.8
	pt2 = cent + (pt2 - cent) * 0.8
	pt3 = cent + (pt3 - cent) * 0.8
	
	elm = SVGPath("face%.4d" % fid)
	elm.move_to(*svg_pos(pt1) )
	elm.line_to(*svg_pos(pt2) )
	elm.line_to(*svg_pos(pt3) )
	elm.close()
	elm.set_fill( (0,255,0) )
	elm.set_stroke(None)
	lay.append(elm)
	
	x,y = svg_pos(cent)
	
	for i in xrange(11) :
		ray = SVGPath("f%.4dray%d" % (fid,i) )
		ray.move_to(x - 20 + 4 * i,y - 20)
		ray.line_to(x - 20 + 4 * i,y + 20)
		ray.set_fill(None)
		ray.set_stroke( (0,0,0) )
		ray.set_stroke_width(0.2)
		lay.append(ray)
	
	elm = SVGText(x - fw,
	              y + fh,
	              "%d" % fid,
	              fontsize,
	              "ftxt%.4d" % fid)
	elm.set_fill( (0,0,0) )
	lay.append(elm)

#draw edges
lay = SVGLayer("edges",size,size,"layer2")
sc.append(lay)

for eid in mesh.wisps(1) :
	pt1,pt2 = (pos[pid] for pid in mesh.borders(1,eid) )
	elm = SVGPath("edge%.4d" % eid)
	elm.move_to(*svg_pos(pt1) )
	elm.line_to(*svg_pos(pt2) )
	elm.set_fill(None)
	elm.set_stroke( (0,0,255) )
	elm.set_stroke_width(2)
	lay.append(elm)
	
	x,y = svg_pos( (pt1 + pt2) / 2.)
	elm = SVGText(x - fw,
	              y + fh,
	              "%d" % eid,
	              fontsize,
	              "etxt%.4d" % eid)
	elm.set_fill( (0,0,0) )
	lay.append(elm)

#draw points
lay = SVGLayer("points",size,size,"layer3")
sc.append(lay)

for pid,vec in pos.iteritems() :
	x,y = svg_pos(vec)
	elm = SVGSphere(x,y,4,4,"point%.4d" % pid)
	elm.set_fill( (0,0,0) )
	lay.append(elm)
	
	x,y = svg_pos(vec + vec * (fontsize / sca / norm(vec) ) )
	elm = SVGText(x - fw,
	              y + fh,
	              "%d" % pid,
	              fontsize,
	              "ptxt%.4d" % pid)
	elm.set_fill( (0,0,0) )
	lay.append(elm)

display(sc,"mesh")
save_png("mesh.png",sc)

