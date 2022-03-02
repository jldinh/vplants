execfile("create_mesh.py")
execfile("create_springs.py")

#############################
#
print "read equilibrium"
#
#############################
from pickle import load
from vplants.plantgl.math import Vector3

eq_pos = load(open("equilibrium_pos.pkl",'rb') )
eq_pos = dict( (pid,Vector3(*tup) ) for pid,tup in eq_pos.iteritems() )

#############################
#
print "compute strain"
#
#############################
from numpy.linalg import eig

fr = spring.local_frame(eq_pos)
strain = fr.global_tensor2(spring.strain(eq_pos) )

w,v = eig(strain)
v1 = Vector3(*tuple(v[:,0]) ) * w[0]
v2 = Vector3(*tuple(v[:,1]) ) * w[1]
if w[1] > w[0] :
	V1,V2 = V2,V1

print "mean strain"
print strain

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
	return size / 2. + vec[0] * sca,\
	       size / 2. - vec[1] * sca

sc = SVGScene(size,size)

execfile("draw_axis.py")

lay = SVGLayer("mesh",size,size,"layer0")
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

lay = SVGLayer("strain",size,size,"layer1")
sc.append(lay)

fid, = mesh.wisps(2)
cent = centroid(mesh,pos,2,fid)

elm = SVGPath("face%.4dV1" % fid)
elm.move_to(*svg_pos(cent - v1 * 30) )
elm.line_to(*svg_pos(cent + v1 * 30) )
elm.set_fill(None)
elm.set_stroke( (255,0,0) )
elm.set_stroke_width(2)
lay.append(elm)

elm = SVGPath("face%.4dV2" % fid)
elm.move_to(*svg_pos(cent - v2 * 30) )
elm.line_to(*svg_pos(cent + v2 * 30) )
elm.set_fill(None)
elm.set_stroke( (0,255,0) )
elm.set_stroke_width(2)
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
dial.setWindowTitle("strain")
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
pix.save("strain.png")

dial.show()

qapp.exec_()








