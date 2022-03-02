from openalea.svgdraw import SVGScene,SVGSphere,SVGBox

sc = SVGScene(400,400)

#shp = SVGSphere(100,100,50.1,50,"shpref")
shp = SVGBox(150,150,100,100,"shpref")
shp.set_fill( (0,0,0) )
sc.append(shp)

