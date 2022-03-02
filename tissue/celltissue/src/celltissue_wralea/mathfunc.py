# -*- python -*-
#
#       celltissue: main tissue object and functions to use it
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
mathematical node definition for celltissue package
"""

__license__= "Cecill-C"
__revision__=" $Id: $ "

from random import uniform
from openalea.core import ScriptLibrary

def random_uniform_func (vmin, vmax) :
	def func () :
		return uniform(vmin,vmax)
	
	return func,

def random_uniform_func_script (inputs, outputs) :
	lib = ScriptLibrary()
	vmin,vmax = inputs
	func, = outputs
	lib.register(func,"func")
	
	script = "def func () :\n\treturn uniform(%f,%f)\n" % (vmin,vmax)
	
	return script

