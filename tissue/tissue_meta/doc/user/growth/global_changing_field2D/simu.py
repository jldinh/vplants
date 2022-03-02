######################################################
#
print "bijection"
#
######################################################
#begin bijection
from math import pi,atan2,sin,cos
from vplants.plantgl.math import norm,Vector3,Vector4
from vplants.plantgl.scenegraph import NurbsCurve,Polyline

tol = 1e-3

def cartesian (patch, uv) :
	u,v = uv
	i1 = int(v * len(patch) )
	i2 = i1 + 1
	weight = v * len(patch) - i1
	if i1 == 0 :
		vec1 = Vector3(0,0,0)
	else :
		crv1 = NurbsCurve([Vector4(tup[0],tup[1],0,1) \
		                  for tup in patch[i1 - 1] ])
		vec1 = crv1.getPointAt(u)
	if i2 > (len(patch) - 1) :
		vec2 = vec1
	else :
		crv2 = NurbsCurve([Vector4(tup[0],tup[1],0,1) \
		                  for tup in patch[i2 - 1] ])
		vec2 = crv2.getPointAt(u)
	
	vec3 = vec1 * (1 - weight) + vec2 * weight
	return (vec3.x,vec3.y)

def uv (patch, vec) :
	vec = Vector3(vec)
	if norm(vec) < tol :
		return 0.,0.
	
	crv_inf = NurbsCurve([Vector4(0,0,0,1)] * 4)
	pt_inf = Vector3(0,0,0)
	u_inf = 0.
	for i,ctrl_pts in enumerate(patch) :
		crv_sup = NurbsCurve([Vector4(tup[0],tup[1],0,1) \
		                  for tup in ctrl_pts])
		pt_sup,u_sup = crv_sup.findClosest(vec)
		
		if (vec - pt_inf) * (vec - pt_sup) < 0. :
			crv_left = Polyline([crv_inf.getPointAt(0.),
			                     crv_sup.getPointAt(0.)])
			pt_left,v_left = crv_left.findClosest(vec)
			if norm(vec - pt_left) < tol :
				return 0.,(i + v_left) / len(patch)
			
			for j in xrange(101) :
				crv_right = Polyline([crv_inf.getPointAt( (j + 1) / 101. ),
				                      crv_sup.getPointAt( (j + 1) / 101. )])
				pt_right,v_right = crv_right.findClosest(vec)
				
				if (vec - pt_left) * (vec - pt_right) < 0. :
					d = norm(vec - pt_left) / norm(pt_right - pt_left)
					v = (i + v_left * (1 - d) + v_right * d) / len(patch)
					u = (j + d) / 101.
					if u < tol :
						u = 0.
					
					return u,v
				
				crv_left = crv_right
				pt_left = pt_right
				v_left = v_right
			
			return 1.,(i + v_left) / len(patch)
		
		crv_inf = crv_sup
		pt_inf = pt_sup
		u_inf = u_sup
	
	if u_inf < tol :
		u_inf = 0
	return u_inf,1.

#end bijection
######################################################
#
print "read space frames"
#
######################################################
#begin space frames
from vplants.plantgl.math import Vector2
from openalea.svgdraw import open_svg

f = open_svg("growth_field.svg",'r')
sc = f.read()
f.close()

#stage0
lay = sc.get_layer("frame0")

crvs = []
for pth in lay.elements() :
	ctrl_pts = [sc.natural_pos(*pth.scene_pos(pt) ) \
	            for pt in pth.nurbs_ctrl_points()]
	crvs.append( (ctrl_pts[0][1],
	              ctrl_pts,
	              (ctrl_pts[0][0],ctrl_pts[-1][1]) ) )

crvs.sort()
frame0_patch = [[Vector2(tup[0] - off[0],tup[1] - off[1]) \
                for tup in crv]\
                for pt,crv,off in crvs]

#stage1
lay = sc.get_layer("frame1")

crvs = []
for pth in lay.elements() :
	ctrl_pts = [sc.natural_pos(*pth.scene_pos(pt) ) \
	            for pt in pth.nurbs_ctrl_points()]
	crvs.append( (ctrl_pts[0][1],
	              ctrl_pts,
	              (ctrl_pts[0][0],ctrl_pts[-1][1]) ) )

crvs.sort()
frame1_patch = [[Vector2(tup[0] - off[0],tup[1] - off[1]) \
                for tup in crv]\
                for pt,crv,off in crvs]

#end space frames
######################################################
#
print "create space"
#
######################################################
#begin create space
def space_field (t) :
	"""Compute geometry of space at time t
	
	:Parameters:
	 - `t` (float) - between 0 and 1
	
	:Return: a list of curves ctrl_points
	
	:Retuns Type: list of list of (float,float)
	"""
	return [[pt * (1 - t) + frame1_patch[i][j] * t \
	         for j,pt in enumerate(crv)] \
	         for i,crv in enumerate(frame0_patch)]

#end create space
######################################################
#
print "create tissue"
#
######################################################
#begin create tissue
from random import random
from openalea.celltissue import Tissue

NB = 16 #(None) #number of cells in L1

#create tissue
t = Tissue()
CELL = t.add_type("CELL")
WALL = t.add_type("WALL")
POINT = t.add_type("POINT")
mesh_id = t.add_relation("mesh",(POINT,WALL,CELL) )
mesh = t.relation(mesh_id)

#create cell
cid = mesh.add_wisp(2)
L1_cids = [mesh.add_wisp(2) for i in xrange(NB)]

#create points
uvpos = {}
cent = mesh.add_wisp(0)
uvpos[cent] = (0,0)

L1ext_pids = [mesh.add_wisp(0) for i in xrange(NB + 1)]
uvpos.update( (pid,(i / float(NB),1.) ) for i,pid in enumerate(L1ext_pids) )

L1int_pids = [mesh.add_wisp(0) for i in xrange(NB + 1)]
uvpos.update( (pid,(i / float(NB),4./ 5.) ) for i,pid in enumerate(L1int_pids) )

#create walls
wid = mesh.add_wisp(1)
mesh.link(1,wid,cent)
mesh.link(1,wid,L1int_pids[0])
mesh.link(2,cid,wid)

wid = mesh.add_wisp(1)
mesh.link(1,wid,cent)
mesh.link(1,wid,L1int_pids[-1])
mesh.link(2,cid,wid)

for i in xrange(NB) :
	#L1ext
	wid = mesh.add_wisp(1)
	mesh.link(1,wid,L1ext_pids[i])
	mesh.link(1,wid,L1ext_pids[i + 1])
	mesh.link(2,L1_cids[i],wid)
	#L1int
	wid = mesh.add_wisp(1)
	mesh.link(1,wid,L1int_pids[i])
	mesh.link(1,wid,L1int_pids[i + 1])
	mesh.link(2,L1_cids[i],wid)
	mesh.link(2,cid,wid)

#L1trans
for i in xrange(NB + 1) :
	wid = mesh.add_wisp(1)
	mesh.link(1,wid,L1ext_pids[i])
	mesh.link(1,wid,L1int_pids[i])
	if i > 0 :
		mesh.link(2,L1_cids[i - 1],wid)
	if i < NB :
		mesh.link(2,L1_cids[i],wid)

#associate a property with each cell
prop = dict( (cid,0.35 + random() * 0.3 ) for cid in mesh.wisps(2) )

#create L1 propertys
L1 = set(L1_cids)

#defines cartesian positions for display purpose
patch = space_field(0.)
pos = dict( (pid,cartesian(patch,tup) ) \
            for pid,tup in uvpos.iteritems() )

#end create tissue
######################################################
#
print "growth func"
#
######################################################
#begin Gfunc
current_time = 0.
current_space = space_field(0.)

def grow_space () :
	global current_time,current_space
	if current_time < 1 :
		current_time += 0.01
	else :
		current_time = 1.
	current_space = space_field(current_time)

#end Gfunc
######################################################
#
print "growth"
#
######################################################
#begin growth
def growth () :
	grow_space()
	for pid,tup in uvpos.iteritems() :
		pos[pid] = cartesian(current_space,tup)

#end growth
######################################################
#
print "find axis"
#
######################################################
#begin find axis
from openalea.tissueshape import centroid,face_main_axes_2D

def find_axis (cid) :
	if cid in L1 :
		#compute normal to surface
		pt = centroid(mesh,pos,2,cid)
		uvpt = uv(current_space,pt)
		crv = NurbsCurve([Vector4(tup[0],tup[1],0,1) \
		                  for tup in current_space[-1] ])
		N = crv.getNormalAt(uvpt[0])
		axis = (-N.y,N.x)
	else :
		#compute main axis of the cell
		pt,axis,V2 = face_main_axes_2D(mesh,pos,cid)
	
	return pt,axis

#end find axis
######################################################
#
print "cell division"
#
######################################################
#begin cell division
from openalea.tissueshape import centroid,divide_face

shrink = 20 #(None) #percentage of shrinkage of newly created wall

def is_internal_point (pid) :
	for eid in mesh.regions(0,pid) :
		if mesh.nb_regions(1,eid) == 1 :
			return False
	return True

def is_L1_point (pid) :
	for eid in mesh.regions(0,pid) :
		for cid in mesh.regions(1,eid) :
			if cid in L1 :
				return True
	return False

def divide_cell (cid) :
	bary,axis = find_axis(cid)
	#perform division
	lineage = divide_face(mesh,pos,cid,bary,axis)
	
	#prop update
	mem = prop.pop(cid)
	for did in lineage[2][cid] :
		prop[did] = mem
	
	if cid in L1 :
		L1.discard(cid)
		L1.update(lineage[2][cid])
	
	#shrink
	nwid, = lineage[1][None]
	bary = centroid(mesh,pos,1,nwid)
	for pid in mesh.borders(1,nwid) :
		if is_internal_point(pid) :
			if is_L1_point(pid) :
				sca = (100. - shrink / 10.) / 100.
			else :
				sca = (100. - shrink) / 100.
			pos[pid] = bary + (pos[pid] - bary) * sca
	
	#uvpos
	for pid in lineage[0][None] :
		uvpos[pid] = uv(current_space,pos[pid])
		if (not is_internal_point(pid) ) \
		   and is_L1_point(pid) :
			uvpos[pid] = (uvpos[pid][0],1.)
		pos[pid] = cartesian(current_space,uvpos[pid])

#end cell division
######################################################
#
print "division"
#
######################################################
#begin division
from openalea.tissueshape import face_surface_2D

V_threshold = 550 #(m2) #surface above which a cell must divide

def division () :
	division_occurs = False
	for cid in tuple(mesh.wisps(2) ) :
		if face_surface_2D(mesh,pos,cid) > V_threshold :
			divide_cell(cid)
			division_occurs = True
	
	return division_occurs

#end division
######################################################
#
print "display func"
#
######################################################
#begin display func
from vplants.plantgl.ext.color import JetMap
from vplants.plantgl.scenegraph import Material
from openalea.tissueview import ScalarPropView,MeshView2D

cmap = JetMap(0.,1.)

cv = ScalarPropView(mesh,pos,2,prop,0,cmap)
wv = MeshView2D(mesh,pos,1,0,Material( (0,0,0) ),0.1)

def redraw () :
	cv.redraw(False)
	wv.redraw()

#end dislay func
######################################################
#
print "create scheduler"
#
######################################################
#begin create scheduler
from openalea.scheduler import Scheduler,Task

sch = Scheduler()
sch.register(Task(growth,1,10,"growth") )
sch.register(Task(division,1,9,"division") )
sch.register(Task(redraw,1,0,"redraw") )

#end create scheduler
######################################################
#
print "launch simu"
#
######################################################
#begin launch simu
from openalea.pglviewer import (QApplication,Viewer,
                                LoopView,LoopGUI,
                                TemplateGUI,
                                ViewerGUI,View3DGUI)

#divide big L3 cell
while division() :
	print "ini div"

#create GUI
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

#launch
reset_prop()

qapp = QApplication([])
v = Viewer()
v.add_world(cv)
v.add_world(wv)
v.add_gui(ViewerGUI(vars() ) )
v.add_gui(gui)
v.add_gui(LoopGUI(loop) )
v.add_gui(View3DGUI() )

v.show()
v.view().set_dimension(2)

qapp.exec_()

#end launch simu



























