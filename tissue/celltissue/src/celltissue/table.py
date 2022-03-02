# -*- python -*-
#
#       celltissue: view a property as a table of values
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
This module defines a function to store a property as a table
"""

__license__= "Cecill-C"
__revision__=" $Id: $ "

class TableFile (object) :
	"""Object used to serialize a property as a table
	"""
	def __init__ (self, filename, mode, dformat, separator) :
		"""Constructor
		
		:Parameters:
		 - `filename` (str) - name of the file in which to store or read
		                      informations
		 - `mode` (str) - either 'r' to read or 'w' to write.
		 - `dformat` (str) - a string description used to format data values
		                     e.g. '%d' for int, '%f' for float, ...
		 - `separator` (str) - a character used to separate values
		                     e.g. ' ', '\t', ';', ','
		
		.. note:: Do not create this object directly, use :func:`open_table`
		          instead.
		"""
		self._filename = filename
		self._mode = mode
		self._data_format = dformat
		self._separator = separator
		self._keys = None
		
		if mode == 'a' :
			f = open(filename,'r')
			#data format
			line = f.readline().strip()
			assert line.startswith("#DFORMAT:")
			self._data_format = line.split(":")[1].strip()
			
			#separator
			line = f.readline().strip()
			assert line.startswith("#SEPARATOR:")
			self._separator = line.split("'")[1]
			
			#skip comments
			while line.startswith("#") :
				line = f.readline()
			
			while len(line) > 0 and len(line.strip() ) == 0 :
				line = f.readline()
			
			#headers
			if len(line) > 0 :
				self._keys = [int(v) \
				              for v in line.split(self._separator)[1:] ]
			
			f.close()
		
		self._stream = open(filename,mode)
		
		if mode == 'w' :
			#write data format
			self._stream.write("#DFORMAT: %s\n" % self._data_format)
			
			#write separator character
			self._stream.write("#SEPARATOR: '%s'\n" % self._separator)
	
	def write (self, step, prop) :
		"""Append a given property as a new line in the table
		
		.. warning:: keys of the property must stay unchanged between two calls
		             to this function.
		
		:Parameters:
		 - `step` (int) - current step
		 - `prop` (dict of (int|any) ) - the new value of the property for this
		                                 step
		"""
		f = self._stream
		dformat = self._data_format
		sep = self._separator
		
		if self._keys is None :
			#create list of keys
			self._keys = list(prop.iterkeys() )
			self._keys.sort()
			
			#write headers
			f.write("step")
			for elmid in self._keys :
				f.write("%s%d" % (sep,elmid) )
			f.write("\n")
		
		#write step
		f.write("%d" % step)
		
		#write values
		for elmid in self._keys :
			f.write(sep + dformat % prop[elmid])
		f.write("\n")
	
	def close (self) :
		"""Close stream
		"""
		self._stream.close()

def open_table (filename, mode = 'r', dformat = "%f", separator = "\t") :
	"""Open a stream to read or write tables of values
	
	:Parameters:
	 - `filename` (str) - name of the file in which to store or read
	                      informations
	 - `mode` (str) - either 'r' to read, 'w' to write or 'a' to append
	 - `dformat` (str) - a string description used to format data values
	                     e.g. '%d' for int, '%f' for float, ...
	 - `separator` (str) - a character used to separate values
	                     e.g. ' ', '\t', ';', ','
	
	:Returns: a stream to read or write into
	
	:Returns Type: `TableFile`
	"""
	return TableFile(filename,mode,dformat,separator)
















