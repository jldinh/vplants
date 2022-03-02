#############################
#
print "open inrimage"
#
#############################
from openalea.vmanalysis import read_inrimage

im,h = read_inrimage("seg_reconstructed.inr.gz")
print h

imref,href = read_inrimage("data/segmentation_partial_p60D2.inr.gz")
print href

#############################
#
print "compute error"
#
#############################
err = im != imref

meris = imref > 1

print "relative error",0.5 * err.sum() / float(meris.sum() )

sl_err = []
for z in xrange(im.shape[2]) :
	err = im[:,:,z] != imref[:,:,z]
	meris = im[:,:,z] > 1
	meris_ref = imref[:,:,z] > 1
	nb = (meris.sum() + meris_ref.sum() ) / 2.
	if nb == 0 :
		sl_err.append(0)
	else :
		sl_err.append(0.5 * err.sum() / float(nb) )

from pylab import plot,show,figure,xlabel,ylabel,savefig
zlist = range(im.shape[2] - 1,-1,-1)
plot(sl_err,zlist)
show()

fig = figure(figsize = (8,6) )
plot(sl_err,zlist)
xlabel("Relative error")
ylabel("vertical position")

savefig("tgs_vert_err_plot.png")

#############################
#
print "display vertical slide"
#
#############################
import struct
from PyQt4.QtGui import QImage,QColor
from openalea.vmanalysis import compute_palette
from numpy import cast,uint8

err = im[:,170,:] != imref[:,170,:]

data = cast[uint8](err * 1)
img = QImage(data.flatten('F'),
             data.shape[0],
             data.shape[1],
             QImage.Format_Indexed8)
img.setColorTable([QColor(0,0,0).rgb(),
                   QColor(255,255,255).rgb()])
img.save("tgs_vert_err.png")

pal = compute_palette("bwrainbow",max(im.max(),imref.max() ) )

img = QImage("".join(struct.pack('I',pal[ind]) \
                      for ind in imref[:,170,:].flatten('F') ),
             imref.shape[0],
             imref.shape[2],
             QImage.Format_RGB32)
img.save("tgs_vert_ref.png")

img = QImage("".join(struct.pack('I',pal[ind]) \
                      for ind in im[:,170,:].flatten('F') ),
             im.shape[0],
             im.shape[2],
             QImage.Format_RGB32)
img.save("tgs_vert_rec.png")

#############################
#
print "display"
#
#############################
z = 100

#reconstructed image
img = QImage("".join(struct.pack('I',pal[ind]) \
                      for ind in im[:,:,z].flatten('F') ),
             im.shape[0],
             im.shape[1],
             QImage.Format_RGB32)
img.save("tgs_reconstruct.png")

#reference image
img = QImage("".join(struct.pack('I',pal[ind]) \
                      for ind in imref[:,:,z].flatten('F') ),
             imref.shape[0],
             imref.shape[1],
             QImage.Format_RGB32)
img.save("tgs_reference.png")

#############################
#
print "display error"
#
#############################
err = im[:,:,z] != imref[:,:,z]

data = cast[uint8](err * 1)
img = QImage(data.flatten('F'),
             data.shape[0],
             data.shape[1],
             QImage.Format_Indexed8)
img.setColorTable([QColor(0,0,0).rgb(),
                   QColor(255,255,255).rgb()])
img.save("tgs_err.png")


