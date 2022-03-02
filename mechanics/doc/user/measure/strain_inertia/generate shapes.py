from openalea.svgdraw import display,save_png

###############################################
#
print "reference shape"
#
###############################################
execfile("create_reference_shape.py")

display(sc,"reference shape")
save_png("reference_shape.png",sc)

###############################################
#
print "actual shape"
#
###############################################
execfile("create_actual_shape.py")

display(sc,"actual shape")
save_png("actual_shape.png",sc)


