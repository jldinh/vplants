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

sc = SVGScene(500,500)

lay = SVGLayer("geometry",500,500,"layer0")
sc.append(lay)

hexa = SVGPath("geom")
hexa.move_to(250 + 100 * cos(radians(30) ),
             250 - 100 * sin(radians(30) ) )
for i in xrange(1,6) :
	hexa.line_to(250 + 100 * cos(radians(30 + i * 60) ),
	             250 - 100 * sin(radians(30 + i * 60) ) )
hexa.close()
hexa.set_fill( (0,255,0) )

lay.append(hexa)

for i in xrange(11) :
	ray = SVGPath("ray%d" % i)
	ray.move_to(200 + 10 * i,200)
	ray.line_to(200 + 10 * i,300)
	ray.set_fill(None)
	ray.set_stroke( (0,0,0) )
	ray.set_stroke_width(1)
	lay.append(ray)

display(sc,"system geometry")
save_png("system_geometry.png",sc)

#############################
#
print "draw forces"
#
#############################
lay = SVGLayer("forces",500,500,"layer1")
sc.append(lay)

for i in xrange(6) :
	f = SVGPath("force%d" % i)
	f.move_to(0,0)
	f.line_to(0,-20)
	f.line_to(80,-20)
	f.line_to(80,-40)
	f.line_to(120,0)
	f.line_to(80,40)
	f.line_to(80,20)
	f.line_to(0,20)
	f.close()
	f.set_fill(None)
	f.set_stroke( (255,0,0) )
	f.set_stroke_width(4)
	f.rotate(radians(- 60 * i) )
	f.translate(250 + 100 * cos(radians(60 * i) ),
	            250 - 100 * sin(radians(60 * i) ) )
	lay.append(f)


display(sc,"forces")
save_png("system_forces.png",sc)





