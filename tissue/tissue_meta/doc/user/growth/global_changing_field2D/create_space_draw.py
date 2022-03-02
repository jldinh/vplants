from openalea.deploy import execfile_partial

execfile_partial(vars(),"simu.py",None,"#end create space")

################################################
#
print "draw"
#
################################################
from vplants.plantgl.math import Vector4
from vplants.plantgl.ext.color import JetMap
from vplants.plantgl.scenegraph import NurbsCurve
from openalea.svgdraw import SVGScene,SVGPath,SVGLayer,SVGText

cmap = JetMap(0.,1.)
sc = SVGScene(250 * 6,800)

for ti in xrange(6) :
	t = ti / 5.
	lay = SVGLayer("frame%d" % ti,300,800)
	lay.translate(250 * ti,- 50)
	sc.append(lay)
	
	#patch
	crvs = [NurbsCurve([Vector4(pt[0],pt[1],0,1) for pt in ctrl_pts]) \
	                       for ctrl_pts in space_field(t)]
	
	col = cmap(t).i3tuple()
	
	#time
	x,y = sc.svg_pos(20,-40)
	txt = SVGText(x,y,"t = %.2f" % t,32)
	txt.set_fill( (0,0,0) )
	lay.append(txt)
	
	#frame
	xtop,ytop,ztop = crvs[-1].getPointAt(0.)
	xtop,ytop = sc.svg_pos(xtop,ytop + 20)
	xright,yright = sc.svg_pos(230,0)
	
	pth = SVGPath("Oxy%d" % ti)
	pth.move_to(xtop,ytop)
	pth.line_to(*sc.svg_pos(0,0) )
	pth.line_to(xright,yright)
	pth.set_fill(None)
	pth.set_stroke( (0,0,0) )
	pth.set_stroke_width(1.)
	lay.append(pth)
	
	pth = SVGPath("Oxarrow%d" % ti)
	pth.move_to(xright - 10,yright - 5)
	pth.line_to(xright,yright)
	pth.line_to(xright - 10,yright + 5)
	pth.set_fill(None)
	pth.set_stroke( (0,0,0) )
	pth.set_stroke_width(1.)
	lay.append(pth)
	
	pth = SVGPath("Oyarrow%d" % ti)
	pth.move_to(xtop - 5,ytop + 10)
	pth.line_to(xtop,ytop)
	pth.line_to(xtop + 5,ytop + 10)
	pth.set_fill(None)
	pth.set_stroke( (0,0,0) )
	pth.set_stroke_width(1.)
	lay.append(pth)
	
	#vslices
	for i,crv in enumerate(crvs) :
		pts = [tuple(crv.getPointAt(j / 100.) )[:2] for j in xrange(101)]
		pth = SVGPath("vpth%d%d" % (ti,i) )
		pth.move_to(*sc.svg_pos(*pts[0]) )
		for pt in pts[1:] :
			pth.line_to(*sc.svg_pos(*pt) )
		
		pth.set_fill(None)
		pth.set_stroke(col)
		pth.set_stroke_width(3)
		
		lay.append(pth)
	
	#uslices
	for j in xrange(11) :
		pts = [tuple(crv.getPointAt(j / 10.) )[:2] for crv in crvs]
		pth = SVGPath("upth%d%d" % (ti,j) )
		pth.move_to(*sc.svg_pos(0,0) )
		for pt in pts :
			pth.line_to(*sc.svg_pos(*pt) )
		
		pth.set_fill(None)
		pth.set_stroke(col)
		pth.set_stroke_width(3)
		
		lay.append(pth)

################################################
#
print "display"
#
################################################
from openalea.svgdraw import display,save_png

display(sc)
save_png("growing_space_field.png",sc)

