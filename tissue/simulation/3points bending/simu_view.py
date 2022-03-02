# -*- python -*-
#
#       simulation.3points bending: example simulation package for mass spring systems
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

import matplotlib
matplotlib.use('Qt4Agg')
from pylab import clf,plot,show,xlim,ylim,legend

from PyQt4.QtCore import SIGNAL
from openalea.plantgl.math import Vector3,Vector2
from openalea.plantgl.scenegraph import Material,Shape,Translated,Sphere,Polyline,Text,Font
from openalea.pglviewer.data import SceneView
from openalea.tissueshape import edge_geom,face_geom_2D

class Record (list) :
	"""
	a simple container for a plot
	"""
	def __init__ (self, col, scale) :
		list.__init__(self)
		self.color = col
		self.scale = scale

class SimuView (SceneView) :
	"""
	display the content of a simulation
	"""
	def __init__ (self, global_vars) :
		SceneView.__init__(self)
		self.__dict__.update(global_vars) #allow an easy access to all variables defined in simu.py
		self.times = []
		self.records = {"deformation":Record('r',1.),"width":Record('g',0.3),"load":Record('b',1.)}
		self.top_line = dict( (pid,self.pos[pid] + Vector2(0,0.3)) for pid in self.cfg.top_points )
		self._display_pid = False
		self._display_fixed = True
		self._display_top = False
		self._display_load = True
		self.redraw()
	
	def update_info (self, time) :
		self.times.append(time)
		self.records["deformation"].append(self.deformation())
		self.records["width"].append(self.geom_width())
		self.records["load"].append(self.load(self.mid_top_point))
	
	def redraw (self) :
		"""
		redraw the tissue
		"""
		self.clear()
		#draw walls
		wall_mat = Material( (0,0,0) )
		for eid in self.mesh.wisps(1) :
			geom = edge_geom(self.mesh,self.pos,eid)
			self.add(Shape(geom,wall_mat))
		#draw points
		if self._display_pid :
			pts_mat = Material( (0,0,255) )
			font = Font("ariana",8)
			for pid in self.mesh.wisps(0) :
				geom = Text("%d" % pid,Vector3(self.pos[pid],0.1),False,font)
				self.add(Shape(geom,pts_mat))
		#draw additional elements
		sph = Sphere(0.3)
		if self._display_fixed :
			mat = Material( (255,0,0) )
			for pid in self.fixed_points :
				vec = Vector3(self.pos[pid],0)
				geom = Translated(vec,sph)
				self.add(Shape(geom,mat))
		if self._display_top :
			mat = Material( (0,0,100) )
			for pid in self.cfg.top_points :
				vec = Vector3(self.pos[pid],0)
				geom = Translated(vec,sph)
				self.add(Shape(geom,mat))
		#top load
		if self._display_load :
			geom = Polyline([Vector3(self.top_line[pid],0.) for pid in self.cfg.top_points])
			self.add(Shape(geom,Material( (70,70,70) )))
			left_corner = Vector3(self.top_line[self.cfg.top_points[0]],0.)
			geom = Polyline([left_corner,left_corner+(0,2,0)])
			self.add(Shape(geom,Material( (70,70,70) )))
			geom = Polyline([Vector3(self.top_line[pid] + Vector2(0,self.load(pid)),0.1) for pid in self.cfg.top_points])
			self.add(Shape(geom,Material( (0,100,100) )))
		#plot info
		if not all(rec.color is None for rec in self.records.itervalues()) :
			clf()
			for name,record in self.records.iteritems() :
				if record.color is not None :
					plot(self.times,[val*record.scale for val in record],color=record.color,label=name)
			ylim(0.,2.)
			legend()
			show()
	#############################################
	#
	#		interaction
	#
	#############################################
	def display_pid (self, display) :
		if display != self._display_pid :
			self._display_pid = display
			self.redraw()
			self.emit(SIGNAL("display_pid"),display)
	
	def display_fixed (self, display) :
		if display != self._display_fixed :
			self._display_fixed = display
			self.redraw()
			self.emit(SIGNAL("display_fixed"),display)
	
	def display_top (self, display) :
		if display != self._display_top :
			self._display_top = display
			self.redraw()
			self.emit(SIGNAL("display_top"),display)
	
	def display_load (self, display) :
		if display != self._display_load :
			self._display_load = display
			self.redraw()
			self.emit(SIGNAL("display_load"),display)
	
	def display_record (self, name, color) :
		if self.records[name].color != color :
			self.records[name].color = color
			self.redraw()
			self.emit(SIGNAL("display_record"),name,display)
	
	def scale_record (self, name, scale) :
		if self.records[name].scale != scale :
			self.records[name].scale = scale
			self.redraw()
			self.emit(SIGNAL("scale_record"),name,scale)




