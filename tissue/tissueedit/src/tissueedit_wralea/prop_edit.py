# -*- python -*-
#
#       tissueedit: set of GUI to edit a tissue
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
node definition for tissueedit package
"""

__license__= "Cecill-C"
__revision__=" $Id: $ "

from openalea.core import ScriptLibrary
from openalea.tissueedit import ScalarPropEditGUI

def scalar_prop_edit (scalar_prop_view, prop_type, select_func) :
	gui = ScalarPropEditGUI(scalar_prop_view,
	                        eval(prop_type),
	                        select_func)
	
	return gui,

def scalar_prop_edit_script (inputs, outputs) :
	lib = ScriptLibrary()
	scalar_prop_view,prop_type,select_func = inputs
	view,script = lib.name(scalar_prop_view,"")
	func,script = lib.name(select_func,script)
	gui, = outputs
	gui = lib.register(gui,"gui")
	
	script += "from openalea.tissueedit import ScalarPropEditGUI\n"
	script += "%s = ScalarPropEditGUI(%s,%s,%s)\n" % (gui,view,prop_type,func)
	
	return script

