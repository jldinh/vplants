####################################
#
print "create array"
#
####################################
from numpy import zeros,ones,uint8

dat = zeros( (200,150,50),uint8)

cell = ones( (50,20,10),uint8)

dat[:50,:20,:10] = cell
dat[-50:,-20:,-10:] = cell * 2

####################################
#
print "create header"
#
####################################
h = {"SCALE":"2**0",
     "CPU":"decm",
     "VX":"0.1",
     "VY":"0.1",
     "VZ":"0.2",
     "TX":"",
     "TY":"",
     "TZ":"",
     "#GEOMETRY":"CARTESIAN"}

####################################
#
print "write inrimage"
#
####################################
from openalea.vmanalysis import InrImage

im = InrImage(h,dat)
im.write("test.inr.gz")

