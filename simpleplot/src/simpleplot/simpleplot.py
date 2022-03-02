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
This module defines a simple ploter for sequences
"""

__license__= "Cecill-C"
__revision__=" $Id: simpleplot.py 7887 2010-02-09 07:49:59Z cokelaer $ "

from math import floor,ceil
from PyQt4.QtCore import SIGNAL
from PyQt4.QtGui import QGraphicsScene,QPen,QColor,\
                        QPainterPath

class SimplePlot (QGraphicsScene) :
	
	def __init__ (self, seq, width = 400, height = 300, parent = None) :
		QGraphicsScene.__init__(self,0,0,width,height,parent)
		self._seq = seq
		
		self._xmin = None
		self._xmax = None
		self._ymin = None
		self._ymax = None
		
		self._xres = 1.
		self._yres = 1.
		#connect to seq signals
		self.connect(seq,SIGNAL("add"),self.point_added)
		self.connect(seq,SIGNAL("extend"),self.seq_extended)
		
		#redraw
		if seq.nb_points() > 0 :
			self.redraw()
	
	##############################################
	#
	#	change of coordinates
	#
	##############################################
	def set_xscale (self, xmin, xmax) :
		"""Set policy for x axis.
		
		If xmin (or xmax) is None, set automatic scale
		for xmin (or xmax)
		"""
		self._xmin = xmin
		self._xmax = xmax
	
	def set_yscale (self, ymin, ymax) :
		"""Set policy for y axis.
		
		If ymin (or ymax) is None, set automatic scale
		for ymin (or ymax)
		"""
		self._ymin = ymin
		self._ymax = ymax
	
	def plot_coordinates (self, x, y, frame) :
		"""Compute plot coordinates.
		"""
		xmin,xmax,ymin,ymax = frame
		px = (x - xmin) / (xmax - xmin) * self.width()
		py = self.height() - (y - ymin) / (ymax - ymin) * self.height()
		return px,py
	
	def set_xres (self, res) :
		"""Set resolution along x.
		"""
		self._xres = res
	
	def set_yres (self, res) :
		"""Set resolution along y.
		"""
		self._yres = res
	
	##############################################
	#
	#	sequence edited
	#
	##############################################
	def point_added (self, pt) :
		self.redraw()
		self.update(0,0,self.width(),self.height() )
	
	def seq_extended (self, pt) :
		self.redraw()
		self.update(0,0,self.width(),self.height() )
	
	##############################################
	#
	#	redraw
	#
	##############################################
	def get_frame (self) :
		"""Compute aproximating frame.
		"""
		seq = self._seq
		#defines frame
		xres = self._xres
		yres = self._yres
		if self._xmin is None :
			xmin = floor(seq.xmin() / xres) * xres
		else :
			xmin = self._xmin
		if self._xmax is None :
			xmax = ceil(seq.xmax() / xres) * xres
		else :
			xmax = self._xmax
		if self._ymin is None :
			ymin = floor(seq.ymin() / yres) * yres
		else :
			ymin = self._ymin
		if self._ymax is None :
			ymax = ceil(seq.ymax() / yres) * yres
		else :
			ymax = self._ymax
		#return
		if (xmax - xmin) < xres :
			xmax = xmin + xres
		if (ymax - ymin) < yres :
			ymax = ymin + yres
		return (xmin,xmax,ymin,ymax)
	
	def redraw (self) :
		"""Redraw the curve.
		"""
		seq = self._seq
		#clear
		for item in self.items() :
			self.removeItem(item)
		#defines frame
		frame = self.get_frame()
		#plot points
		if seq.nb_points() > 0 :
			pth = QPainterPath()
			iterpts = seq.iterpoints()
			x,y = iterpts.next()
			pts = self.plot_coordinates(x,y,frame)
			pth.moveTo(*pts )
			for x,y in iterpts :
				pth.lineTo(*self.plot_coordinates(x,y,frame) )
			
			pen = QPen(QColor(0,0,255) )
			pen.setWidth(3)
			
			item = self.addPath(pth,pen)

		
