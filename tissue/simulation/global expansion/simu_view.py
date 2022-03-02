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

from vplants.plantgl.math import Vector3
from vplants.plantgl.scenegraph import Sphere,Polyline,Text,Translated,Material,Font,Shape
from vplants.plantgl.algo import Discretizer
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
		self._display_points = False
		self._display_pids = False
		self._display_mesh = True
		self._display_field = True
		#redraw
		self.redraw(0.)
	####################################
	#
	#	interaction
	#
	####################################
	def display_points (self, display) :
		self._display_points = display
		self.emit(SIGNAL("display_points"),display)
	
	def display_pids (self, display) :
		self._display_pids = display
		self.emit(SIGNAL("display_pids"),display)
	
	def display_mesh (self, display) :
		self._display_mesh = display
		self.emit(SIGNAL("display_mesh"),display)
	
	def display_field (self, display) :
		self._display_field = display
		self.emit(SIGNAL("display_field"),display)
	####################################
	#
	#	draw function
	#
	####################################
	def redraw (self, time) :
		"""
		redraw the tissue
		"""
		self.clear()
		#display points
		if self._display_points :
			mat = Material( (0,0,255) )
			sph = Sphere(2.)
			for pid,v in self.pos.iteritems() :
				geom = Translated(v,sph)
				shp = Shape(geom,mat)
				self.add(shp)
		#display pids
		if self._display_pids :
			pts_mat = Material( (0,0,255) )
			font = Font("ariana",8)
			for pid,v in self.pos.iteritems() :
				geom = Text("%d" % pid,Vector3(v[0],v[1],0.1),False,font)
				self.add(Shape(geom,pts_mat))
		#display mesh
		if self._display_mesh :
			mesh = self.t.relation(self.cfg.mesh_id)
			mat = Material( (0,255,0) )
			for wid in mesh.wisps(1) :
				geom = Polyline([self.pos[pid] for pid in mesh.borders(1,wid)])
				self.add(Shape(geom,mat))
		#display field
		if self._display_field :
			mat = Material( (80,80,255) )
			patch = self.field.getUPatch(time)
			shp = Shape(patch,mat)
			d = Discretizer()
			shp.apply(d)
			for triangle in d.discretization.indexList :
				geom = Polyline([d.discretization.pointList[triangle[i%3]] for i in xrange(4)])
				self.add(Shape(Translated( (0,0,-0.1),geom),mat))

