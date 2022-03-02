from PyQt4.QtCore import SIGNAL
from PyQt4.QtGui import QImage,QPixmap,QTransform
from inrimage_widget import InrImageWidget

class InrImageStackWidget (InrImageWidget) :
	"""View on a stack one image at a time
	"""
	def __init__ (self, parent = None) :
		InrImageWidget.__init__(self,parent)
		
		self._pixmaps = []
		self._transform = 0
		self._current_pix = 0
	
	########################################
	#
	#	accessors
	#
	########################################
	def set_image (self, im) :
		"""Set an image to display
		
		:Parameters:
		 - `im` (InrImage)
		"""
		#create images
		pal = self._pal
		data = im.data()
		
		pix = []
		for z in xrange(data.shape[2]) :
			dat = pal[data[:,:,z] ].flatten('F')
			img = QImage(dat,
			             data.shape[0],
			             data.shape[1],
			             QImage.Format_RGB32)
			pix.append(QPixmap.fromImage(img) )
		
		self._pixmaps = pix
		
		#set pixmap
		self.setPixmap(self._pixmaps[self._current_pix])
		
		#call parent function
		InrImageWidget.set_image(self,im)
	
	def rotate (self, orient) :
		"""Rotate view 90 degrees
		
		:Parameters:
		 - `orient` (int) - orientation of rotation
		    - if orient == 1, rotation clockwise
		    - if orient == -1, rotation counterclockwise
		"""
		#rotate pixmaps
		tr = QTransform()
		tr.rotate(orient * 90)
		self._pixmaps = [pix.transformed(tr) for pix in self._pixmaps]
		self._ratio = 1. / self._ratio
		self._transform = (self._transform + orient * 90) % 360
		
		#adjust view
		self.change_pix(self._current_pix)
		self.resize(self.height(),self.width() )
	
	def nb_pix (self) :
		"""Number of pixmaps in the stack
		
		:Returns Type: int
		"""
		return len(self._pixmaps)
	
	def change_pix (self, ind) :
		"""Change current displayed pixmap
		
		:Parameters:
		 - `ind` (int) - index of the pixmap in the data array
		"""
		self._current_pix = ind
		self.setPixmap(self._pixmaps[ind])
		self.setMinimumSize(50,50)
		self.emit(SIGNAL("change_pix"),ind)
	
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
		
		:Returns Type: int,int,int,int
		"""
		w,h,d = self._img.data().shape
		
		if self._transform == 0 :
			x_pix = x_screen * w / self.width()
			y_pix = y_screen * h / self.height()
		elif self._transform == 90 :
			x_pix = y_screen * h / self.height()
			y_pix = (self.width() - x_screen) * w / self.width()
		elif self._transform == 180 :
			x_pix = (self.width() - x_screen) * w / self.width()
			y_pix = (self.height() - y_screen) * h / self.height()
		elif self._transform == 270 :
			x_pix = (self.height() - y_screen) * h / self.height()
			y_pix = x_screen * w / self.width()
		
		if 0 <= x_pix < w and 0 <= y_pix < h :
			intensity = self._img.data()[x_pix,y_pix,self._current_pix]
		else :
			intensity = None
		
		return (x_pix,y_pix,self._current_pix),intensity

