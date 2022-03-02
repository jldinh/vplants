#############################
#
print "draw geometry"
#
#############################
from math import radians,sin,cos
from openalea.svgdraw import (display,save_png,
                              SVGScene,SVGLayer,
                              SVGSphere,SVGConnector,
                              SVGPath,SVGText)

sc = SVGScene(500,300)

lay = SVGLayer("geometry",500,300,"layer0")
sc.append(lay)

hexa = SVGPath("geom")
hexa.move_to(250 + 100 * cos(radians(30) ),
             150 - 100 * sin(radians(30) ) )
for i in xrange(1,6) :
	hexa.line_to(250 + 100 * cos(radians(30 + i * 60) ),
	             150 - 100 * sin(radians(30 + i * 60) ) )
hexa.close()
hexa.set_fill( (0,255,0) )

lay.append(hexa)

display(sc,"system geometry")
save_png("system_geometry.png",sc)

#############################
#
print "draw forces"
#
#############################
lay = SVGLayer("forces",300,300,"layer1")
sc.append(lay)

f1 = SVGPath("force1")
f1.move_to(350,130)
f1.line_to(430,130)
f1.line_to(430,110)
f1.line_to(480,150)
f1.line_to(430,190)
f1.line_to(430,170)
f1.line_to(350,170)
f1.close()
f1.set_fill(None)
f1.set_stroke( (255,0,0) )
f1.set_stroke_width(4)
lay.append(f1)

f2 = SVGPath("force1")
f2.move_to(150,130)
f2.line_to(70,130)
f2.line_to(70,110)
f2.line_to(20,150)
f2.line_to(70,190)
f2.line_to(70,170)
f2.line_to(150,170)
f2.close()
f2.set_fill(None)
f2.set_stroke( (255,0,0) )
f2.set_stroke_width(4)
lay.append(f2)


display(sc,"forces")
save_png("system_forces.png",sc)





