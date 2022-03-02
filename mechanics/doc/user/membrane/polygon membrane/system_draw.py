#############################
#
print "draw geometry"
#
#############################
from math import radians,sin,cos
from openalea.svgdraw import to_xml, open_svg,\
                             SVGScene,SVGLayer,\
                             SVGSphere,SVGConnector,\
                             SVGPath,SVGText

sc = SVGScene(500,300)

lay = SVGLayer("geometry",500,300,"layer0")
sc.append(lay)

hexa = SVGPath("geom")
hexa.move_to(250 + 100 * cos(radians(30) ),
             150 - 100 * sin(radians(30) ) )
for i in xrange(1,6) :
	hexa.line_to(250 + 100 * cos(radians(30 + i * 60) ),
	             150 - 100 * sin(radians(30 + i * 60) ) )
hexa.close()
hexa.set_fill( (0,255,0) )

lay.append(hexa)

f = open_svg("toto.svg",'w')
f.write(sc)
f.close()

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
dial.setWindowTitle("system geometry")
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
pix.save("system_geometry.png")

dial.show()

qapp.exec_()


#############################
#
print "draw forces"
#
#############################
lay = SVGLayer("forces",300,300,"layer1")
sc.append(lay)

f1 = SVGPath("force1")
f1.move_to(350,130)
f1.line_to(430,130)
f1.line_to(430,110)
f1.line_to(480,150)
f1.line_to(430,190)
f1.line_to(430,170)
f1.line_to(350,170)
f1.close()
f1.set_fill(None)
f1.set_stroke( (255,0,0) )
f1.set_stroke_width(4)
lay.append(f1)

f2 = SVGPath("force1")
f2.move_to(150,130)
f2.line_to(70,130)
f2.line_to(70,110)
f2.line_to(20,150)
f2.line_to(70,190)
f2.line_to(70,170)
f2.line_to(150,170)
f2.close()
f2.set_fill(None)
f2.set_stroke( (255,0,0) )
f2.set_stroke_width(4)
lay.append(f2)


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
dial.setWindowTitle("system forces")
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
pix.save("system_forces.png")

dial.show()

qapp.exec_()






