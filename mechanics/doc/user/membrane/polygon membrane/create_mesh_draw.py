execfile("create_mesh.py")

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
from openalea.tissueshape import centroid

sca = 200.
size = 2.5 * sca
fontsize = 24
fw = 10.5 / 2.
fh = 16.3 / 2.

def svg_pos (vec) :
	return size / 2. + vec.x * sca,\
	       size / 2. - vec.y * sca

sc = SVGScene(size,size)

execfile("draw_axis.py")

lay = SVGLayer("faces",size,size,"layer1")
sc.append(lay)

for fid in mesh.wisps(2) :
	cent = centroid(mesh,pos,2,fid)
	pts = [cent + (pos[pid] - cent) * 0.9 for pid in mesh.borders(2,fid,2)]
	
	elm = SVGPath("face%.4d" % fid)
	elm.move_to(*svg_pos(pts[0]) )
	for pt in pts[1:] :
		elm.line_to(*svg_pos(pt) )
	
	elm.close()
	elm.set_fill( (0,255,0) )
	elm.set_stroke(None)
	lay.append(elm)
	
	x,y = svg_pos(cent)
	elm = SVGText(x - fw,
	              y + fh,
	              "%d" % fid,
	              fontsize,
	              "ftxt%.4d" % fid)
	elm.set_fill( (0,0,0) )
	lay.append(elm)

lay = SVGLayer("edges",size,size,"layer2")
sc.append(lay)

for eid in mesh.wisps(1) :
	pt1,pt2 = (pos[pid] for pid in mesh.borders(1,eid) )
	elm = SVGPath("edge%.4d" % eid)
	elm.move_to(*svg_pos(pt1) )
	elm.line_to(*svg_pos(pt2) )
	elm.set_fill(None)
	elm.set_stroke( (0,0,255) )
	elm.set_stroke_width(2)
	lay.append(elm)
	
	x,y = svg_pos( (pt1 + pt2) / 2.)
	elm = SVGText(x - fw,
	              y + fh,
	              "%d" % eid,
	              fontsize,
	              "etxt%.4d" % eid)
	elm.set_fill( (0,0,0) )
	lay.append(elm)

lay = SVGLayer("points",size,size,"layer3")
sc.append(lay)

for pid,vec in pos.iteritems() :
	x,y = svg_pos(vec)
	elm = SVGSphere(x,y,4,4,"point%.4d" % pid)
	elm.set_fill( (0,0,0) )
	lay.append(elm)
	
	x,y = svg_pos(vec + vec * (fontsize / sca / norm(vec) ) )
	elm = SVGText(x - fw,
	              y + fh,
	              "%d" % pid,
	              fontsize,
	              "ptxt%.4d" % pid)
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
dial.setWindowTitle("initial mesh")
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
pix.save("mesh.png")

dial.show()

qapp.exec_()








