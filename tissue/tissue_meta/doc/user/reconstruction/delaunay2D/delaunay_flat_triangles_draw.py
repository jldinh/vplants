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
print "find flat triangles"
#
#############################
from openalea.vmanalysis import centroid,circum_center2D,curve_intersect

#read outer boundary curve
crv, = sc.get_layer("outer boundary").elements()
ctrl_pts = [sc.natural_pos(*crv.scene_pos(pt) ) \
            for pt in crv.nurbs_ctrl_points()]
outer_boundary = NurbsCurve.CBezier(ctrl_pts,
                                    False,
                                    200)
segs = {}

for fid in mesh.wisps(2) :
	tr = tuple(pos[pid] for pid in mesh.borders(2,fid,2) )
	G = centroid(mesh,pos,2,fid)
	H = circum_center2D(*tr)
	segs[fid] = (G,H)

flat_tr = set(curve_intersect(outer_boundary,segs) )

regular_tr = set(mesh.wisps(2) ) - flat_tr
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

for fid in regular_tr :
	coords = [pos[pid] for pid in ordered_pids(mesh,fid)]
	elm = SVGPath("triangle%.4d" % fid)
	elm.move_to(*coords[-1])
	for x,y in coords :
		elm.line_to(x,y)
	
	elm.set_fill( (randint(150,255),randint(150,255),randint(150,255) ) )
	
	lay.append(elm)

for fid in flat_tr :
	coords = [pos[pid] for pid in ordered_pids(mesh,fid)]
	elm = SVGPath("triangle%.4d" % fid)
	elm.move_to(*coords[-1])
	for x,y in coords :
		elm.line_to(x,y)
	
	elm.set_fill( (randint(0,80),randint(0,80),randint(0,80) ) )
	
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
pix.save("delaunay_flat_triangles.png")

dial.show()

qapp.exec_()








