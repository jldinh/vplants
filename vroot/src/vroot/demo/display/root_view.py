from random import random
from PyQt4.QtCore import SIGNAL
from celltissue.gui import GraphicalTissue,UniformFill,IntensityFill,\
				LabelDescriptor,\
				black,red,JetMap
from openalea.plantgl.all import *
from openalea.plantgl.algo import GLRenderer
from celltissue.gui.pgl import draw2D
from pglviewer.data import SceneView

class Root2DView (SceneView) :
	name="scene"
	def __init__ (self, root) :
		SceneView.__init__(self)
		self._root=root
		t=root.tissue
		pos=root.pos
		#walls
		self._display_walls=True
		self._wall_color=black
		#auxin
		self._display_auxin=True
		#pumps
		self._display_pumps=False
		#pump autoamplification
		self._autoamplified_pumps=False
		#selection
		self.gt_select_cell=GraphicalTissue()
		self.gt_select_cell.add_description(UniformFill(0,t,pos,black))
		self.gt_select_wall=GraphicalTissue()
		self.gt_select_wall.add_description(UniformFill(1,t,pos,black))
		self.redraw()

	#########################################################
	#
	#		emulation of root methods
	#
	#########################################################
	def display_auxin (self, display) :
		self._display_auxin=display
		self.emit(SIGNAL("display auxin"),display)
	
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
		pos=self._root.pos
		layer=0
		if self._display_auxin :
			gt=GraphicalTissue()
			gt.add_description(IntensityFill(r.auxin,t,pos,JetMap(0.,1.,True)))
			draw2D(gt,self,layer)
			layer+=1
		if self._display_walls :
			gt=GraphicalTissue()
			gt.add_description(UniformFill(1,t,pos,self._wall_color))
			draw2D(gt,self,layer)
		if self._display_pumps :
			pump_material=Material( (0,0,0) )
			for wid in t.wisps(1) :
				wgeom=t.geometry(1,wid)
				wcen=wgeom.centroid(pos)
				neigh = [cid for cid in t.regions(1,wid)]
				if len(neigh) == 2 :
				   ccen1=t.geometry(0,neigh[0]).barycenter(pos)
                                   ccen2=t.geometry(0,neigh[1]).barycenter(pos)
				   pos1,pos2=(pos[pid] for pid in wgeom)
				   trans1=(ccen1-wcen)*0.5*r.eP[r.wallgraph.edge(neigh[0],neigh[1])]/10
				   trans2=(ccen2-wcen)*0.5*r.eP[r.wallgraph.edge(neigh[1],neigh[0])]/10
	      			   if (pos2-pos1).cross(trans1)<0 :
			   	      pos2,pos1=pos1,pos2
    			           if (pos2-pos1).cross(trans2)<0 :
				      pos2,pos1=pos1,pos2
                                   trans1_1=(ccen1-pos1)*0.5*r.eP[r.wallgraph.edge(neigh[0],neigh[1])]/10
                                   trans1_2=(ccen1-pos2)*0.5*r.eP[r.wallgraph.edge(neigh[0],neigh[1])]/10
				   trans2_1=(ccen2-pos1)*0.5*r.eP[r.wallgraph.edge(neigh[1],neigh[0])]/10
   				   trans2_2=(ccen2-pos2)*0.5*r.eP[r.wallgraph.edge(neigh[1],neigh[0])]/10
			           pts1=[self.pgl_coords(pos1),
					self.pgl_coords(pos2),
					self.pgl_coords(pos2+trans1_2),
					self.pgl_coords(pos1+trans1_1)]
				   pts2=[self.pgl_coords(pos1),
					self.pgl_coords(pos2),
					self.pgl_coords(pos2+trans2_2),
					self.pgl_coords(pos1+trans2_1)]
				   geom1=FaceSet(pts1,[(0,1,2,3)])
				   geom2=FaceSet(pts2,[(0,1,2,3)])
				   shp1=Shape( geom1,pump_material )
				   shp2=Shape( geom2,pump_material )
				   shp1.id=neigh[0]
				   shp2.id=neigh[1]
				   self+=shp1
				   self+=shp2
			layer+=1
	########################################################
	#
	#		selection
	#
	########################################################
	def select_cell_draw (self, view) :
		sc=SceneView()
		draw2D(self.gt_select_cell,sc)
		sc.selection_draw(view,GLRenderer.SelectionId.ShapeId)
	
	def select_wall_draw (self, view) :
		sc=SceneView()
		draw2D(self.gt_select_wall,sc)
		sc.selection_draw(view,GLRenderer.SelectionId.ShapeId)

