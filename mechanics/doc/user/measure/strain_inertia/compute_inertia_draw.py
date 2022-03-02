execfile("find_shape.py")
execfile("compute_inertia.py")

from math import sqrt
from numpy.linalg import eig

print "I_ref"
print I_ref

w,v = eig(I_ref)
V1_ref = Vector2(v[0,0],v[1,0]) * sqrt(w[0]) * 2
V2_ref = Vector2(v[0,1],v[1,1]) * sqrt(w[1]) * 2
if w[0] < w[1] :
	V1_ref,V2_ref = V2_ref,V1_ref

print w
print v

ref_bary = sum(ref_shp,Vector2() ) / len(ref_shp)

print "I_act"
print I_act

w,v = eig(I_act)
V1_act = Vector2(v[0,0],v[1,0]) * sqrt(w[0]) * 2
V2_act = Vector2(v[0,1],v[1,1]) * sqrt(w[1]) * 2
if w[0] < w[1] :
	V1_act,V2_act = V2_act,V1_act

print w
print v

act_bary = sum(act_shp,Vector2() ) / len(act_shp)

############################################
#
print "draw"
#
############################################
from openalea.svgdraw import display,SVGPath,save_png

execfile("create_reference_shape.py")

elm = SVGPath("V1")
elm.move_to(*(ref_bary - V1_ref) )
elm.line_to(*(ref_bary + V1_ref) )
elm.set_fill(None)
elm.set_stroke( (255,0,0) )
elm.set_stroke_width(5)
sc.append(elm)

elm = SVGPath("V2")
elm.move_to(*(ref_bary - V2_ref) )
elm.line_to(*(ref_bary + V2_ref) )
elm.set_fill(None)
elm.set_stroke( (0,255,0) )
elm.set_stroke_width(5)
sc.append(elm)

display(sc)
save_png("reference_inertia.png",sc)

execfile("create_actual_shape.py")

elm = SVGPath("V1")
elm.move_to(*(act_bary - V1_act) )
elm.line_to(*(act_bary + V1_act) )
elm.set_fill(None)
elm.set_stroke( (255,0,0) )
elm.set_stroke_width(5)
sc.append(elm)

elm = SVGPath("V2")
elm.move_to(*(act_bary - V2_act) )
elm.line_to(*(act_bary + V2_act) )
elm.set_fill(None)
elm.set_stroke( (0,255,0) )
elm.set_stroke_width(5)
sc.append(elm)

display(sc)
save_png("actual_inertia.png",sc)


