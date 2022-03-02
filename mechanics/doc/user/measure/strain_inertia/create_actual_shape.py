from math import radians
from openalea.svgdraw import SVGScene,SVGSphere,SVGBox

sc = SVGScene(400,400)

#shp = SVGSphere(0,0,100,60,"shpact")
shp = SVGBox(0,0,200,120,"shpact")
shp.rotate(radians(-30) )
shp.translate(100-16,200)
shp.set_fill( (0,0,0) )
sc.append(shp)

