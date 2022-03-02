#########################################
#
print "read image"
#
#########################################
from openalea.vmanalysis import read_inrimage

im,h = read_inrimage("segmentation_partial_p60D2.inr.gz")
print h

#########################################
#
print "write file"
#
#########################################
f = open("../local_params.py",'w')
f.write("Xsize = %s\n" % h["XDIM"])
f.write("Ysize = %s\n" % h["YDIM"])
f.write("Zsize = %s\n" % h["ZDIM"])

f.write("Xres = %s\n" % h["VX"])
f.write("Yres = %s\n" % h["VY"])
f.write("Zres = %s\n" % h["VZ"])

f.close()






