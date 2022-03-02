execfile("create_mesh.py")

#############################
#
print "read equilibrium"
#
#############################
from pickle import load

eq_pos = load(open("equilibrium_pos.pkl",'rb') )

#############################
#
print "draw result"
#
#############################
from vplants.plantgl.math import norm
from openalea.svgdraw import to_xml, open_svg,\
                             SVGScene,SVGLayer,\
                             SVGSphere,SVGConnector,\
                             SVGPath,SVGText

sca = 200.
size = 2.5 * sca
fontsize = 24
fw = 10.5 / 2.
fh = 16.3 / 2.

def svg_pos (vec) :
	return size / 2. + vec[0] * sca,\
	       size / 2. - vec[1] * sca

sc = SVGScene(size,size)

execfile("draw_axis.py")

lay = SVGLayer("ref",size,size,"layer0")
sc.append(lay)

for eid in mesh.wisps(1) :
	pt1,pt2 = (pos[pid] for pid in mesh.borders(1,eid) )
	elm = SVGPath("edge%.4d" % eid)
	elm.move_to(*svg_pos(pt1) )
	elm.line_to(*svg_pos(pt2) )
	elm.set_fill(None)
	elm.set_stroke( (0,0,0) )
	elm.set_stroke_width(2)
	lay.append(elm)

for pid,vec in pos.iteritems() :
	x,y = svg_pos(vec)
	elm = SVGSphere(x,y,4,4,"point%.4d" % pid)
	elm.set_fill( (0,0,0) )
	lay.append(elm)

lay = SVGLayer("act",size,size,"layer1")
sc.append(lay)

for eid in mesh.wisps(1) :
	pt1,pt2 = (pos[pid] - (pos[pid] - eq_pos[pid]) * 30 for pid in mesh.borders(1,eid) )
	elm = SVGPath("edge%.4d" % eid)
	elm.move_to(*svg_pos(pt1) )
	elm.line_to(*svg_pos(pt2) )
	elm.set_fill(None)
	elm.set_stroke( (0,0,255) )
	elm.set_stroke_width(2)
	lay.append(elm)

for pid,vec in eq_pos.iteritems() :
	x,y = svg_pos(pos[pid] - (pos[pid] - vec) * 30)
	elm = SVGSphere(x,y,4,4,"point%.4d" % pid)
	elm.set_fill( (0,0,0) )
	lay.append(elm)

#############################
#
print "display result"
#
#############################
from PyQt4.QtCore import QByteArray
from PyQt4.QtGui import QApplication, \
                        QColor,QPalette, \
                        QPixmap,QPainter, \
                        QDialog,QVBoxLayout
from PyQt4.QtSvg import QSvgWidget,QSvgRenderer

qapp = QApplication([])

dial = QDialog()
dial.setWindowTitle("equilibrium")
dial.setPalette(QPalette(QColor(255,255,255) ) )
lay = QVBoxLayout(dial)

w = QSvgWidget(dial)
data = QByteArray(str(to_xml(sc) ) )
w.load(data)

r = w.renderer()
w.setMinimumSize(r.defaultSize() )
lay.addWidget(w)

pix = QPixmap(r.defaultSize() )
pix.fill(QColor(255,255,255) )
painter = QPainter(pix)
r.render(painter)
painter.end()
pix.save("equilibrium.png")

dial.show()

qapp.exec_()








