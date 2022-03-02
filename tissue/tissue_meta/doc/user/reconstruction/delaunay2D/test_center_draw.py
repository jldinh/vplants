#############################
#
print "compute delaunay"
#
#############################
execfile("delaunay_simple.py")

cpos = dict( (pid,tuple(vec) ) for pid,vec in pos.iteritems() )
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
print "compute centers"
#
#############################
from openalea.tissueshape import tovec,totup,centroid

pos = tovec(pos)

cell_centers = dict( (fid,centroid(mesh,pos,2,fid) ) \
                     for fid in mesh.wisps(2) )

pos = totup(pos)
cell_centers = totup(cell_centers)
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

pos = dict( (pid,sc.svg_pos(*vec) ) \
        for pid,vec in pos.iteritems() )
cpos = dict( (pid,sc.svg_pos(*vec) ) \
        for pid,vec in cpos.iteritems() )
cell_centers = dict( (pid,sc.svg_pos(*vec) ) \
        for pid,vec in cell_centers.iteritems() )

d = Discretizer()
outer_boundary.apply(d)
pts = [sc.svg_pos(vec[0],vec[1]) for vec in d.result]

sc = SVGScene(*sc.size() )

lay = SVGLayer("voronoi cells",lay.width(),lay.height(),"layer0")
sc.append(lay)

for fid in mesh.wisps(2) :
	coords = [pos[pid] for pid in ordered_pids(mesh,fid)]
	elm = SVGPath("cell%.4d" % fid)
	elm.move_to(*coords[-1])
	for x,y in coords :
		elm.line_to(x,y)
	
	elm.set_fill( (randint(150,255),randint(150,255),randint(150,255) ) )
	
	lay.append(elm)

lay = SVGLayer("cell centroids",lay.width(),lay.height(),"layer1")
sc.append(lay)

for pid,(x,y) in cell_centers.iteritems() :
	elm = SVGSphere(x,y,4,4,"centroid%.4d" % pid)
	elm.set_fill( (0,0,0) )
	lay.append(elm)

lay = SVGLayer("cell centers",lay.width(),lay.height(),"layer2")
sc.append(lay)

for pid,(x,y) in cpos.iteritems() :
	elm = SVGSphere(x,y,2,2,"center%.4d" % pid)
	elm.set_fill( (255,0,0) )
	lay.append(elm)

lay = SVGLayer("outer boundary",lay.width(),lay.height(),"layer3")
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
dial.setWindowTitle("test cell centers")
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
pix.save("test_cell_center.png")

dial.show()

qapp.exec_()








