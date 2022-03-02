from celltissue.shapes.digit import open_svg,create_tissue,simplify_positions,match_tissue
from celltissue.data import TissueProperty
from physics.math import xy
from pglviewer import QApplication,Viewer
from pglviewer.data import SceneView,SceneGUI
#from openalea.plantgl.all import *
from celltissue.gui import GraphicalTissue,UniformFill,WispFill,\
				LabelDescriptor,PositionLabel,\
				Color,black,blue,red,green,yellow
from celltissue.gui.pgl import draw2D

f=open_svg("root02.svg")
im,=f.images(f.layer("image"))
t,pos,path_id,style=create_tissue ([pth for pth in f.paths(f.layer("walls"))\
				if pth.style["stroke"]=="#00ff00"],im)
print "created"
threshold=3
t,pos=simplify_positions(t,pos,threshold)
print "simplified"

tb,posb,path_id,style=create_tissue (f.paths(f.layer("celltypes")),im)
trans=match_tissue(tb,posb,t,pos)
print "matched"
f.close()

path_id=TissueProperty(0,{},dict( (trans[wid],pid) for wid,pid in path_id.iteritems()) )
style=TissueProperty(0,{},dict( (trans[wid],sty) for wid,sty in style.iteritems()) )

gt=GraphicalTissue()
gt.add_description(UniformFill(1,t,pos,red))
cell_color=WispFill(0,t,pos)
for cid,sty in style.iteritems() :
	col=Color()
	col.from_string(sty["fill"])
	cell_color[cid]=col
gt.add_description(cell_color)
#gt.add_description(LabelDescriptor(1,t,pos,8,red))
#gt.add_description(PositionLabel(pos,8,blue))
sc=SceneView()
draw2D(gt,sc,0)

#im=ImageView()
#im.load("dome.info")

qapp=QApplication([])
v=Viewer(locals())
v.set_world(SceneGUI(sc))
v.show()
v.set_2D()
qapp.exec_()

from celltissue import open_tissue
f=open_tissue("mockup02",'w')
f.write(t,pos,{})
f.write_property(path_id,"path_id")
f.write_property(style,"style")
f.close()
