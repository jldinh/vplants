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
"""This module defines a set of usefull functions
to deal with tissue simulations.
"""

__license__ = "Cecill-C"
__revision__ = " $Id: $ "

from os.path import exists

__all__ = ["last_index"]

def last_index (pattern, *args) :
	"""Return the last index of a
	set of files that match a pattern
	
	.. warning:: this function assume that if the files are defined
	  they start from 0
	
	:Parameters:
	 - `pattern` (str) - a file pattern e.g. "data/tissue.%.4d.zip"
	 - `args` (tuple) - a list of values if the pattern requiers more than
	                    one argument
	
	:Returns Type: int or None
	"""
	if not exists(pattern % tuple(args + (0,) ) ) :
		return None
	
	ind = 1
	while exists(pattern % tuple(args + (ind,) ) ) :
		ind += 1
	
	return ind - 1
