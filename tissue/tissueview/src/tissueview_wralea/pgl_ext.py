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
nodes for plantgl
"""

__license__= "Cecill-C"
__revision__=" $Id: $ "

from openalea.core import ScriptLibrary

def clear_sc (sc, send_signal) :
	sc.clear(send_signal)
	return sc,

def clear_sc_script (inputs, outputs) :
	lib = ScriptLibrary()
	sc, = inputs
	sc,script = lib.name(sc,"")
	
	script += "%s.clear()\n" % sc
	
	return script

