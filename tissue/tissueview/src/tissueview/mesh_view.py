# -*- python -*-
#
#       tissueview: function used to display tissue properties
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
This module defines functions to display a property on a topomesh
"""

__license__= "Cecill-C"
__revision__=" $Id: $ "

from PyQt4.QtCore import Qt,SIGNAL
from vplants.plantgl.algo import GLRenderer
from vplants.plantgl.scenegraph import Material
from openalea.pglviewer import SceneView
from mesh_display import draw_mesh,draw_mesh2D,draw_mesh1D

default_mat = Material()
default_mat.transparency = 0.5

class MeshView (SceneView) :
	"""View on a mesh.
	"""
	def __init__ (self, mesh, pos, deg, shrink, cmap) :
		SceneView.__init__(self)
		self.idmode = SceneView.IDMODE.SHAPE
		self.set_alpha_threshold(0.1)
		
		self.set_name("mesh")
		
		self._mesh = mesh
		self._pos = pos
		self._deg = deg
		self._shrink = shrink
		self._cmap = cmap
		self._normal_reversed = False
		self._triangulation_method = 'topo'
		self._internal_point = None
	
	def redraw (self, send_signal = True) :
		sc = draw_mesh(self._mesh,
		               self._pos,
		               self._deg,
		               self._cmap,
		               self._shrink,
		               self._normal_reversed,
		               self._triangulation_method,
		               self._internal_point)
		self.clear(False)
		self.merge(sc,send_signal)

class MeshView2D (MeshView) :
	"""View on a mesh.
	"""
	def __init__ (self, mesh, pos, deg, shrink, cmap, offset) :
		MeshView.__init__(self,mesh,pos,deg,shrink,cmap)
		self._offset = offset
		self._triangulation_method = 'topo'
	
	def redraw (self, send_signal = True) :
		sc = draw_mesh2D(self._mesh,
		                 self._pos,
		                 self._deg,
		                 self._cmap,
		                 self._shrink,
		                 self._offset,
		                 self._triangulation_method)
		self.clear(False)
		self.merge(sc,send_signal)

class MeshView1D (SceneView) :
	"""View on a mesh.
	"""
	def __init__ (self, mesh, pos, width, cmap, shrink) :
		SceneView.__init__(self)
		self.idmode = SceneView.IDMODE.SHAPE
		self.set_alpha_threshold(0.1)
		
		self.set_name("mesh")
		
		self._mesh = mesh
		self._pos = pos
		self._width = width
		self._cmap = cmap
		self._shrink = shrink
	
	def redraw (self, send_signal = True) :
		sc = draw_mesh1D(self._mesh,
		                 self._pos,
		                 self._width,
		                 self._cmap,
		                 self._shrink)
		self.clear(False)
		self.merge(sc,send_signal)


