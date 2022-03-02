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
from openalea.tissueview import draw_mesh, \
                                draw_mesh2D, \
                                draw_mesh1D

def display_mesh (mesh, pos, deg, material, shrink, sc) :
	sc.merge(draw_mesh(mesh,pos,deg,material,shrink) )
	
	return sc,

def display_mesh_script (inputs, outputs) :
	lib = ScriptLibrary()
	mesh,pos,deg,material,shrink,sc = inputs
	mesh,script = lib.name(mesh,"")
	pos,script = lib.name(pos,script)
	material,script = lib.name(material,script)
	sc,script = lib.name(sc,script)
	
	script += "from openalea.tissueview import draw_mesh\n"
	script += "%s.merge(draw_mesh(%s,%s,%d,%s,%d) )\n" % (mesh,pos,deg,material,shrink)
	
	return script

def display_mesh2D (mesh, pos, deg, material ,shrink, offset, sc, clear) :
	lsc = draw_mesh2D(mesh,pos,deg,material,shrink,offset)
	
	if clear :
		sc.clear(False)
	sc.merge(lsc)
	
	return sc,

def display_mesh2D_script (inputs, outputs) :
	lib = ScriptLibrary()
	mesh,pos,deg,material,shrink,offset,sc = inputs
	mesh,script = lib.name(mesh,"")
	pos,script = lib.name(pos,script)
	material,script = lib.name(material,script)
	sc,script = lib.name(sc,script)
	
	script += "from openalea.tissueview import draw_mesh2D\n"
	script += "%s.merge(draw_mesh2D(%s,%s,%d,%s,%d,%d) )\n" % (mesh,pos,deg,material,shrink,offset)
	
	return script

def display_mesh1D (mesh, pos, width, material ,shrink, sc) :
	sc.merge(draw_mesh1D(mesh,pos,width,material,shrink) )
	
	return sc,

def display_mesh1D_script (inputs, outputs) :
	lib = ScriptLibrary()
	mesh,pos,width,material,shrink,sc = inputs
	mesh,script = lib.name(mesh,"")
	pos,script = lib.name(pos,script)
	material,script = lib.name(material,script)
	sc,script = lib.name(sc,script)
	
	script += "from openalea.tissueview import draw_mesh1D\n"
	script += "%s.merge(draw_mesh1D(%s,%s,%f,%s,%d) )\n" % (mesh,pos,width,material,shrink)
	
	return script


