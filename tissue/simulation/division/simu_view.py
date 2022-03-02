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

from openalea.plantgl.math import Vector3
from openalea.plantgl.scenegraph import Material,Shape,Translated,Font,Text
from openalea.pglviewer import SIGNAL
from openalea.pglviewer.scene import SceneView
from openalea.tissueshape import centroid
from openalea.tissueview.mesh_pgl import edge_geom,face_geom2D

class SimuView (SceneView) :
	"""
	display the content of a simulation
	"""
	def __init__ (self, global_vars) :
		SceneView.__init__(self)
		self._global_vars = global_vars
		self.__dict__.update(global_vars) #allow an easy access to all variables defined in simu.py
		self._display_style = "wire"
		self._display_cids = True
		self.redraw()
	
	####################################
	#
	#	interaction
	#
	####################################
	def reload_tissue (self) :
		self.load_tissue()
		self.__dict__.update(self._global_vars)
	
	def display_style (self, style) :
		self._display_style = str(style)
		self.emit(SIGNAL("display_style"),style)
	
	def display_cids (self, display) :
		self._display_cids = display
		self.emit(SIGNAL("display_cids"),display)
	####################################
	#
	#	draw function
	#
	####################################
	def redraw (self) :
		"""
		redraw the tissue
		"""
		self.clear()
		#draw cell walls
		if self._display_style == "wire" :
			mat = Material( (0,0,0) )
			for wid in self.mesh.wisps(1) :
				geom = edge_geom(self.mesh,self.pos,wid)
				self.add(Shape(geom,mat))
		#draw the cytoplasm
		elif self._display_style == "fill" :
			print "fill"
		#draw cytoplasm plus walls
		elif self._display_style == "nurbs" :
			print "nurbs"
		#display cell id
		if self._display_cids :
			mat = Material( (255,0,255) )
			font = Font("ariana",8)
			for cid in self.mesh.wisps(2) :
				vec = centroid(self.mesh,self.pos,2,cid)
				geom = Text("%d" % cid,Vector3(vec,0.1),False,font)
				self.add(Shape(geom,mat))
