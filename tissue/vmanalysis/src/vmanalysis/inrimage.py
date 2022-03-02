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

from numpy import append,zeros
from serial.inrimage import read_inrimage,write_inrimage

class InrImage (object) :
	"""Container for 3D images
	
	associate a header with a numpy matrix for voxels
	"""
	def __init__ (self, header = {}, data = None) :
		""""Constructor
		
		:Parameters:
		 - `header` (dict of str|str) - meta info
		    associated with image
		 - `data` (array) - value of each voxel
		"""
		self._header = header
		self._data = data
	
	##################################################
	#
	#		accessors
	#
	##################################################
	def header (self) :
		"""Retrieve meta informations associated with image
		
		:Returns Type: dict of (str|str)
		"""
		return self._header
	
	def set_header (self, header) :
		"""Associate new meta infos with this image
		
		:Parameters:
		 - `header` (dict of (str|str) )
		"""
		self._header = header
	
	def data (self) :
		"""Retrieve data, value of each voxel
		
		:Returns Type: array
		"""
		return self._data
	
	def set_data (self, data) :
		"""Associate new pixel values with this image
		
		:Parameters:
		 - `data` (array)
		"""
		self._data = data
		for i,name in enumerate( ("XDIM","YDIM","ZDIM") ) :
			if name in self._header :
				self._header[name] = data.shape[i]
	
	##################################################
	#
	#		inout
	#
	##################################################
	def read (self, filename) :
		"""Read inrimage from a file
		
		:Parameters:
		 - `filename` (str) - name of the file in which info is stored
		"""
		self._data,self._header = read_inrimage(filename)
	
	def write (self, filename) :
		"""Write inrimage into a file
		
		:Parameters:
		 - `filename` (str) - name of the file in which info will be stored
		"""
		write_inrimage(self._data,self._header,filename)
	
	##################################################
	#
	#		algos
	#
	##################################################
	def crop (self, imin, imax, jmin, jmax, kmin, kmax) :
		"""Crop image in place
		"""
		self._data = self._data[imin:imax,jmin:jmax,kmin:kmax]
	
	def rectify (self) :
		"""Ensure that dimensions of the image are multiple of 4
		"""
		shp = self._data.shape
		for i in xrange(3) :
			if shp[i] % 4 != 0 :
				subshp = list(shp)
				subshp[i] = 4 - (shp[i] % 4)
				self._data = append(self._data,
				                    zeros(subshp,self._data.dtype),
				                    i)
	
	def resize (self, scaling) :
		"""Resize image in place
		
		:Parameters:
		 - `scaling` (float) - scaling factor
		     new_size = old_size * scaling
		"""
		#data
		#TODO
		scaling = 0.5
		self._data = self._data[::2,::2,::2]
		
		#header
		h = self._header
		for name in ("VX","VY","VZ") :
			try :
				h[name] = "%f" % (float(h[name]) / scaling)
			except KeyError :
				pass














