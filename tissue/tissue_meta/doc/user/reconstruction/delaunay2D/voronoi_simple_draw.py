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

#put point in infinity
from openalea.tissueshape import tovec,totup

pos = tovec(pos)
dangling_eids = set(eid for eid in mesh.wisps(1) \
            if len(set(mesh.borders(1,eid) ) & dangling_pids) == 2)

for pid in dangling_pids :
	eid, = set(mesh.regions(0,pid) ) - dangling_eids
	spid, = set(mesh.borders(1,eid) ) - set([pid])
	tpid = pid
	
	seg_ori = pos[tpid] - pos[spid]
	seg_ori.normalize()
	pos[tpid] += seg_ori * 300

pos = totup(pos)
#############################
#
print "draw result"
#
#############################
from random import randint
from pickle import dump
from openalea.tissueshape import ordered_pids
from openalea.svgdraw import to_xml, \
                             SVGScene,SVGLayer,\
                             SVGSphere,SVGConnector,\
                             SVGPath

pos = dict( (pid,sc.svg_pos(*vec) ) for pid,vec in pos.iteritems() )

sc = SVGScene(*sc.size() )

lay = SVGLayer("voronoi cells",lay.width(),lay.height(),"layer0")
sc.append(lay)

cell_color = dict( (fid,(randint(0,255),
                         randint(0,255),
                         randint(0,255) ) ) for fid in mesh.wisps(2) )
dump(cell_color,open("vor_cell_color.pkl",'w') )

for fid,col in cell_color.iteritems() :
	coords = [pos[pid] for pid in ordered_pids(mesh,fid)]
	elm = SVGPath("cell%.4d" % fid)
	elm.move_to(*coords[-1])
	for x,y in coords :
		elm.line_to(x,y)
	
	elm.set_fill(col)
	
	lay.append(elm)

lay = SVGLayer("vertices",lay.width(),lay.height(),"layer1")
sc.append(lay)

for pid,(x,y) in pos.iteritems() :
	elm = SVGSphere(x,y,2,2,"vtx%.4d" % pid)
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
dial.setWindowTitle("simple voronoi 2D")
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
pix.save("voronoi_simple.png")

dial.show()

qapp.exec_()








