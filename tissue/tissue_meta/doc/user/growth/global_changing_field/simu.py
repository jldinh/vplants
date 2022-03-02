####################################################
#
print "bijection"
#
####################################################
#begin bijection
from math import pi,atan2,sin,cos
from vplants.plantgl.math import norm,Vector3,Matrix3

def cartesian (crv, uv) :
	u,v = uv
	rot =Matrix3.axisRotation( (0,0,1),2 * pi * v)
	vec = crv.getPointAt(u)
	
	return rot * vec

def uv (crv, vec) :
	alpha = atan2(vec[1],vec[0])
	if alpha < 0 :
		v = 1.  + alpha / (2 * pi)
	else :
		v = alpha / (2 * pi)
	
	pos = (norm( (vec[0],vec[1]) ),0,vec[2])
	pt,u = crv.findClosest(pos)
	
	return u,v

#end bijection
####################################################
#
print "create field steps"
#
####################################################
#begin create steps
from vplants.plantgl.scenegraph import NurbsCurve

#first step
ctrl_pts1 = [(0,0,0,1),(1,0,0,1),(1,0,0,1),(2,0,0,1)]
crv1 = NurbsCurve(ctrl_pts1)

#middle step
ctrl_pts2 = [(0,0,2,1),(3,0,2,1),(4,0,1,1),(5,0,0,1)]
crv2 = NurbsCurve(ctrl_pts2)

#middle step
ctrl_pts3 = [(0,0,4,1),(6,0,4,1),(10,0,3,1),(15,0,0,1)]
crv3 = NurbsCurve(ctrl_pts3)

#last step
ctrl_pts4 = [(0,0,15,1),(6,0,15,1),(15,0,13,1),(15,0,0,1)]
crv4 = NurbsCurve(ctrl_pts4)

#end create steps
####################################################
#
print "create field"
#
####################################################
#begin create field
from vplants.plantgl.scenegraph import NurbsPatch

Gfield = NurbsPatch([ctrl_pts1,
                     ctrl_pts2,
                     ctrl_pts3,
                     ctrl_pts4])

#end create field
####################################################
#
print "create tissue"
#
####################################################
#begin create tissue
from random import random
from openalea.celltissue import Tissue

NB = 24

#create tissue
t = Tissue()
CELL = t.add_type("CELL")
WALL = t.add_type("WALL")
POINT = t.add_type("POINT")
mesh_id = t.add_relation("mesh",(POINT,WALL,CELL) )
mesh = t.relation(mesh_id)

#create cell
cid = mesh.add_wisp(2)

#create points
pids = [mesh.add_wisp(0) for i in xrange(NB)]

uvpos = dict( (pid,(1.,i / float(NB) ) ) for i,pid in enumerate(pids) )

#create walls
for i in xrange(NB) :
	wid = mesh.add_wisp(1)
	mesh.link(1,wid,pids[i])
	mesh.link(1,wid,pids[(i + 1) % NB])
	mesh.link(2,cid,wid)

#associate a property with each cell
prop = dict( (cid,random() ) for cid in mesh.wisps(2) )

#defines cartesian positions for display purpose
crv = Gfield.getUSection(0.)
pos = dict( (pid,cartesian(crv,tup) ) \
            for pid,tup in uvpos.iteritems() )

#end create tissue
####################################################
#
print "create growth func"
#
####################################################
#begin growth func
current_time = 0.
current_space = Gfield.getUSection(0.)

def grow_space () :
	global current_time,current_space
	if current_time < 1 :
		current_time += 0.01
	else :
		current_time = 1.
	current_space = Gfield.getUSection(current_time)

#end growth func
####################################################
#
print "create growth"
#
####################################################
#begin growth
def growth () :
	grow_space()
	for pid,tup in uvpos.iteritems() :
		pos[pid] = cartesian(current_space,tup)

#end growth
####################################################
#
print "find axis"
#
####################################################
#begin find axis
from openalea.tissueshape import face_main_axes_3D

def find_axis (cid) :
	#compute main axis of the cell
	bary,main_axis,V2 = face_main_axes_3D(mesh,pos,cid)
	
	return bary,main_axis

#end find axis
####################################################
#
print "cell division"
#
####################################################
#begin cell division
from openalea.tissueshape import centroid,divide_face

shrink = 20 #(None) #percentage of shrinkage of newly created wall

def is_external_point (pid) :
	for eid in mesh.regions(0,pid) :
		if mesh.nb_regions(1,eid) == 1 :
			return True
	return False

def divide_cell (cid) :
	bary,axis = find_axis(cid)
	#perform division
	lineage = divide_face(mesh,pos,cid,bary,axis)
	
	#shrink
	sca = (100. - shrink) / 100.
	nwid, = lineage[1][None]
	bary = centroid(mesh,pos,1,nwid)
	for pid in mesh.borders(1,nwid) :
		pos[pid] = bary + (pos[pid] - bary) * sca
	
	#uvpos
	for pid in lineage[0][None] :
		uvpos[pid] = uv(current_space,pos[pid])
		if is_external_point(pid) :
			uvpos[pid] = (1.,uvpos[pid][1])
		
		pos[pid] = cartesian(current_space,uvpos[pid])
	
	#prop update
	mem = prop.pop(cid)
	for did in lineage[2][cid] :
		prop[did] = mem

#end cell division
####################################################
#
print "division"
#
####################################################
#begin division
from openalea.tissueshape import face_surface_3D

V_threshold = 1.5 #(m2) #surface above which a cell must divide

def division () :
	for cid in tuple(mesh.wisps(2) ) :
		if face_surface_3D(mesh,pos,cid) > V_threshold :
			divide_cell(cid)

#end division
####################################################
#
print "display func"
#
####################################################
#begin display func
from vplants.plantgl.ext.color import JetMap
from openalea.tissueview import ScalarPropView

Zoffset = 15

cmap = JetMap(0.,1.)
vpos = {}
tsc = ScalarPropView(mesh,vpos,2,prop,10,cmap)

def redraw () :
	for pid,vec in pos.iteritems() :
		vpos[pid] = vec + (0,0,Zoffset)
	tsc.redraw()

#end display func
####################################################
#
print "create scheduler"
#
####################################################
#begin create scheduler
from openalea.scheduler import Scheduler,Task

sch = Scheduler()
sch.register(Task(growth,1,10,"growth") )
sch.register(Task(division,1,9,"division") )
sch.register(Task(redraw,1,0,"redraw") )

#end create scheduler
####################################################
#
print "launch simu"
#
####################################################
#begin launch simu
from openalea.pglviewer import (QApplication,Viewer,
                                LoopView,LoopGUI,
                                TemplateGUI,
                                ViewerGUI,View3DGUI)

loop = LoopView(sch)

gui = TemplateGUI("growth")

def reset_prop () :
	if loop.running() :
		print "pause simulation first"
		return
	
	for cid in prop :
		prop[cid] = random()
	redraw()

gui.add_action_descr("shuffle",reset_prop)

redraw()

qapp = QApplication([])
v = Viewer()
v.add_world(tsc)
v.add_gui(ViewerGUI(vars() ) )
v.add_gui(gui)
v.add_gui(LoopGUI(loop) )
v.add_gui(View3DGUI() )

v.show()
v.view().show_entire_world()
v.view().cursor().set_position( (0,0,Zoffset) )

qapp.exec_()

#end launch simu











