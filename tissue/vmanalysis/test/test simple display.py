#####################################
#
print "read inrimage"
#
#####################################
from openalea.vmanalysis import InrImage

im = InrImage()
im.read("test.inr.gz")

#####################################
#
print "display"
#
#####################################
from PyQt4.QtGui import QApplication,QColor
from openalea.vmanalysis import SlideViewer

palette = [QColor(0,0,0).rgb(),
           QColor(255,0,0).rgb(),
           QColor(0,255,0).rgb()]

qapp = QApplication([])

w = SlideViewer()

v = w.view()
v.set_palette(palette)
v.set_image(im)

w.show()

qapp.exec_()

