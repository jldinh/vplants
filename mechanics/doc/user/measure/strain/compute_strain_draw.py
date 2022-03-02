from math import log

execfile("find_shape.py")
execfile("compute_strain.py")

from numpy.linalg import eig

print "strain"
print st

w,v = eig(st)
V1 = Vector2(v[0,0],v[1,0]) * (w[0])
V2 = Vector2(v[0,1],v[1,1]) * (w[1])
if w[0] < w[1] :
	V1,V2 = V2,V1

print w
print v

############################################
#
print "draw"
#
############################################
from openalea.svgdraw import display,SVGPath,SVGScene,save_png

execfile("create_reference_shape.py")
ref_elm = shp
execfile("create_actual_shape.py")
act_elm = shp


sc = SVGScene(750,220)
ref_elm.translate(100,110)
sc.append(ref_elm)
act_elm.translate(600,110)
sc.append(act_elm)

sca = 100
bary = Vector2(300,110)

elm = SVGPath("V1")
elm.move_to(*(bary - V1 * sca) )
elm.line_to(*(bary + V1 * sca) )
elm.set_fill(None)
elm.set_stroke( (255,0,0) )
elm.set_stroke_width(5)
sc.append(elm)

elm = SVGPath("V2")
elm.move_to(*(bary - V2 * sca) )
elm.line_to(*(bary + V2 * sca) )
elm.set_fill(None)
elm.set_stroke( (0,255,0) )
elm.set_stroke_width(5)
sc.append(elm)

#math
elm = SVGPath("Hplus")
elm.move_to(190,110)
elm.line_to(210,110)
elm.set_fill(None)
elm.set_stroke( (0,0,0) )
elm.set_stroke_width(5)
sc.append(elm)

elm = SVGPath("Vplus")
elm.move_to(200,120)
elm.line_to(200,100)
elm.set_fill(None)
elm.set_stroke( (0,0,0) )
elm.set_stroke_width(5)
sc.append(elm)

elm = SVGPath("topegal")
elm.move_to(380,105)
elm.line_to(400,105)
elm.set_fill(None)
elm.set_stroke( (0,0,0) )
elm.set_stroke_width(5)
sc.append(elm)

elm = SVGPath("Vplus")
elm.move_to(380,115)
elm.line_to(400,115)
elm.set_fill(None)
elm.set_stroke( (0,0,0) )
elm.set_stroke_width(5)
sc.append(elm)

display(sc)
save_png("strain.png",sc)

