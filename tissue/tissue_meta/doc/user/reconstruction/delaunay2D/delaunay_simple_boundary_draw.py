#############################
#
print "compute delaunay"
#
#############################
execfile("delaunay_simple.py")

#############################
#
print "read boundary"
#
#############################
from vplants.plantgl.scenegraph import NurbsCurve
from openalea.vmanalysis import curve_intersect

crv, = sc.get_layer("outer limit").elements()
surface = NurbsCurve.CBezier([sc.natural_pos(*crv.scene_pos(pt) ) for pt in crv.nurbs_ctrl_points()],
                             False,
                             200)

segs = dict( (eid,tuple(pos[pid] for pid in mesh.borders(1,eid) ) ) \
             for eid in mesh.wisps(1) )

#compute inside and outside triangles
outside_tr = set()

for eid in curve_intersect(surface,segs) :
	outside_tr.update(mesh.regions(1,eid) )

inside_tr = set(mesh.wisps(2) ) - outside_tr
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
from vplants.plantgl.algo import Discretizer

pos = dict( (pid,sc.svg_pos(*vec) ) for pid,vec in pos.iteritems() )

d = Discretizer()
surface.apply(d)
pts = [sc.svg_pos(vec[0],vec[1]) for vec in d.result]

sc = SVGScene(*sc.size() )

lay = SVGLayer("delaunay triangles",lay.width(),lay.height(),"layer0")
sc.append(lay)

for fid in inside_tr :
	coords = [pos[pid] for pid in ordered_pids(mesh,fid)]
	elm = SVGPath("triangle%.4d" % fid)
	elm.move_to(*coords[-1])
	for x,y in coords :
		elm.line_to(x,y)
	
	elm.set_fill( (randint(150,255),randint(150,255),randint(150,255) ) )
	
	lay.append(elm)

for fid in outside_tr :
	coords = [pos[pid] for pid in ordered_pids(mesh,fid)]
	elm = SVGPath("triangle%.4d" % fid)
	elm.move_to(*coords[-1])
	for x,y in coords :
		elm.line_to(x,y)
	
	elm.set_fill( (randint(0,80),randint(0,80),randint(0,80) ) )
	
	lay.append(elm)

lay = SVGLayer("cell centers",lay.width(),lay.height(),"layer1")
sc.append(lay)

for pid,(x,y) in pos.iteritems() :
	elm = SVGSphere(x,y,3,3,"point%.4d" % pid)
	elm.set_fill( (0,0,0) )
	lay.append(elm)

lay = SVGLayer("outerboundary",lay.width(),lay.height(),"layer2")
sc.append(lay)

elm = SVGPath("surfacepath")
elm.move_to(*pts[0])
for pt in pts[1:] :
	elm.line_to(*pt)
elm.set_fill(None)
elm.set_stroke( (0,255,255) )
elm.set_stroke_width(crv.stroke_width() )
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
pix.save("delaunay_simple_boundary.png")

dial.show()

qapp.exec_()








