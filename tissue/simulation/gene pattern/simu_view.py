# -*- python -*-
#
#       simulation.gene pattern: example simulation package to display a gene expression pattern
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
from openalea.pglviewer.data import SceneView
from openalea.tissueshape import edge_geom,face_geom_2D

class SimuView (SceneView) :
	"""
	display the content of a simulation
	"""
	def __init__ (self, mesh, pos, pattern) :
		SceneView.__init__(self)
		#draw walls
		wall_mat = Material( (0,0,0) )
		for eid in mesh.wisps(1) :
			geom = edge_geom(mesh,pos,eid)
			self.add(Shape(Translated( (0,0,0.01),geom),wall_mat))
		#draw activated cells
		gene_mat = Material( (0,100,0) )
		for cid in pattern :
			geom = face_geom_2D(mesh,pos,cid)
			self.add(Shape(geom,gene_mat))

