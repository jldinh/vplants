# -*- python -*-
#
#       simulation.diffusion reaction: example simulation package to perform
#										integration of differential equations
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

from openalea.plantgl.scenegraph import Material,Shape,Translated
from openalea.plantgl.ext.color import JetMap
from openalea.pglviewer.data import SceneView
from openalea.tissueshape import edge_geom,face_geom_2D

class SimuView (SceneView) :
	"""
	display the content of a simulation
	"""
	def __init__ (self, global_vars) :
		SceneView.__init__(self)
		self.__dict__.update(global_vars) #allow an easy access to all variables defined in simu.py
		self.redraw()
	
	def redraw (self) :
		"""
		redraw the tissue
		"""
		self.clear()
		#draw cell content
		cmap = JetMap(0.,1.,outside_values = True)
		for cid,conc in self.IAA.iteritems() :
			geom = face_geom_2D(self.mesh,self.pos,cid)
			col = cmap(conc).i3tuple()
			self.add(Shape(geom,Material(col)))
		
