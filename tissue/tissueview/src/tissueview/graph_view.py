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
This module defines functions to display a property on a graph
"""

__license__= "Cecill-C"
__revision__=" $Id: $ "

from PyQt4.QtCore import Qt,SIGNAL
from vplants.plantgl.algo import GLRenderer
from vplants.plantgl.scenegraph import Material
from openalea.pglviewer import SceneView
from graph_display import draw_graph

default_mat = Material()
default_mat.transparency = 0.5

class GraphView (SceneView) :
	"""View on a graph
	"""
	def __init__ (self, graph, pos, elm_type, scaling, cmap) :
		SceneView.__init__(self)
		self.idmode = SceneView.IDMODE.SHAPE
		self.set_alpha_threshold(0.1)
		
		self.set_name("graph")
		
		self._graph = graph
		self._pos = pos
		self._elm_type = elm_type
		self._scaling = scaling
		self._cmap = cmap
	
	def redraw (self, send_signal = True) :
		sc = draw_graph(self._graph,
		               self._pos,
		               self._elm_type,
		               self._scaling,
		               self._cmap)
		self.clear(False)
		self.merge(sc,send_signal)


