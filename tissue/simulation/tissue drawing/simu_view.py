# -*- python -*-
#
#       simulation.template: example simulation package
#
#       Copyright 2006 INRIA - CIRAD - INRA  
#
#       File author(s): Jerome Chopard <jerome.chopard@sophia.inria.fr>
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
# 
#       OpenAlea WebSite : http://openalea.gforge.inria.fr
#

__doc__="""
This module defines the view on a simulation
"""

__license__= "Cecill-C"
__revision__=" $Id: $ "

from openalea.plantgl.math import Vector2,Vector3
from openalea.plantgl.scenegraph import Material,Shape,Sphere,Polyline2D,Translated,\
										ImageTexture,QuadSet
from openalea.pglviewer import SIGNAL
from openalea.pglviewer.data import SceneView

class SimuView (SceneView) :
	"""
	display the content of a simulation
	"""
	def __init__ (self, global_vars) :
		SceneView.__init__(self)
		self.__dict__.update(global_vars) #allow an easy access to all variables defined in simu.py
		#variables for interaction
		self._display_points = True
		self._display_walls = True
		self._display_cells = True
		self._display_background = True
		#redraw
		self.redraw()
	
	#############################################
	#
	#		interaction
	#
	#############################################
	def display_points (self, display) :
		self._display_points = display
		self.emit(SIGNAL("display_points"),display)
	
	def display_walls (self, display) :
		self._display_walls = display
		self.emit(SIGNAL("display_walls"),display)
	
	def display_cells (self, display) :
		self._display_cells = display
		self.emit(SIGNAL("display_cells"),display)
	
	def display_background (self, display) :
		self._display_background = display
		self.emit(SIGNAL("display_background"),display)
	
	#############################################
	#
	#		draw func
	#
	#############################################
	def redraw (self) :
		"""
		redraw the tissue
		"""
		self.clear()
		#display points
		if self._display_points :
			g = self.t.relation(self.cfg.wall_graph)
			sph = Sphere(10)
			pmat = Material( (255,255,0) )
			for vid in g.vertices() :
				geom = Translated(Vector3(self.pos[vid],0.),sph)
				self.add(Shape(geom,pmat))
		#display walls
		if self._display_walls :
			g = self.t.relation(self.cfg.wall_graph)
			wmat = Material( (0,255,0) )
			for eid in g.edges() :
				geom = Polyline2D([self.pos[g.source(eid)],self.pos[g.target(eid)]])
				self.add(Shape(geom,wmat))
		#display cells
		if self._display_cells :
			g = self.t.relation(self.cfg.cell_graph)
			sph = Sphere(10)
			cmat = Material( (255,0,255) )
			for vid in g.vertices() :
				geom = Translated(Vector3(self.pos[vid],0.),sph)
				self.add(Shape(geom,cmat))
		#display background
		if self._display_background :
			tex = ImageTexture("coleochaete.png")
			geom = QuadSet( [(0,0,-0.1),(960,0,-0.1),(960,932,-0.1),(0,932,-0.1)],
							[(0,1,2,3)] )
			geom.texCoordList = [(0,0),(1,0),(1,1),(0,1)]
			self.add(Shape(geom,tex))
