############################################
#
print "create graph"
#
############################################
from random import sample,uniform
from numpy.random import uniform as muni
from openalea.container import Graph

graph = Graph()

vtx = [graph.add_vertex() for i in range(10)]

for i in xrange(20) :
	sid,tid = sample(vtx,2)
	
	graph.add_edge(sid,tid)

pos = dict( (vid,muni(-10.,10.,3) ) for vid in vtx)

R = dict( (vid,uniform(0.1,0.5) ) for vid in vtx)

############################################
#
print "draw graph"
#
############################################
from vplants.plantgl.scenegraph import Material
from openalea.tissueview import draw_graph
from openalea.pglviewer import SceneView

def Rmap (vid) :
	return R[vid]

def cmap (vid) :
	return Material( (255,0,0) )

vv = SceneView()
vv.merge(draw_graph(graph,pos,"vertex",Rmap,cmap) )

def ERmap (eid) :
	return uniform(0.1,0.4)

ev = SceneView()
ev.merge(draw_graph(graph,pos,"edge",ERmap,Material( (0,255,0) ) ) )

############################################
#
print "display graph"
#
############################################
from openalea.pglviewer import QApplication,Viewer

qapp = QApplication([])
v = Viewer()

v.add_world(vv)
v.add_world(ev)

v.show()
v.view().show_entire_world()

qapp.exec_()


