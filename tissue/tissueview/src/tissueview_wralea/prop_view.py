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
from openalea.tissueview import ScalarPropView,TensorialPropView

def scalar_prop_view (mesh, pos, deg, prop ,shrink, cmap) :
	sc = ScalarPropView(mesh,pos,deg,prop,shrink,cmap)
	sc.redraw()
	
	return sc,sc.redraw,sc.selection_draw

def scalar_prop_view_script (inputs, outputs) :
	lib = ScriptLibrary()
	mesh,pos,deg,prop,shrink,cmap = inputs
	mesh,script = lib.name(mesh,"")
	pos,script = lib.name(pos,script)
	prop,script = lib.name(prop,script)
	cmap,script = lib.name(cmap,script)
	
	sc,redraw,select = outputs
	sc = lib.register(sc,"sc")
	redraw = lib.register(redraw,"redraw")
	select = lib.register(select,"select")
	
	script += "from openalea.tissueview import ScalarPropView\n\n"
	script += "sc = ScalarPropView(%s,%s,%d,%s,%d,%s)\n" % (mesh,
	                                                        pos,
	                                                        deg,
	                                                        prop,
	                                                        shrink,
	                                                        cmap)
	script += "sc.redraw()\n"
	script += "%s = sc.redraw\n" % redraw
	script += "%s = sc.selection_draw\n" % select
	
	return script

def tensorial_prop_view (mesh, pos, deg, prop , scaling) :
	sc = TensorialPropView(mesh,pos,deg,prop,scaling)
	sc.redraw()
	
	return sc,sc.redraw,sc.selection_draw

def tensorial_prop_view_script (inputs, outputs) :
	lib = ScriptLibrary()
	mesh,pos,deg,prop,scaling = inputs
	mesh,script = lib.name(mesh,"")
	pos,script = lib.name(pos,script)
	prop,script = lib.name(prop,script)
	
	sc,redraw,select = outputs
	sc = lib.register(sc,"sc")
	redraw = lib.register(redraw,"redraw")
	select = lib.register(select,"select")
	
	script += "from openalea.tissueview import TensorialPropView\n\n"
	script += "sc = TensorialPropView(%s,%s,%d,%s,%f)\n" % (mesh,
	                                                        pos,
	                                                        deg,
	                                                        prop,
	                                                        scaling)
	script += "sc.redraw()\n"
	script += "%s = sc.redraw\n" % redraw
	script += "%s = sc.selection_draw\n" % select
	
	return script


