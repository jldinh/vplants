# -*- python -*-
#
#       tissueview: functions to display a tissue
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
"""
node definition for tissueview package
"""

__license__= "Cecill-C"
__revision__=" $Id: $ "

from openalea.core import ScriptLibrary
from vplants.plantgl.scenegraph import Material
from vplants.plantgl.algo import GLRenderer
from openalea.pglviewer import SceneView
from openalea.tissueview import draw_mesh

def select_mesh (mesh, pos, deg) :
	"""Display elements of a mesh for selection.
	
	mesh: an instance of topomesh
	pos: a dict of (pid,Vec)
	deg: degree of elements to display
	return a drawing function
	"""
	sc = SceneView()
	sc.idmode = GLRenderer.ShapeId
	
	sc.merge(draw_mesh(mesh,
	                   pos,
	                   deg,
	                   Material( (0,0,0) ),
	                   0) )
	
	#return
	return sc.selection_draw

def select_mesh_script (inputs, outputs) :
	lib = ScriptLibrary()
	mesh,pos,deg = inputs
	mesh,script = lib.name(mesh,"")
	pos,script = lib.name(pos,script)
	func, = outputs
	func = lib.register(func,"func")
	
	script += "from vplants.plantgl.scenegraph import Material\n"
	script += "from vplants.plantgl.algo import GLRenderer\n"
	script += "from openalea.pglviewer import SceneView\n"
	script += "from openalea.tissueview import draw_mesh\n"
	script += "sc = SceneView()\n"
	script += "sc.idmode = GLRenderer.SelectionId.ShapeId\n"
	script += "sc.merge(draw_mesh(%s,%s,%d,Material( (0,0,0) ),0) )\n" % (mesh,pos,deg)
	script += "%s = sc.selection_draw\n" % func
	
	return script

