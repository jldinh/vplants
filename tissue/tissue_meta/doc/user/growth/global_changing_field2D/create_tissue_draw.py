from openalea.deploy import execfile_partial

execfile_partial(vars(),"simu.py",None,"#end create tissue")

################################################
#
print "draw"
#
################################################
from random import randint
from vplants.plantgl.math import Vector4
from vplants.plantgl.ext.color import IntMap
from vplants.plantgl.scenegraph import NurbsCurve
from openalea.svgdraw import SVGScene,SVGPath,SVGLayer,SVGText
from openalea.tissueshape import ordered_pids

sc = SVGScene(250,350)

lay = SVGLayer("space",250,350)
lay.translate(5,-5)
sc.append(lay)

#patch
crvs = [NurbsCurve([Vector4(pt[0],pt[1],0,1) for pt in ctrl_pts]) \
                       for ctrl_pts in space_field(0.)]

col = (0,0,255)

#vslices
for i,crv in enumerate(crvs) :
	pts = [tuple(crv.getPointAt(j / 100.) )[:2] for j in xrange(101)]
	pth = SVGPath("vpth%d" % i)
	pth.move_to(*sc.svg_pos(*pts[0]) )
	for pt in pts[1:] :
		pth.line_to(*sc.svg_pos(*pt) )
	
	pth.set_fill(None)
	pth.set_stroke(col)
	pth.set_stroke_width(1)
	pth.set_stroke_dash(2,2)
	
	lay.append(pth)

#uslices
for j in xrange(11) :
	pts = [tuple(crv.getPointAt(j / 10.) )[:2] for crv in crvs]
	pth = SVGPath("upth%d" % j)
	pth.move_to(*sc.svg_pos(0,0) )
	for pt in pts :
		pth.line_to(*sc.svg_pos(*pt) )
	
	pth.set_fill(None)
	pth.set_stroke(col)
	pth.set_stroke_width(1)
	pth.set_stroke_dash(2,2)
	
	lay.append(pth)

#tissue
lay = SVGLayer("tissue",250,350)
lay.translate(5,-5)
sc.append(lay)

#cells
cmap = IntMap()

for cid in mesh.wisps(2) :
	pts = [sc.svg_pos(*tuple(pos[pid])[:2]) for pid in ordered_pids(mesh,cid) ]
	pth = SVGPath("cell%d" % cid)
	pth.move_to(*pts[-1])
	for pt in pts :
		pth.line_to(*pt)
	
	pth.set_fill(cmap(cid).i3tuple() )
	pth.set_opacity(0.4)
	lay.append(pth)

#walls
for eid in mesh.wisps(1) :
	pt1,pt2 = (tuple(pos[pid])[:2] for pid in mesh.borders(1,eid) )
	pth = SVGPath("wall%d" % eid)
	pth.move_to(*sc.svg_pos(*pt1) )
	pth.line_to(*sc.svg_pos(*pt2) )
	pth.set_fill(None)
	pth.set_stroke( (0,0,0) )
	pth.set_stroke_width(2)
	lay.append(pth)

################################################
#
print "display"
#
################################################
from openalea.svgdraw import display,save_png

display(sc)
save_png("initial_tissue.png",sc)


