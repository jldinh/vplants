#############################
#
print "compute delaunay"
#
#############################
execfile("delaunay_simple.py")

#############################
#
print "constrain delaunay"
#
#############################
execfile("delaunay_constrained.py")

#############################
#
print "filter delaunay"
#
#############################
execfile("delaunay_filtered.py")

#############################
#
print "compute voronoi"
#
#############################
execfile("voronoi_simple.py")

#############################
#
print "compute voronoi"
#
#############################
execfile("voronoi_projected.py")

#############################
#
print "draw result"
#
#############################
from random import randint
from pickle import load
from openalea.tissueshape import ordered_pids
from openalea.svgdraw import to_xml, \
                             SVGScene,SVGLayer,\
                             SVGSphere,SVGConnector,\
                             SVGPath
from vplants.plantgl.algo import Discretizer

pos = dict( (pid,sc.svg_pos(*vec) ) for pid,vec in pos.iteritems() )

d = Discretizer()
outer_boundary.apply(d)
pts = [sc.svg_pos(vec[0],vec[1]) for vec in d.result]

sc = SVGScene(*sc.size() )

lay = SVGLayer("voronoi cells",lay.width(),lay.height(),"layer0")
sc.append(lay)

cell_color = load(open("vor_cell_color.pkl",'rb') )

for fid in mesh.wisps(2) :
	coords = [pos[pid] for pid in ordered_pids(mesh,fid)]
	elm = SVGPath("cell%.4d" % fid)
	elm.move_to(*coords[-1])
	for x,y in coords :
		elm.line_to(x,y)
	
	elm.set_fill(cell_color[fid])
	
	lay.append(elm)

lay = SVGLayer("vertices",lay.width(),lay.height(),"layer1")
sc.append(lay)

for pid,(x,y) in pos.iteritems() :
	elm = SVGSphere(x,y,2,2,"vtx%.4d" % pid)
	elm.set_fill( (0,0,0) )
	lay.append(elm)

lay = SVGLayer("outer boundary",lay.width(),lay.height(),"layer2")
sc.append(lay)

elm = SVGPath("surfacepath")
elm.move_to(*pts[0])
for pt in pts[1:] :
	elm.line_to(*pt)
elm.set_fill(None)
elm.set_stroke( (0,255,0) )
elm.set_stroke_width(1)
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
dial.setWindowTitle("projected voronoi 2D")
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
pix.save("voronoi_projected.png")

dial.show()

qapp.exec_()








