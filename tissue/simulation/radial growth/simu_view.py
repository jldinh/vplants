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
__revision__=" $Id: $ "

from vplants.plantgl.math import Vector3
from vplants.plantgl.scenegraph import Material,Shape,Translated,Text,Font
from vplants.plantgl.ext.color import JetMap
from openalea.pglviewer.data import SceneView
from openalea.tissueshape import centroid,edge_geom,face_geom_2D

class SimuView (SceneView) :
	"""
	display the content of a simulation
	"""
	def __init__ (self, global_vars) :
		SceneView.__init__(self)
		self.__dict__.update(global_vars) #allow an easy access to all variables defined in simu.py
		self._display_pid = False
		self._display_cid = False
		self._display_age = True
		self._display_wall = True
		self.redraw()
	
	def redraw (self) :
		"""
		redraw the tissue
		"""
		self.clear()
		#draw walls
		if self._display_wall :
			mat = Material( (0,0,0) )
			for wid in self.mesh.wisps(1) :
				geom = Translated( (0,0,0.1),edge_geom(self.mesh,self.pos,wid))
				self.add(Shape(geom,mat))
		#draw cell age
		if self._display_age :
			cmap = JetMap(0.,5.,outside_values = True)
			for cid,age in self.cell_age.iteritems() :
				geom = face_geom_2D(self.mesh,self.pos,cid)
				col = cmap(age).i3tuple()
				self.add(Shape(geom,Material(col)))
		#draw cell id
		if self._display_cid :
			cid_mat = Material( (0,0,0) )
			font = Font("ariana",8)
			for cid in self.mesh.wisps(2) :
				geom = Text("%d" % cid,Vector3(centroid(self.mesh,self.pos,cid,2),0.1),False,font)
				self.add(Shape(geom,cid_mat))
		#draw point id
		if self._display_pid :
			pid_mat = Material( (0,255,0) )
			font = Font("ariana",8)
			for pid in self.mesh.wisps(0) :
				geom = Text("%d" % pid,Vector3(self.pos[pid],0.1),False,font)
				self.add(Shape(geom,pid_mat))

