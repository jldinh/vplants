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
special function to remotely access tissue files in the database
"""

__license__= "Cecill-C"
__revision__=" $Id: $ "

from openalea import celltissue
from database import get_filename

def topen (filename, mode = 'r') :
	"""
	replace the original topen
	and look into the database if the file is not found in
	the current directory
	"""
	if mode == 'w' :
		return celltissue.topen(filename,mode)
	else :
		try :
			return celltissue.topen(filename,mode)
		except IOError :
			if mode == 'a' :
				#test wether this particular file is a clone
				#else :
				#	raise UserWarning("make a clone of the file first")
				print mode
			try :
				return celltissue.topen(get_filename(filename),mode)
			except IOError :
				raise IOError("cannot find this particular file even in the database")

