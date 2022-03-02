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
from openalea.tissueview import draw_scalar_prop, \
                                draw_scalar_prop2D, \
                                draw_tensorial_prop

def display_scalar_prop (mesh, pos, deg, prop ,shrink, cmap, sc) :
	sc.merge(draw_scalar_prop(mesh,pos,deg,prop,shrink,cmap) )
	
	return sc,

def display_scalar_prop_script (inputs, outputs) :
	lib = ScriptLibrary()
	mesh,pos,deg,prop,shrink,cmap,sc = inputs
	mesh,script = lib.name(mesh,"")
	pos,script = lib.name(pos,script)
	prop,script = lib.name(prop,script)
	material,script = lib.name(material,script)
	cmap,script = lib.name(cmap,script)
	sc,script = lib.name(sc,script)
	
	script += "from openalea.tissueview import draw_scalar_prop\n"
	script += "%s.merge(draw_scalar_prop(%s,%s,%d,%s,%d,%s) )\n" % (mesh,pos,deg,prop,shrink,cmap)
	
	return script

def display_scalar_prop2D (mesh, pos, deg, prop ,shrink, cmap, offset, sc) :
	sc.merge(draw_scalar_prop2D(mesh,pos,deg,prop,shrink,cmap,offset) )
	
	return sc,

def display_scalar_prop2D_script (inputs, outputs) :
	lib = ScriptLibrary()
	mesh,pos,deg,prop,shrink,cmap,offset,sc = inputs
	mesh,script = lib.name(mesh,"")
	pos,script = lib.name(pos,script)
	prop,script = lib.name(prop,script)
	material,script = lib.name(material,script)
	cmap,script = lib.name(cmap,script)
	sc,script = lib.name(sc,script)
	
	script += "from openalea.tissueview import draw_scalar_prop2D\n"
	script += "%s.merge(draw_scalar_prop2D(%s,%s,%d,%s,%d,%s,%d) )\n" % (mesh,pos,deg,prop,shrink,cmap,offset)
	
	return script

def display_tensorial_prop (mesh, pos, deg, prop, scaling, sc) :
	sc.merge(draw_tensorial_prop(mesh,pos,deg,prop,scaling) )
	
	return sc,

def display_tensorial_prop_script (inputs, outputs) :
	lib = ScriptLibrary()
	mesh,pos,deg,prop,scaling,sc = inputs
	mesh,script = lib.name(mesh,"")
	pos,script = lib.name(pos,script)
	prop,script = lib.name(prop,script)
	sc,script = lib.name(sc,script)
	
	script += "from openalea.tissueview import draw_tensorial_prop\n"
	script += "%s.merge(draw_tensorial_prop(%s,%s,%d,%s,%f) )\n" % (mesh,pos,deg,prop,scaling)
	
	return script


