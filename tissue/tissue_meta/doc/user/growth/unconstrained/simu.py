###################################################
#
print "nutrient field create"
#
###################################################
#begin nutrient field create
from vplants.plantgl.math import Vector2
from openalea.container import Grid

GS = 10. #(mum) #approximate radius of the field
NB = 21 #(None) #discretization, number of boxes
                #per dimension
BS = GS / NB

#create field
nutrient_field = Grid( (NB,NB) )

#associate a level of nutrient
#with each box of the grid
from random import random
nutrient_level = [0. for i in nutrient_field]

#field geometry
def box_center (bid) :
	"""Compute center of the box
	
	:Parameters:
	 - `bid` (int) - index of the
	   box in the grid
	
	:Returns Type: Vector
	"""
	i,j = nutrient_field.coordinates(bid)
	point = Vector2(i,j) * BS - (GS / 2.,GS / 2.) + (BS / 2.,BS / 2.)
	return point

def box_index (point) :
	"""Find index of the box containing
	the given geometric point.
	
	.. warning:: raise UserWarning if the
	  point lies outside of the field
	
	:Parameters:
	 - `point` (Vector) - position in space
	
	:Returns Type: int
	"""
	if - GS / 2. <= point.x < GS / 2. \
	  and - GS / 2. <= point.y < GS / 2. :
		i = int( (point.x + GS / 2.) / BS)
		j = int( (point.y + GS / 2.) / BS)
		return nutrient_field.index( (i,j) )
	else :
		raise UserWarning("point outside of field")

#end nutrient field create
###################################################
#
print "nutrient field interact"
#
###################################################
#begin nutrient field interact
from vplants.plantgl.math import norm,Vector2

def nutrient_increase (point, radius) :
	"""Increase the level of nutrient
	
	Level of nutrient increased of 2 in
	all boxes located in a sphere of the
	given radius centered on the given
	point.
	
	:Parameters:
	 - `point` (Vector) - point around
	  which nutrient level will increase
	 - `radius` (float) - radius of the
	  sphere in which nutrient will increase
	"""
	for bid,val in enumerate(nutrient_level) :
		if norm(box_center(bid) - point) < radius :
			nutrient_level[bid] = min(10.,val + 2.)

def nutrient_decrease (point, radius) :
	"""decrease the level of nutrient
	
	Level of nutrient decreased of 2 in
	all boxes located in a sphere of the
	given radius centered on the given
	point.
	
	:Parameters:
	 - `point` (Vector) - point around
	  which nutrient level will increase
	 - `radius` (float) - radius of the
	  sphere in which nutrient will increase
	"""
	for bid,val in enumerate(nutrient_level) :
		if norm(box_center(bid) - point) < radius :
			nutrient_level[bid] = max(0.,val - 2.)

#end nutrient field interact
###################################################
#
print "colony create"
#
###################################################
#begin colony create
from openalea.container import Topomesh

mesh = Topomesh(1)
pos = {} #(mum) # position of points
nutrient = {} #(mol) #nutrient stored in each cell

#create a single cell
root = mesh.add_wisp(0)
pos[root] = Vector2(0,- GS / 2.)

pid = mesh.add_wisp(0)
pos[pid] = Vector2(0,1. - GS / 2.)

cid = mesh.add_wisp(1)
mesh.link(1,cid,root)
mesh.link(1,cid,pid)
nutrient[cid] = 0.

#end colony create
###################################################
#
print "colony uptake"
#
###################################################
#begin colony uptake
from random import shuffle

SUBDI = 10
uptake_rate = 0.1 #(mol.mum-1) #uptake of nutrient
                               #per length of cell
dt_uptake = 1. #(s) #time step for uptake

def nutrient_uptake (cid) :
	pt0,pt1 = (pos[pid] for pid in mesh.borders(1,cid) )
	seg = pt1 - pt0
	l = seg.normalize() / SUBDI
	for i in xrange(SUBDI) :
		pt = pt0 + seg * (l * (i + 0.5) )
		try :
			try :
				bid = box_index(pt)
				uptake = min(nutrient_level[bid],l * uptake_rate * dt_uptake)
				nutrient_level[bid] -= uptake
				nutrient[cid] += uptake
			except IndexError :
				print pt
				raise
		except UserWarning :#cell outside of field
			pass

def uptake () :
	cids = list(mesh.wisps(1) )
	shuffle(cids)
	for cid in cids :
		nutrient_uptake(cid)

#end colony uptake
###################################################
#
print "colony growth"
#
###################################################
#begin colony growth
from openalea.tissueshape import edge_length
from openalea.growth import Unconstrained

threshold = 0.1 #(mol) #level of nutrients
               #above which growth saturate
growth_efficiency = 0.09 #(m.s-1) # efficiency
               #of transformation of nutrient
               #in cell material
dt_growth = 1. #(s) #time step for growth

def growth () :
	#defines growth speed
	G = {}
	for cid,val in nutrient.iteritems() :
		if val > 0 :
			val = min(threshold,val)
			nutrient[cid] -= val
			G[cid] = val * growth_efficiency / edge_length(mesh,pos,cid)
		else :
			G[cid] = 0.
	
	#create algo
	algo = Unconstrained(mesh,root,G)
	
	#perform deformation
	algo.grow(pos,dt_growth)

#end colony growth
###################################################
#
print "colony divide"
#
###################################################
#begin colony divide
from openalea.container import topo_divide_edge
from openalea.tissueshape import edge_length

Vthreshold = 1. #(mum) #Volume above which a cell
                       #divide and ramify itself

def divide_cell (cid) :
	pt0,pt1 = (pos[pid] for pid in mesh.borders(1,cid) )
	seg_dir = (pt1 - pt0) / 3.
	N = Vector2(-seg_dir.y,seg_dir.x)
	
	#divide cell
	cid1,cid2,pid1 = topo_divide_edge(mesh,cid)
	cid2,cid3,pid2 = topo_divide_edge(mesh,cid2)
	pos[pid1] = pt0 + seg_dir
	pos[pid2] = pt0 + seg_dir * 2.
	
	#create ramifications
	pid1b = mesh.add_wisp(0)
	pos[pid1b] = pos[pid1] + N
	cid1b = mesh.add_wisp(1)
	mesh.link(1,cid1b,pid1)
	mesh.link(1,cid1b,pid1b)
	
	pid2b = mesh.add_wisp(0)
	pos[pid2b] = pos[pid2] - N
	cid2b = mesh.add_wisp(1)
	mesh.link(1,cid2b,pid2)
	mesh.link(1,cid2b,pid2b)
	
	#properties
	val = nutrient.pop(cid)
	for cid in (cid1,cid2,cid3,cid1b,cid2b) :
		nutrient[cid] = val / 5.

def division () :
	for cid in tuple(mesh.wisps(1) ) :
		if edge_length(mesh,pos,cid) > Vthreshold :
			divide_cell(cid)

#end colony divide
###################################################
#
print "colony display"
#
###################################################
#begin colony display
from vplants.plantgl.ext.color import JetMap
from openalea.tissueview import ScalarPropView

cmap = JetMap(0.,threshold,outside_values = True)
cv = ScalarPropView(mesh,pos,1,nutrient,0,cmap)
cv.set_line_width(2.)

N = []

def redraw_colony () :
	cv.redraw()
	N.append(max(nutrient.values() ) )

#end colony display
###################################################
#
print "nutrient field display"
#
###################################################
#begin nutrient field display
from vplants.plantgl.math import Vector3
from vplants.plantgl.scenegraph import (Shape,Material,Scene,
                                        Sphere,Translated,Scaled)
from openalea.pglviewer import SceneView

mat1 = Material( (100,100,100) )
mat2 = Material( (255,0,255) )
sph = Sphere(0.5)
fv = SceneView()

def redraw_field () :
	sc = Scene()
	
	for bid,val in enumerate(nutrient_level) :
		pt = Vector3(box_center(bid),-BS)
		if val < 1:
			mat = mat1
			sca = 0.1 * BS
		else :
			mat = mat2
			sca = val / 10. * BS
		geom = Translated(pt,Scaled( (sca,sca,sca),sph) )
		sc.add(Shape(geom,mat) )
	
	fv.clear(False)
	fv.merge(sc)

#end nutrient field display
###################################################
#
print "create scheduler"
#
###################################################
#begin create scheduler
from openalea.scheduler import Scheduler,Task

sch = Scheduler()
sch.register(Task(uptake,1,11,"uptake") )
sch.register(Task(growth,1,9,"growth") )
sch.register(Task(division,1,8,"division") )
sch.register(Task(redraw_field,1,1,"redraw_field") )
sch.register(Task(redraw_colony,1,10,"redraw_colony") )

#end create scheduler
###################################################
#
print "defines gui"
#
###################################################
#begin defines gui
from PyQt4.QtCore import QObject,SIGNAL
from openalea.pglviewer import Vec,MouseTool,TemplateGUI

class DrawSphereTool (MouseTool) :
	"""Tool to draw sphere on screen
	"""
	def __init__ (self, parent, txt) :
		MouseTool.__init__(self,parent,txt)
		self._center = None
	
	def mousePressEvent (self, view, event) :
		mpt = event.pos()
		self._center = view.camera().unprojectedCoordinatesOf(Vec(mpt.x(),mpt.y(),0) )
	
	def mouseReleaseEvent (self, view, event) :
		mpt = event.pos()
		pt = view.camera().unprojectedCoordinatesOf(Vec(mpt.x(),mpt.y(),0) )
		R = (pt - self._center).norm()
		self.emit(SIGNAL("sphere drawn"),self._center,R)
		self._center = None

gui = TemplateGUI("field")

tool_increase = DrawSphereTool(None,"inc")

def gui_nut_incr (pt, R) :
	pt = Vector2(pt[0],pt[1])
	nutrient_increase(pt,R)
	redraw_field()

QObject.connect(tool_increase,
                SIGNAL("sphere drawn"),
                gui_nut_incr)

gui.add_tool(tool_increase)

tool_decrease = DrawSphereTool(None,"dec")

def gui_nut_decr (pt, R) :
	pt = Vector2(pt[0],pt[1])
	nutrient_decrease(pt,R)
	redraw_field()

QObject.connect(tool_decrease,
                SIGNAL("sphere drawn"),
                gui_nut_decr)

gui.add_tool(tool_decrease)

#end defines gui
###################################################
#
print "launch simu"
#
###################################################
#begin launch simu
from openalea.pglviewer import (QApplication,Viewer,
                                LoopView,LoopGUI,
                                ViewerGUI,View3DGUI)

loop = LoopView(sch)
redraw_field()
redraw_colony()

qapp = QApplication([])
v = Viewer()
v.add_world(fv)
v.add_world(cv)
v.add_gui(ViewerGUI(vars() ) )
v.add_gui(LoopGUI(loop) )
v.add_gui(gui)
v.add_gui(View3DGUI() )

v.show()
v.view().set_dimension(2)

qapp.exec_()

#end launch simu


