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
file handling node definition for celltissue package
"""

__license__= "Cecill-C"
__revision__=" $Id: $ "

from os import mkdir
from os.path import exists,dirname,basename
from openalea.celltissue import open_table

def create_tree (dirpath) :
	if dirname(dirpath) not in ("",".","/") :
		create_tree(dirname(dirpath) )
	if not exists(dirpath) :
		mkdir(dirpath)

class FileNameIterator (object) :
	"""Construct a list of filenames
	base on a template.
	
	This object ensure that any directory
	involved in the template is created.
	"""
	def __init__ (self, template, ini_index) :
		"""Construct the iterator from a template
		and an initial index.
		"""
		self._template = template
		self._index = ini_index
		
		#test directories
		tpl_dir = dirname(template)
		if tpl_dir not in ("",".","/") and not exists(tpl_dir) :
			create_tree(tpl_dir)
	
	def __call__ (self) :
		"""Return a new valid filename.
		"""
		filename = self._template % self._index
		self._index += 1
		return filename

def create_name_iterator (template, ini_index) :
	"""Create an iterator on filenames.
	"""
	return FileNameIterator(template,ini_index),

def create_name_iterator_script (inptus, outputs) :
	return "assert False #need to define a filename iterator\n"

def write_table (filename, dformat, sep, step, prop) :
	"""Create a file table stream
	"""
	#test directories
	outdir = dirname(filename)
	if outdir not in ("",".","/") and not exists(outdir) :
		create_tree(outdir)
	
	#open stream
	if exists(filename) :
		f = open_table(filename,'a')
	else :
		f = open_table(filename,'w',dformat,sep)
	
	#write
	f.write(step,prop)
	f.close()
	
	return prop,
