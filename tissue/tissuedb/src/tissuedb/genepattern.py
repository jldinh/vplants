# -*- python -*-
#
#       tissuedb: package to manage database of scripted files
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
special function to remotely access genepatterns definition in the database
"""

__license__= "Cecill-C"
__revision__=" $Id: $ "

from database import get_zone_filename,get_pattern_filename

def get_zone (name) :
	"""
	retrieve zone definition from the database
	"""
	d = {}
	execfile(get_zone_filename("%s.py" % name),d,d)
	return d['zone']

def get_pattern (name) :
	"""
	retrieve pattern definition from the database
	"""
	d = {}
	execfile(get_pattern_filename("%s.py" % name),d,d)
	return d['expression']

