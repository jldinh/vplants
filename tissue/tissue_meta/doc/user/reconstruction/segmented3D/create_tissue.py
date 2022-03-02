##########################################
#
print "read image"
#
##########################################
#begin read image
from openalea.image.all import imread

im = imread("segmentation.inr.gz")[100:200,100:200,20:60]

#end read image
##########################################
#
print "extract tissue"
#
##########################################
#begin extract tissue
from segmented_tissue import extract_graph_tissue

db = extract_graph_tissue(im,True)

#end extract tissue
##########################################
#
print "filter tissue"
#
##########################################
#begin filter tissue
from numpy import array

graph = db.get_topology("graph_id")
pos = db.get_property("bary")
V = db.get_property("V")
S = db.get_property("S")
axes = db.get_property("axes")



for vid,vec in pos.items() :
	if vec is None :
		for eid in graph.edges(vid) :
			del S[eid]
		
		graph.remove_vertex(vid)
		del pos[vid]
		del V[vid]
		del axes[vid]

axes = dict( (vid,array(t) ) for vid,t in axes.iteritems() )




#end filter tissue
##########################################
#
print "draw tissue"
#
##########################################
#begin draw tissue
from vplants.plantgl.scenegraph import Material
from openalea.tissueview import GraphView,TensorialPropView

def VRmap (vid) :
	return axes[vid] / 2.#(V[vid] ** 0.33) / 4.

vv = GraphView(graph,pos,"vertex",VRmap,Material( (0,0,255) ) )
vv.redraw()

def ERmap (eid) :
	return (S[eid] ** 0.5) / 10.

ev = GraphView(graph,pos,"edge",ERmap,Material( (0,0,0) ) )
ev.redraw()

tv = TensorialPropView(graph,pos,"vertex",axes,0.5)
tv.redraw()

#end draw tissue
##########################################
#
print "display tissue"
#
##########################################
#begin display tissue
from openalea.pglviewer import QApplication,Viewer

qapp = QApplication([])
v = Viewer()

v.add_world(vv)
v.add_world(ev)
#v.add_world(tv)

v.show()
v.view().show_entire_world()

qapp.exec_()

#end display tissue
