from openalea.deploy import execfile_partial

execfile_partial(vars(),"simu.py",None,"#end create field")

from vplants.plantgl.math import Vector2,norm

offset = Vector2(20,40)
xoffset = 20
yoffset = -40
sca = 20
############################################
#
print "constant field"
#
############################################
from openalea.svgdraw import (SVGScene,SVGPath,SVGSphere,SVGText,SVGSphere,
                             display,save_png)
from vplants.plantgl.scenegraph import NurbsCurve2D

sc = SVGScene(900,380)

#change GField so as to be in sc coordinates
svg_ctrl_pts1 = []
for x,y,z,w in ctrl_pts1 :
	x,y = sc.svg_pos(x * sca,z * sca)
	svg_ctrl_pts1.append( (x + xoffset,y + yoffset,0,w) )

svg_ctrl_pts2 = []
loc_x_offset = svg_ctrl_pts1[-1][0] + 20
for x,y,z,w in ctrl_pts2 :
	x,y = sc.svg_pos(x * sca,z * sca)
	svg_ctrl_pts2.append( (x + xoffset + loc_x_offset,y + yoffset,0,w) )

svg_ctrl_pts3 = []
loc_x_offset = svg_ctrl_pts2[-1][0] + 20
for x,y,z,w in ctrl_pts3 :
	x,y = sc.svg_pos(x * sca,z * sca)
	svg_ctrl_pts3.append( (x + xoffset + loc_x_offset,y + yoffset,0,w) )

svg_ctrl_pts4 = []
loc_x_offset = svg_ctrl_pts3[-1][0] + 20
for x,y,z,w in ctrl_pts4 :
	x,y = sc.svg_pos(x * sca,z * sca)
	svg_ctrl_pts4.append( (x + xoffset + loc_x_offset,y + yoffset,0,w) )

Gfield = NurbsPatch([svg_ctrl_pts1,
                     svg_ctrl_pts2,
                     svg_ctrl_pts3,
                     svg_ctrl_pts4])

#draw 2D patch
#uslices
for i in xrange(10) :
	v = i / 9.
	crv = Gfield.getUSection(v)
	pts = [crv.getPointAt(j / 10.) for j in xrange(11)]
	pth = SVGPath("uslice%d" % i)
	pth.move_to(pts[0][0],pts[0][1])
	for x,y,z in pts[1:] :
		pth.line_to(x,y)
	
	pth.set_fill(None)
	pth.set_stroke( (100,100,255) )
	pth.set_stroke_width(1)
	
	sc.append(pth)

#vslices
for i in xrange(10) :
	u = i / 9.
	crv = Gfield.getVSection(u)
	pts = [crv.getPointAt(j / 10.) for j in xrange(11)]
	pth = SVGPath("vslice%d" % i)
	pth.move_to(pts[0][0],pts[0][1])
	for x,y,z in pts[1:] :
		pth.line_to(x,y)
	
	pth.set_fill(None)
	pth.set_stroke( (100,100,255) )
	pth.set_stroke_width(1)
	
	sc.append(pth)

#draw time evolution of ctrl points
for i,u in enumerate( (0.,0.29,0.58,1.) ) :
	crv = Gfield.getVSection(u)
	pts = [crv.getPointAt(j / 10.) for j in xrange(11)]
	pth = SVGPath("time_evol%d" % i)
	pth.move_to(pts[0][0],pts[0][1])
	for x,y,z in pts[1:] :
		pth.line_to(x,y)
	
	pth.set_fill(None)
	pth.set_stroke( (50,50,50) )
	pth.set_stroke_width(1)
	pth.set_stroke_dash(4,2)
	
	sc.append(pth)

#draw specific time steps
for i in xrange(4) :
	v = i / 3.
	
	#get curve
	crv = Gfield.getUSection(v)
	cpts = [(x,y) for x,y,z,w in crv.ctrlPointList]
	
	#draw control points polyline
	pth = SVGPath("ccrv%d" % i)
	pth.move_to(cpts[0][0],cpts[0][1])
	for x,y in cpts[1:] :
		pth.line_to(x,y)
	
	pth.set_fill(None)
	pth.set_stroke( (100,100,100) )
	pth.set_stroke_width(2)
	
	sc.append(pth)
	
	#draw control points
	for j,(x,y) in enumerate(cpts) :
		circ = SVGSphere(x,y,0.3 * sca,0.3 * sca,"ctrl_pt%d_%d" % (j,i) )
		circ.set_fill( (255,0,0) )
		sc.append(circ)
	
	#draw curve
	pth = SVGPath("crv%d" % i)
	pts = [crv.getPointAt(u / 100.) for u in xrange(101)]
	pth.move_to(pts[0][0],pts[0][1])
	for x,y,z in pts[1:] :
		pth.line_to(x,y)
	
	pth.set_fill(None)
	pth.set_stroke( (0,0,200) )
	pth.set_stroke_width(3)
	
	sc.append(pth)
	
	#draw time text
	x = crv.getPointAt(1)[0] - 10
	y = crv.getPointAt(1)[1] + 25
	txt = SVGText(x,y,"t%d" % i,24)
	txt.set_fill( (0,0,0) )
	
	sc.append(txt)

display(sc,"growth field")
save_png("growth_field.png",sc)






