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
from openalea.tissueview import MeshView,MeshView2D,MeshView1D

def mesh_view (mesh, pos, deg, shrink, cmap) :
	sc = MeshView(mesh,pos,deg,shrink,cmap)
	sc.redraw()
	
	return sc,sc.redraw,sc.selection_draw

def mesh_view_script (inputs, outputs) :
	lib = ScriptLibrary()
	mesh,pos,deg,shrink,cmap = inputs
	mesh,script = lib.name(mesh,"")
	pos,script = lib.name(pos,script)
	cmap,script = lib.name(cmap,script)
	
	sc,redraw,select = outputs
	sc = lib.register(sc,"sc")
	redraw = lib.register(redraw,"redraw")
	select = lib.register(select,"select")
	
	script += "from openalea.tissueview import MeshView\n\n"
	script += "sc = MeshView(%s,%s,%d,%d,%s)\n" % (mesh,
	                                               pos,
	                                               deg,
	                                               shrink,
	                                               cmap)
	script += "sc.redraw()\n"
	script += "%s = sc.redraw\n" % redraw
	script += "%s = sc.selection_draw\n" % select
	
	return script

def mesh_view2D (mesh, pos, deg, shrink, cmap, offset) :
	sc = MeshView2D(mesh,pos,deg,shrink,cmap,offset)
	sc.redraw()
	
	return sc,sc.redraw,sc.selection_draw

def mesh_view2D_script (inputs, outputs) :
	lib = ScriptLibrary()
	mesh,pos,deg,shrink,cmap,offset = inputs
	mesh,script = lib.name(mesh,"")
	pos,script = lib.name(pos,script)
	cmap,script = lib.name(cmap,script)
	
	sc,redraw,select = outputs
	sc = lib.register(sc,"sc")
	redraw = lib.register(redraw,"redraw")
	select = lib.register(select,"select")
	
	script += "from openalea.tissueview import MeshView2D\n\n"
	script += "sc = MeshView2D(%s,%s,%d,%d,%s,%d)\n" % (mesh,
	                                                    pos,
	                                                    deg,
	                                                    shrink,
	                                                    cmap,
	                                                    offset)
	script += "sc.redraw()\n"
	script += "%s = sc.redraw\n" % redraw
	script += "%s = sc.selection_draw\n" % select
	
	return script

def mesh_view1D (mesh, pos, width, cmap, shrink) :
	sc = MeshView1D(mesh,pos,width,cmap,shrink)
	sc.redraw()
	
	return sc,sc.redraw,sc.selection_draw

def mesh_view1D_script (inputs, outputs) :
	lib = ScriptLibrary()
	mesh,pos,width,cmap,shrink = inputs
	mesh,script = lib.name(mesh,"")
	pos,script = lib.name(pos,script)
	cmap,script = lib.name(cmap,script)
	
	sc,redraw,select = outputs
	sc = lib.register(sc,"sc")
	redraw = lib.register(redraw,"redraw")
	select = lib.register(select,"select")
	
	script += "from openalea.tissueview import MeshView1D\n\n"
	script += "sc = MeshView1D(%s,%s,%f,%s,%d)\n" % (mesh,
	                                                 pos,
	                                                 width,
	                                                 cmap,
	                                                 shrink)
	script += "sc.redraw()\n"
	script += "%s = sc.redraw\n" % redraw
	script += "%s = sc.selection_draw\n" % select
	
	return script


