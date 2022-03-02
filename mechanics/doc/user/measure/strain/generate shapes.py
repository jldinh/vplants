from openalea.svgdraw import display,save_png,SVGScene

###############################################
#
print "reference shape"
#
###############################################
execfile("create_reference_shape.py")

sc = SVGScene(400,400)
shp.translate(200,200)
sc.append(shp)

display(sc,"reference shape")
save_png("reference_shape.png",sc)

###############################################
#
print "actual shape"
#
###############################################
execfile("create_actual_shape.py")

sc = SVGScene(400,400)
shp.translate(200,200)
sc.append(shp)

display(sc,"actual shape")
save_png("actual_shape.png",sc)


