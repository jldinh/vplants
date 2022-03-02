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

from openalea.plantgl.scenegraph import ImageTexture,QuadSet,Shape
from openalea.pglviewer.data import SceneView

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
		mat = ImageTexture("description_files/meduse.png")
		geom = QuadSet( [(-1,-1,0),(1,-1,0),(1,1,0),(-1,1,0)],
						[(0,1,2,3)] )
		geom.texCoordList = [(0,0),(1,0),(1,1),(0,1)]
		shp = Shape(geom,mat)
		self.add(shp)
