# -*- python -*-
#
#       vmanalysis: 2D view on inrimages
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
"""This module defines adapters to look at inrimages as pixmaps
"""

__license__ = "Cecill-C"
__revision__ = " $Id: $ "

class InrImage2DView (object) :
	"""Provide a 2D pixmap view on any InrImage
	"""
	def __init__ (self, img = None) :
		""""Constructor
		
		:Parameters:
		 - `img` (InrImage) - image to display
		"""
		self._orientation = 0 #rotation of the image
		self.set_image(img)
	
	##################################################
	#
	#		accessors
	#
	##################################################
	def image (self) :
		"""Retrieve image
		
		:Returns Type: InrImage
		"""
		return self._img
	
	def set_image (self, img) :
		"""Specify the image to display
		
		:Parameters:
		 - `img` (InrImage)
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














