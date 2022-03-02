# -*- python -*-
#
#       simpleplot: a simple widget to plot sequences
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
This module defines the main Sequence object
"""

__license__= "Cecill-C"
__revision__=" $Id: sequence.py 7887 2010-02-09 07:49:59Z cokelaer $ "

from itertools import izip
from PyQt4.QtCore import QObject,SIGNAL

class Sequence (QObject) :
	"""A sequence of X and Y values.
	"""
	
	def __init__ (self, xname, yname, xunit, yunit) :
		"""Initialise the sequence.
		"""
		QObject.__init__(self)
		self.setObjectName("seq(%s,%s)" % (xname,yname) )
		
		self._xvals = []
		self._yvals = []
		
		self._xname = xname
		self._yname = yname
		self._xunit = xunit
		self._yunit = yunit
		
		self._xmin = float('inf')
		self._xmax = float('-inf')
		self._ymin = float('inf')
		self._ymax = float('-inf')
	
	##########################################################
	#
	#		accessors
	#
	##########################################################
	def xname (self) :
		"""Name of x sequence.
		"""
		return self._xname
	
	def yname (self) :
		"""Name of y sequence.
		"""
		return self._yname
	
	def xunit (self) :
		"""Unit of x sequence.
		"""
		return self._xunit
	
	def yunit (self) :
		"""Unit of y sequence.
		"""
		return self._yunit
	
	def xmin (self) :
		"""Minimum value of x sequence.
		"""
		return self._xmin
	
	def xmax (self) :
		"""Maximum value of x sequence.
		"""
		return self._xmax
	
	def xrange (self) :
		"""Return tuple (xmin,xmax).
		"""
		return (self._xmin,self._xmax)
	
	def ymin (self) :
		"""Minimum value of y sequence.
		"""
		return self._ymin
	
	def ymax (self) :
		"""Maximum value of y sequence.
		"""
		return self._ymax
	
	def yrange (self) :
		"""Return tuple (ymin,ymax).
		"""
		return (self._ymin,self._ymax)
	
	def nb_points (self) :
		"""Number of values in the sequence.
		"""
		return len(self._xvals)
	
	def iterx (self) :
		"""Iterator on x values.
		"""
		return iter(self._xvals)
	
	def itery (self) :
		"""Iterator on y values.
		"""
		return iter(self._yvals)
	
	def iterpoints (self) :
		"""Iterator on (x,y).
		"""
		return izip(self._xvals,self._yvals)
	
	##########################################################
	#
	#		add values
	#
	##########################################################
	def add (self, xval, yval) :
		"""Add a new value in the sequence.
		"""
		self._xvals.append(xval)
		self._xmin = min(self._xmin,xval)
		self._xmax = max(self._xmax,xval)
		self._yvals.append(yval)
		self._ymin = min(self._ymin,yval)
		self._ymax = max(self._ymax,yval)
		self.emit(SIGNAL("add"),(xval,yval) )
	
	def extend (self, xvals, yvals) :
		"""Add points in the sequence.
		"""
		assert len(xvals) == len(yvals)
		self._xvals.extend(xvals)
		self._xmin = min(self._xmin,min(xvals) )
		self._xmax = max(self._xmax,max(xvals) )
		self._yvals.extend(yvals)
		self._ymin = min(self._ymin,min(yvals) )
		self._ymax = max(self._ymax,max(yvals) )
		self.emit(SIGNAL("extend"),(xvals,yvals) )


