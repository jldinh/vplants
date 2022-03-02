#############################
#
print "compute delaunay"
#
#############################
execfile("delaunay_simple.py")

#############################
#
print "draw result"
#
#############################
from random import randint
from openalea.tissueshape import ordered_pids
from openalea.svgdraw import to_xml, \
                             SVGScene,SVGLayer,\
                             SVGSphere,SVGConnector,\
                             SVGPath

pos = dict( (pid,sc.svg_pos(*vec) ) for pid,vec in pos.iteritems() )

sc = SVGScene(*sc.size() )

lay = SVGLayer("delaunay triangles",lay.width(),lay.height(),"layer0")
sc.append(lay)

for fid in mesh.wisps(2) :
	coords = [pos[pid] for pid in ordered_pids(mesh,fid)]
	elm = SVGPath("triangle%.4d" % fid)
	elm.move_to(*coords[-1])
	for x,y in coords :
		elm.line_to(x,y)
	
	elm.set_fill( (randint(0,255),randint(0,255),randint(0,255) ) )
	
	lay.append(elm)

lay = SVGLayer("cell centers",lay.width(),lay.height(),"layer1")
sc.append(lay)

for pid,(x,y) in pos.iteritems() :
	elm = SVGSphere(x,y,3,3,"point%.4d" % pid)
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
dial.setWindowTitle("simple delaunay 2D")
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
pix.save("delaunay_simple.png")

dial.show()

qapp.exec_()








