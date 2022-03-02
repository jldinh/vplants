# -*- python -*-
#
#       simulation.global growth: example simulation package of global growth field
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
__revision__=" $Id: simu_view.py 7897 2010-02-09 09:06:21Z cokelaer $ "

from PyQt4.QtCore import SIGNAL
from vplants.plantgl.math import Vector3
from vplants.plantgl.scenegraph import Material,Shape,Translated,Text,Font
from vplants.plantgl.ext.color import JetMap
from openalea.pglviewer.data import SceneView
from openalea.tissueshape import centroid,edge_geom,face_geom_2D

class SimuView (SceneView) :
	"""
	display the content of a simulation
	"""
	def __init__ (self, param) :
		SceneView.__init__(self)
		self.param = param
		self._display_pid = False
		self._display_wid = False
		self._display_cid = False
		self._display_age = False
		self._display_morphogen = True
		self._display_wall = True
		#self.redraw()
	
	######################################################
	#
	#	interaction
	#
	######################################################
	def pid_displayed (self) :
		return self._display_pid
	
	def display_pid (self, display) :
		self._display_pid = display
		self.emit(SIGNAL("display_pid"),display)
	
	def wid_displayed (self) :
		return self._display_wid
	
	def display_wid (self, display) :
		self._display_wid = display
		self.emit(SIGNAL("display_wid"),display)
	
	def cid_displayed (self) :
		return self._display_cid
	
	def display_cid (self, display) :
		self._display_cid = display
		self.emit(SIGNAL("display_cid"),display)
	
	def age_displayed (self) :
		return self._display_age
	
	def display_age (self, display) :
		self._display_age = display
		self.emit(SIGNAL("display_age"),display)
	
	def morphogen_displayed (self) :
		return self._display_morphogen
	
	def display_morphogen (self, display) :
		self._display_morphogen = display
		self.emit(SIGNAL("display_morphogen"),display)
	
	def wall_displayed (self) :
		return self._display_wall
	
	def display_wall (self, display) :
		self._display_wall = display
		self.emit(SIGNAL("display_wall"),display)
	######################################################
	#
	#	redraw
	#
	######################################################
	def redraw (self) :
		"""
		redraw the tissue
		"""
		self.clear()
		#local
		mesh = self.param.mesh
		pos = self.param.pos
		#draw walls
		if self._display_wall :
			mat = Material( (0,0,0) )
			for wid in mesh.wisps(1) :
				geom = Translated( (0,0,0.1),edge_geom(mesh,pos,wid))
				self.add(Shape(geom,mat))
		#draw cell morphogen concentration
		if self._display_morphogen :
			cmap = JetMap(0.,1.,outside_values = True)
			for cid,conc in self.param.morphogen.iteritems() :
				geom = face_geom_2D(mesh,pos,cid)
				col = cmap(conc).i3tuple()
				self.add(Shape(geom,Material(col)))
		#draw cell age
		if self._display_age :
			cmap = JetMap(0.,5.,outside_values = True)
			for cid,age in self.param.cell_age.iteritems() :
				geom = face_geom_2D(mesh,pos,cid)
				col = cmap(age).i3tuple()
				self.add(Shape(geom,Material(col)))
		#draw cell id
		if self._display_cid :
			cid_mat = Material( (0,0,0) )
			font = Font("ariana",8)
			for cid in mesh.wisps(2) :
				geom = Text("%d" % cid,Vector3(centroid(mesh,pos,2,cid),0.1),False,font)
				self.add(Shape(geom,cid_mat))
		#draw wall id
		if self._display_wid :
			wid_mat = Material( (0,0,0) )
			font = Font("ariana",8)
			for wid in mesh.wisps(1) :
				geom = Text("%d" % wid,Vector3(centroid(mesh,pos,1,wid),0.1),False,font)
				self.add(Shape(geom,wid_mat))
		#draw point id
		if self._display_pid :
			pid_mat = Material( (0,0,0) )
			font = Font("ariana",8)
			for pid in mesh.wisps(0) :
				geom = Text("%d" % pid,Vector3(pos[pid],0.1),False,font)
				self.add(Shape(geom,pid_mat))

