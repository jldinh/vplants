###########################################
#
print "bijection"
#
###########################################
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
###########################################
#
print "create field"
#
###########################################
#begin create field
from vplants.plantgl.scenegraph import NurbsCurve

ctrl_pts = [(0,0,0,1),(6,0,0,1),(15,0,-2,1),(15,0,-15,1)]
Gfield = NurbsCurve(ctrl_pts)

#end create field
###########################################
#
print "create tissue"
#
###########################################
#begin create tissue
from random import random
from openalea.celltissue import Tissue

#create tissue
t = Tissue()
CELL = t.add_type("CELL")
WALL = t.add_type("WALL")
POINT = t.add_type("POINT")
mesh_id = t.add_relation("mesh",(POINT,WALL,CELL) )
mesh = t.relation(mesh_id)

#create cells
cells = [mesh.add_wisp(2) for i in xrange(6)]

#create points
pids_int = [mesh.add_wisp(0) for i in xrange(6)]
pids_ext = [mesh.add_wisp(0) for i in xrange(6)]

uvpos = {}
for i,pid in enumerate(pids_int) :
	uvpos[pid] = (0.02,i / 6.)
for i,pid in enumerate(pids_ext) :
	uvpos[pid] = (0.05,i / 6.)

#create walls
for i in xrange(6) :
	#internal
	wid = mesh.add_wisp(1)
	mesh.link(1,wid,pids_int[i])
	mesh.link(1,wid,pids_int[(i + 1) % 6])
	mesh.link(2,cells[i],wid)
	
	#external
	wid = mesh.add_wisp(1)
	mesh.link(1,wid,pids_ext[i])
	mesh.link(1,wid,pids_ext[(i + 1) % 6])
	mesh.link(2,cells[i],wid)
	
	#transversal
	wid = mesh.add_wisp(1)
	mesh.link(1,wid,pids_ext[i])
	mesh.link(1,wid,pids_int[i])
	mesh.link(2,cells[i],wid)
	mesh.link(2,cells[(i - 1) % 6],wid)

#associate a property with each cell
prop = dict( (cid,random() ) for cid in mesh.wisps(2) )

#defines cartesian positions for display purpose
pos = dict( (pid,cartesian(Gfield,tup) ) \
            for pid,tup in uvpos.iteritems() )

#end create tissue
###########################################
#
print "growth func"
#
###########################################
#begin growth func
def grow_point (u, v) :
	if u > 0.3 :
		return u * 1.03,v
	elif u > 0.2 :
		return u * 1.02,v
	elif u > 0.03 :
		return u * 1.01,v
	else :
		return u,v

#end growth func
###########################################
#
print "grow space"
#
###########################################
#begin grow space
def growth () :
	for pid,tup in uvpos.iteritems() :
		uvpos[pid] = grow_point(*tup)
		pos[pid] = cartesian(Gfield,uvpos[pid])

#end grow space
###########################################
#
print "find axis"
#
###########################################
#begin find axis
from openalea.tissueshape import face_main_axes_3D

def find_axis (cid) :
	#compute main axis of the cell
	bary,main_axis,V2 = face_main_axes_3D(mesh,pos,cid)
	
	#compute principal axes of the growth field
	u,v = uv(Gfield,bary)
	rot = Matrix3.axisRotation( (0,0,1),v * 2 * pi)
	V1 = rot * Gfield.getTangentAt(u)
	N = rot * Gfield.getNormalAt(u)
	V2 = V1 ^ N
	
	#compare them
	main_axis /= norm(main_axis)
	V1 /= norm(V1)
	if V1 * main_axis < 0 :
		V1 *= -1
	V2.normalize()
	if V2 * main_axis < 0 :
		V2 *= -1
	
	#return most aligned one
	if norm(V1 - main_axis) < norm(V2 - main_axis) :
		return bary,V1
	else :
		return bary,V2

#end find axis
###########################################
#
print "cell division"
#
###########################################
#begin cell division
from openalea.tissueshape import centroid,divide_face

shrink = 20 #(None) #percentage of shrinkage of newly created wall

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
		uvpos[pid] = uv(Gfield,pos[pid])
		pos[pid] = cartesian(Gfield,uvpos[pid])
	
	#prop update
	mem = prop.pop(cid)
	for did in lineage[2][cid] :
		prop[did] = mem

#end cell division
###########################################
#
print "division"
#
###########################################
#begin division
from openalea.tissueshape import face_surface_3D

V_threshold = 1.5 #(m2) #surface above which a cell must divide

def division () :
	for cid in tuple(mesh.wisps(2) ) :
		if face_surface_3D(mesh,pos,cid) > V_threshold :
			divide_cell(cid)

#end division
###########################################
#
print "prunning"
#
###########################################
#begin prunning
ulim = 0.9

def prunning () :
	to_remove = set()
	for pid,(u,v) in uvpos.iteritems() :
		if u > ulim :
			for eid in mesh.regions(0,pid) :
				to_remove.update(mesh.regions(1,eid) )
	
	for cid in to_remove :
		#properties
		del prop[cid]
		
		#mesh
		edges = tuple(mesh.borders(2,cid) )
		mesh.remove_wisp(2,cid)
		
		pids = set()
		for eid in edges :
			if mesh.nb_regions(1,eid) == 0 :
				pids.update(mesh.borders(1,eid) )
				mesh.remove_wisp(1,eid)
		
		for pid in pids :
			if mesh.nb_regions(0,pid) == 0 :
				del pos[pid]
				del uvpos[pid]
				mesh.remove_wisp(0,pid)

#end prunning
###########################################
#
print "display func"
#
###########################################
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
###########################################
#
print "create scheduler"
#
###########################################
#begin create scheduler
from openalea.scheduler import Scheduler,Task

sch = Scheduler()
sch.register(Task(growth,1,10,"growth") )
sch.register(Task(division,1,9,"division") )
sch.register(Task(prunning,1,8,"prunning") )
sch.register(Task(redraw,1,0,"redraw") )

#end create scheduler
###########################################
#
print "launch simu"
#
###########################################
#begin launch simu
from openalea.pglviewer import (QApplication,Viewer,
                                LoopView,LoopGUI,
                                TemplateGUI,
                                ViewerGUI,View3DGUI)

loop = LoopView(sch)

gui = TemplateGUI("growth")

def reset_prop () :
	loop_running = False
	if loop.running() :
		loop_running = True
		loop.pause()
	
	for cid in prop :
		prop[cid] = random()
	redraw()
	
	if loop_running :
		loop.play()

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

