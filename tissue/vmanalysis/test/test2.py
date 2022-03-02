#####################################
#
print "read inrimage"
#
#####################################
from openalea.vmanalysis import InrImage

im = InrImage()
im.read("SAM.inr.gz")
im.set_data(im.data()[:100,:,:])

#####################################
#
print "display"
#
#####################################
from PyQt4.QtGui import QApplication,QColor
from openalea.vmanalysis import SlideViewer,compute_palette

palette = compute_palette('grayscale',im.data().max() )

qapp = QApplication([])

w = SlideViewer()

v = w.view()
v.set_palette(palette)
v.set_image(im)

w.show()

qapp.exec_()

