from random import uniform,randint
from openalea.svgdraw import open_svg,SVGScene,SVGSphere

sc = SVGScene(1000,1000)

for i in xrange(100) :
	sph = SVGSphere(uniform(0,1000),
	                uniform(0,1000),
	                uniform(10,100),
	                uniform(10,100),
	                "sph%.4d" % i)
	
	col = tuple(randint(0,255) for j in xrange(3) )
	sph.set_fill(col)
	col = tuple(randint(0,255) for j in xrange(3) )
	sph.set_stroke(col)
	sph.set_stroke_width(uniform(1,10) )
	
	sc.append(sph)

f = open_svg("toto.svg",'w')
f.write(sc)
f.close()





