from random import random
from PyQt4.QtCore import SIGNAL
from openalea.plantgl.scenegraph import Color3,Color4,Material
from openalea.plantgl.algo import GLRenderer
from openalea.pglviewer.data import FramedSceneView
from openalea.celltissue.gui import nurb_wall_cell, nurb_wall_pump_cell, polygonal_cell
from openalea.plantgl.ext.geom.color import red,green,blue,yellow,magenta,cyan,white,black,ColorRange,JetMap

class GreenMap (ColorRange):
	def __init__ (self, val_min=0., val_max=1., outside_value=False) :
		ColorRange.__init__(self,(val_min,val_max),
				[black,green],outside_values=outside_value)

default_mat=Material( (0,0,0),0.,(0,0,0),(0,0,0),0 )

class Root2DView (FramedSceneView) :
	def __init__ (self, root) :
		FramedSceneView.__init__(self)
		self._root=root
		t=root.tissue
		pos=root.position
		#basic cell shape
		self._display_base_cells=True
		#walls
		self._display_walls=False
		#pumps
		self._display_pumps=False
		#pump autoamplification
		self._autoamplified_pumps=False
		#display
		self.wall_thickness_min=0.1
		self.wall_thickness_max=1.

           	self.wall_color=Color4(0,0,0,255)
		self.pump_color=Color4(255,0,0,255)
		self.cell_color=GreenMap(0.,1.,True)

		#self.wall_color=Color4(0,0,0,255)
		#self.pump_color=Color4(50,50,150,255)
		#self.cell_color=JetMap(0.,1.,True)

		self.redraw()

	def cell_shape (self, cid) :
		root=self._root
		corners=[root.position[pid] for pid in root.cell_corners[cid]]
		col=self.cell_color(root.auxin[cid]).i4tuple()
		return polygonal_cell(corners,col)

	def wall_cell_shape (self, cid) :
		root=self._root
		corners=[root.position[pid] for pid in root.cell_corners[cid]]
		col=self.cell_color(root.auxin[cid]).i4tuple()
		shp=nurb_wall_cell(corners, self.wall_thickness_min, col, self.wall_color, 100, 3)
		return shp

	def pump_cell_shape (self, cid) :
		root=self._root
		corner_ids=root.cell_corners[cid]
		corners=[root.position[pid] for pid in corner_ids]
		g=root.transport_graph()
		cg=root.corner_graph()
		nb=len(corners)
		pumps=[0.]*nb
		for pump_id in g.out_edges(cid) :
			wid=root.wall(pump_id)
			sid=cg.source(wid)
			tid=cg.target(wid)
			for i in xrange(nb) :
				if corner_ids[i] in (sid,tid) \
				   and corner_ids[(i+1)%nb] in (sid,tid) :
					pumps[i]=root.relative_pumps[pump_id]
		col=self.cell_color(root.auxin[cid]).i4tuple()
		shp=nurb_wall_pump_cell(corners,pumps,
						self.wall_thickness_min,
						self.wall_thickness_max,
						col,self.pump_color,self.wall_color,
						100,3)
		return shp

	def line_pump_cell_shape (self, cid) :
		root=self._root
		shp=self.wall_cell_shape(cid)
		corners=[root.position[pid] for pid in root.cell_corners[cid]]
		cent=sum(corners,Vector3())/len(corners)
		cent[2]=1.
		g=root.transport_graph()
		cg=root.corner_graph()
		pumps=[]
		for pump_id in g.out_edges(cid) :
			if root.relative_pumps[pump_id]>0.5 :
				wid=root.wall(pump_id)
				mid=(root.position[cg.source(wid)]+root.position[cg.target(wid)])/2.
				mid[2]=1.
				pumps.append(Polyline([cent,mid]))
		shp.geometry=Group([shp.geometry]+pumps)
		return shp

	#########################################################
	#
	#		emulation of root gui
	#
	#########################################################
	def display_base_cells (self, display) :
		self._display_base_cells=display
		self.emit(SIGNAL("display base cells"),display)

	def display_walls (self, display) :
		self._display_walls=display
		self.emit(SIGNAL("display walls"),display)

	def display_pumps (self, display) :
		self._display_pumps=display
		self.emit(SIGNAL("display pumps"),display)

	def autoamplified_pumps (self, display) :
	        self._autoamplified_pumps=display
	        self.emit(SIGNAL("autoamplified pumps"),display)

	#########################################################
	#
	#		drawable
	#
	#########################################################
	def pgl_coords (self, vec) :
		return vec.x,vec.y,0.02

	def redraw (self) :
		self.clear()
		r=self._root
		t=self._root.tissue
		pos=self._root.position
		layer=0
		if self._display_base_cells :
			draw_func=self.cell_shape
		elif self._display_walls :
			draw_func=self.wall_cell_shape
		elif self._display_pumps :
			draw_func=self.pump_cell_shape
		else :
			draw_func=None
		if draw_func is not None :
			for cid in r.cells() :
				shp=draw_func(cid)
				shp.appearance=default_mat
				self.add(shp)
	########################################################
	#
	#		selection
	#
	########################################################
	def select_cell_draw (self, view) :
		sc=FramedSceneView()
		sc.frame().setPosition(self.frame().position())
		sc.frame().setOrientation(self.frame().orientation())
		for cid in self._root.cells() :
			shp=self.cell_shape(cid)
			shp.id=cid
			sc.add(shp)
		sc.selection_draw(view,GLRenderer.SelectionId.ShapeId)

#	def select_wall_draw (self, view) :
#		sc=SceneView()
#		draw2D(self.gt_select_wall,sc)
#		sc.selection_draw(view,GLRenderer.SelectionId.ShapeId)
