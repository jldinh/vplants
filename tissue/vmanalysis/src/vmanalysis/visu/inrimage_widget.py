from numpy import array,uint32
from PyQt4.QtCore import SIGNAL
from PyQt4.QtGui import QLabel,QColor

def compute_palette (palname, cmax) :
	if palname == "grayscale" :
		pal = [QColor(i * 255. / cmax,
		              i * 255. / cmax,
		              i * 255. / cmax).rgb() for i in xrange(cmax + 1)]
	elif palname == "rainbow" :
		pal = [QColor.fromHsv(i * 359. / cmax,
		                      255,
		                      255).rgb() for i in xrange(cmax + 1)]
	elif palname == "bwrainbow" :
		pal = [QColor(255,255,255).rgb(),
		       QColor(0,0,0).rgb()] \
		    + [QColor.fromHsv(int(i * 359. / (cmax - 2.) ),
		                      255,
		                      255).rgb() for i in xrange(cmax - 1)]
	else :
		raise UserWarning("undefined palette : %s" % palname)
	
	return array(pal,uint32)

class InrImageWidget (QLabel) :
	"""Display an InrImage in a scalable label
	"""
	def __init__ (self, parent = None) :
		QLabel.__init__(self,parent)
		
		self._img = None
		self._pal = None
		self._ratio = 1.
		
		self.setScaledContents(True)
		self.setMouseTracking(True)
	
	def resizeEvent (self, event) :
		if event.oldSize() != event.size() :
			w = event.size().width()
			h = event.size().height()
			if int(w * self._ratio) <= h :
				self.resize(w,w * self._ratio)
			else :
				self.resize(h / self._ratio,h)
	
	def mousePressEvent (self, event) :
		x = event.x()
		y = event.y()
                pix,intens = self.pixmap_coordinates(x,y)
		self.emit(SIGNAL("mouse_press"),pix,intens)
	
	def mouseMoveEvent (self, event) :
		x = event.x()
		y = event.y()
                pix,intens = self.pixmap_coordinates(x,y)
		self.emit(SIGNAL("mouse_move"),pix,intens)
	
	########################################
	#
	#	accessors
	#
	########################################
	def palette (self) :
		"""Palette used
		
		:Returns Type: array of uint32
		"""
		return self._pal
	
	def set_palette (self, palette) :
		"""Set the palette
		
		.. warning:: will cast color value to uint32
		
		:Parameters:
		 - `palette` (list of int)
		"""
		self._pal = array(palette,uint32)
	
	def image (self) :
		"""Get currently displayed image
		
		:Returns Type: `InrImage`
		"""
		return self._img
	
	def set_image (self, im) :
		"""Set an image to display
		
		:Parameters:
		 - `im` (InrImage)
		"""
		self._img = im
		
		#header
		h = im.header()
		try :
			VX = float(h["VX"])
			VY = float(h["VY"])
			if VX == 0 or VY == 0 :
				VX = 1.
				VY = 1.
		except KeyError :
			VX = 1.
			VY = 1.
		except ValueError :
			VX = 1.
			VY = 1.
		
		#ratio
		size = im.data().shape
		self._ratio = (size[1] * VY) / (size[0] * VX)
		
		#signal
		self.emit(SIGNAL("set_image") )
	
	def rotate (self, orient) :
		"""Rotate view 90 degrees
		
		:Parameters:
		 - `orient` (int) - orientation of rotation
		    - if orient == 1, rotation clockwise
		    - if orient == -1, rotation counterclockwise
		"""
		raise NotImplementedError("TO subclass")
	
	#########################################
	#
	#	change of referential
	#
	#########################################
	def pixmap_coordinates (self, x_screen, y_screen) :
		"""Return coordinates of a point in the pixmap
		
		This function returns the coordinate of the point
		corresponding to the index in the array used to store
		the data
		
		.. warning:: These are not the coordinates of the point in the real
		             space. One must multiply these coordinates by VX, VY and VZ
		             contained in the header of inrimage to access the real
		             coordinates in the real world.
		
		:Parameters:
		 - `x_screen` (int) - x coordinate of the point
		 - `y_screen` (int) - y coordinate of the point
		
		:Returns Type: int,int,int
		"""
		raise NotImplementedError("TO subclass")

