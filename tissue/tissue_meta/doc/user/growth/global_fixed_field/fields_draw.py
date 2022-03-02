from vplants.plantgl.math import Vector2,norm

offset = Vector2(50,240)
plot_offset = offset + (0,50)

############################################
#
print "constant field"
#
############################################
from openalea.svgdraw import SVGScene,SVGPath,SVGSphere,SVGText,\
                             display,save_png
from vplants.plantgl.scenegraph import NurbsCurve2D

ctrl_pts = [(0,0,1),(160,0,1),(300,-50,1),(300,-200,1)]
crv = NurbsCurve2D(ctrl_pts)

pts = [crv.getPointAt(i / 100.) for i in xrange(101)]
speed = [Vector2(i * 3,norm(pts[i + 1] - pts[i]) * 10 ) for i in xrange(100)]


sc = SVGScene(400,400)

pth = SVGPath("ctrl_path")
pt = Vector2(ctrl_pts[0][0],ctrl_pts[0][1]) + offset
pth.move_to(*sc.svg_pos(*pt) )
for x,y,w in ctrl_pts[1:] :
	pt = Vector2(x,y) + offset
	pth.line_to(*sc.svg_pos(*pt) )

pth.set_fill(None)
pth.set_stroke( (0,0,0) )
pth.set_stroke_width(2)

sc.append(pth)

pth = SVGPath("crv")
pth.move_to(*sc.svg_pos(*(pts[0] + offset) ) )
for pt in pts[1:] :
	pth.line_to(*sc.svg_pos(*(pt + offset) ) )

pth.set_fill(None)
pth.set_stroke( (0,0,200) )
pth.set_stroke_width(4)

sc.append(pth)

pth = SVGPath("xarrow")
pth.move_to(*sc.svg_pos(*(plot_offset + (290,5) ) ) )
pth.line_to(*sc.svg_pos(*(plot_offset + (300,0) ) ) )
pth.line_to(*sc.svg_pos(*(plot_offset + (290,-5) ) ) )

pth.set_fill(None)
pth.set_stroke( (0,0,0) )
pth.set_stroke_width(2)

sc.append(pth)

pth = SVGPath("yarrow")
pth.move_to(*sc.svg_pos(*(plot_offset + (-5,45) ) ) )
pth.line_to(*sc.svg_pos(*(plot_offset + (0,50) ) ) )
pth.line_to(*sc.svg_pos(*(plot_offset + (5,45) ) ) )

pth.set_fill(None)
pth.set_stroke( (0,0,0) )
pth.set_stroke_width(2)

sc.append(pth)

pth = SVGPath("axes")
pth.move_to(*sc.svg_pos(*(plot_offset + (0,50) ) ) )
pth.line_to(*sc.svg_pos(*plot_offset) )
pth.line_to(*sc.svg_pos(*(plot_offset + (300,0) ) ) )

pth.set_fill(None)
pth.set_stroke( (0,0,0) )
pth.set_stroke_width(2)

sc.append(pth)

pth = SVGPath("speed")
pth.move_to(*sc.svg_pos(*(speed[0] + plot_offset) ) )
for pt in speed[1:] :
	pth.line_to(*sc.svg_pos(*(pt + plot_offset) ) )

pth.set_fill(None)
pth.set_stroke( (0,200,0) )
pth.set_stroke_width(2)

sc.append(pth)

pt = sc.svg_pos(*(plot_offset + (190,50) ) )
txt = SVGText(pt[0],pt[1],"speed",24)
txt.set_fill( (0,0,0) )
sc.append(txt)

for i in xrange(10) :
	u = i / 9.
	pt = crv.getPointAt(u) + offset
	sx,sy = sc.svg_pos(*pt)
	elm = SVGSphere(sx,sy,6,6,"speed_pt%.4d" % i)
	elm.set_fill( (0,100,0) )
	sc.append(elm)

for pid,(x,y,w) in enumerate(ctrl_pts) :
	pt = Vector2(x,y) + offset
	sx,sy = sc.svg_pos(*pt)
	elm = SVGSphere(sx,sy,3,3,"ctrl_pt%.4d" % pid)
	elm.set_fill( (255,0,0) )
	sc.append(elm)

display(sc,"constant")
save_png("field_constant.png",sc)

############################################
#
print "accelerating field"
#
############################################

ctrl_pts = [(0,0,1),(10,0,1),(320,30,1),(300,-200,1)]
crv = NurbsCurve2D(ctrl_pts)

pts = [crv.getPointAt(i / 100.) for i in xrange(101)]
speed = [Vector2(i * 3,norm(pts[i + 1] - pts[i]) * 10 ) for i in xrange(100)]

sc = SVGScene(400,400)

pth = SVGPath("ctrl_path")
pt = Vector2(ctrl_pts[0][0],ctrl_pts[0][1]) + offset
pth.move_to(*sc.svg_pos(*pt) )
for x,y,w in ctrl_pts[1:] :
	pt = Vector2(x,y) + offset
	pth.line_to(*sc.svg_pos(*pt) )

pth.set_fill(None)
pth.set_stroke( (0,0,0) )
pth.set_stroke_width(2)

sc.append(pth)

pth = SVGPath("crv")
pth.move_to(*sc.svg_pos(*(pts[0] + offset) ) )
for pt in pts[1:] :
	pth.line_to(*sc.svg_pos(*(pt + offset) ) )

pth.set_fill(None)
pth.set_stroke( (0,0,200) )
pth.set_stroke_width(4)

sc.append(pth)

pth = SVGPath("xarrow")
pth.move_to(*sc.svg_pos(*(plot_offset + (290,5) ) ) )
pth.line_to(*sc.svg_pos(*(plot_offset + (300,0) ) ) )
pth.line_to(*sc.svg_pos(*(plot_offset + (290,-5) ) ) )

pth.set_fill(None)
pth.set_stroke( (0,0,0) )
pth.set_stroke_width(2)

sc.append(pth)

pth = SVGPath("yarrow")
pth.move_to(*sc.svg_pos(*(plot_offset + (-5,45) ) ) )
pth.line_to(*sc.svg_pos(*(plot_offset + (0,50) ) ) )
pth.line_to(*sc.svg_pos(*(plot_offset + (5,45) ) ) )

pth.set_fill(None)
pth.set_stroke( (0,0,0) )
pth.set_stroke_width(2)

sc.append(pth)

pth = SVGPath("axes")
pth.move_to(*sc.svg_pos(*(plot_offset + (0,50) ) ) )
pth.line_to(*sc.svg_pos(*plot_offset) )
pth.line_to(*sc.svg_pos(*(plot_offset + (300,0) ) ) )

pth.set_fill(None)
pth.set_stroke( (0,0,0) )
pth.set_stroke_width(2)

sc.append(pth)

pth = SVGPath("speed")
pth.move_to(*sc.svg_pos(*(speed[0] + plot_offset) ) )
for pt in speed[1:] :
	pth.line_to(*sc.svg_pos(*(pt + plot_offset) ) )

pth.set_fill(None)
pth.set_stroke( (0,200,0) )
pth.set_stroke_width(2)

sc.append(pth)

pt = sc.svg_pos(*(plot_offset + (200,20) ) )
txt = SVGText(pt[0],pt[1],"speed",24)
txt.set_fill( (0,0,0) )
sc.append(txt)

for i in xrange(10) :
	u = i / 9.
	pt = crv.getPointAt(u) + offset
	sx,sy = sc.svg_pos(*pt)
	elm = SVGSphere(sx,sy,6,6,"speed_pt%.4d" % i)
	elm.set_fill( (0,100,0) )
	sc.append(elm)

for pid,(x,y,w) in enumerate(ctrl_pts) :
	pt = Vector2(x,y) + offset
	sx,sy = sc.svg_pos(*pt)
	elm = SVGSphere(sx,sy,3,3,"ctrl_pt%.4d" % pid)
	elm.set_fill( (255,0,0) )
	sc.append(elm)

display(sc,"acc")
save_png("field_acc.png",sc)






