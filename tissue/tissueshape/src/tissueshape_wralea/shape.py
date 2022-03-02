# -*- python -*-
#
#       tissueshape: tissue geometry and functions to use it
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
node definition for tissueshape package
"""

__license__= "Cecill-C"
__revision__=" $Id: $ "

from openalea.core import ScriptLibrary
from vplants.plantgl.math import Vector2,Vector3
from openalea.tissueshape import tovec as tovec_pgl

def tovec (pos, force_3D) :
	vec_map = tovec_pgl(pos)
	if force_3D :
		vec_map.set_value(dict( (pid,Vector3(vec) ) for pid,vec in vec_map.iteritems() ) )
	
	return vec_map,

def tovec_script (inputs, outputs) :
	lib = ScriptLibrary()
	pos,force_3D = inputs
	pos,script = lib.name(pos,"")
	vec_map, = outputs
	vec_map = lib.register(vec_map,"pos")
	
	script += "from openalea.tissueshape import tovec\n"
	script += "%s = tovec(%s)\n" % (vec_map,pos)
	if force_3D :
		script += "from vplants.plantgl.math import Vector3\n"
		script += "%s.set_value(dict( (pid,Vector3(vec) for pid,vec in %s.iteritems() )\n" % (vec_map,vec_map)
	
	return script
