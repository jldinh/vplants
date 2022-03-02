from physics.math import xy
from celltissue import open_tissue
from celltissue.shapes.digit import open_svg,create_tissue,simplify_positions,match_tissue
from celltissue.data import TissueProperty
from pglviewer import QApplication,Viewer
from pglviewer.data import SceneView,SceneGUI
#from openalea.plantgl.all import *
from celltissue.gui import GraphicalTissue,UniformFill,WispFill,\
				LabelDescriptor,PositionLabel,\
				Color,black,blue,red,green,yellow
from celltissue.gui.pgl import draw2D

f=open_tissue("mockup02_shortcapped",'r')
t,pos,info=f.read()
f.close()

f=open_svg("root02_shortcapped.svg")
im,=f.images(f.layer("image"))
paths=list(f.paths(f.layer("pumps")))
pumps_pth=[[xy(*im.real_pos(v)) for v in path.as_polyline()] \
				for path in paths]
f.close()

print "matching"
cell_cen=dict( (wid,t.geometry(0,wid).centroid(pos)) for wid in t.wisps(0) )
wall_cen=dict( (wid,t.geometry(1,wid).centroid(pos)) for wid in t.wisps(1) )
pumps={}
for ind,pump in enumerate(pumps_pth) :
	assert len(pump)==2
	cen=reduce(lambda x,y : x+y,pump)/len(pump)
	dist=[ ((cen-wall_cen[wid]).normsquare(),wid) for wid in t.wisps(1) ]
	dist.sort()
	#matched wall
	wid=dist[0][1]
	cid1,cid2=t.regions(1,wid)
	ori=(pump[1]-pump[0]).dot(cell_cen[cid2]-cell_cen[cid1])
	if ori>0 :
		pumps[wid]=(cid1,cid2)
	else :
		pumps[wid]=(cid2,cid1)

for i in pumps.iteritems() :
	print i

pumps_prop=TissueProperty(1,0.,pumps)

gt=GraphicalTissue()
gt.add_description(UniformFill(1,t,pos,black))
gt.add_description(LabelDescriptor(0,t,pos,8,red))
gt.add_description(LabelDescriptor(1,t,pos,8,blue))

sc=SceneView()
draw2D(gt,sc,0)

qapp=QApplication([])
v=Viewer(locals())
v.set_world(SceneGUI(sc))
v.show()
v.set_2D()
qapp.exec_()

f=open_tissue("mockup02_shortcapped",'r')
f.write_property(pumps_prop,"pumps","id of walls and orientation of pumps from sid to tid")
f.close()
