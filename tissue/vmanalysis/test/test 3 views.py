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
print "create 3 views"
#
#####################################
im_top = im

data = im.data().transpose(0,2,1)
h = dict(im.header() )
h["VY"],h["VZ"] = h["VZ"],h["VY"]
im_face = InrImage(h,data)

data = im.data().transpose(2,1,0)
h = dict(im.header() )
h["VX"],h["VY"],h["VZ"] = h["VZ"],h["VY"],h["VX"]
im_side = InrImage(h,data)

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

#top
wt = SlideViewer()
v = wt.view()
v.set_palette(palette)
v.set_image(im_top)
wt.show()
wt.setWindowTitle("top")

#face
wf = SlideViewer()
v = wf.view()
v.set_palette(palette)
v.set_image(im_face)
wf.show()
wf.setWindowTitle("face")

#side
ws = SlideViewer()
v = ws.view()
v.set_palette(palette)
v.set_image(im_side)
ws.show()
ws.setWindowTitle("side")

qapp.exec_()

