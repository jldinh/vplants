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
from vplants.plantgl.ext.color import IntMap,JetMap,GreenMap

def jet_map (vmin, vmax) :
	cmap = JetMap(vmin,vmax,outside_values = True)
	return cmap,

def jet_map_script (inputs, outputs) :
	lib = ScriptLibrary()
	vmin,vmax = inputs
	cmap, = outputs
	cmap = lib.register(cmap,"cmap")
	
	script = "from vplants.plantgl.ext.color import JetMap\n"
	script += "%s = JetMap(%f,%f,outside_values = True)\n" % (cmap,vmin,vmax)
	
	return script

def green_map (vmin, vmax) :
	cmap = GreenMap(vmin,vmax,outside_values = True)
	return cmap,

def green_map_script (inputs, outputs) :
	lib = ScriptLibrary()
	vmin,vmax = inputs
	cmap, = outputs
	cmap = lib.register(cmap,"cmap")
	
	script = "from vplants.plantgl.ext.color import GreenMap\n"
	script += "%s = GreenMap(%f,%f,outside_values = True)\n" % (cmap,vmin,vmax)
	
	return script

def int_map () :
	cmap = IntMap()
	return cmap,

def int_map_script (inputs, outputs) :
	lib = ScriptLibrary()
	cmap, = outputs
	cmap = lib.register(cmap,"cmap")
	
	script = "from vplants.plantgl.ext.color import IntMap\n"
	script += "%s = IntMap()\n" % cmap
	
	return script

def material_map (prop, cmap) :
	"""assign a single material to every elm in prop.
	"""
	def func (wid) :
		return Material(cmap(prop[wid]).i3tuple() )
	return func,

def material_map_script (inputs, outputs) :
	lib = ScriptLibrary()
	prop,cmap = inputs
	prop,script = lib.name(prop,"")
	cmap,script = lib.name(cmap,script)
	func, = outputs
	func = lib.register(func,"func")
	
	script = "from vplants.plantgl.scenegraph import Material\n"
	script += "def %s (wid) :\n" % func
	script += "	return Material(%s(%s[wid]).i3tuple() )\n" % (cmap,prop)
	script += "\n"
	
	return script


