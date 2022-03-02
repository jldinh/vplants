from PyQt4.QtCore import QRectF
from PyQt4.QtGui import QImage,QPixmap
import OpenGL.GL as ogl
from openalea.pglviewer import ElmView,Vec
from openalea.pglviewer.constants import DRAW_MODE

class StackView( ElmView) :
	"""View an InrImage as a stack of slides
	"""
	
	def __init__ (self, image, palette, alpha_threshold = 0.1) :
		"""Constructor
		
		:Parameters:
		 - `image` (InrImage)
		 - `palette` (array of int) - an rgba color for each different value
		    of the voxels in image
		"""
		ElmView.__init__(self,"stack")
		self.use_alpha(True)
		self.set_alpha_threshold(alpha_threshold)
		
		self._image = image
		self._palette = palette
		
		#dimensions
		h = image.header()
		self._vx = float(h["VX"])
		self._vy = float(h["VY"])
		self._vz = float(h["VZ"])
		
		#create image list
		data = image.data()
		imax,jmax,kmax = data.shape
		
		imgs = []
		for z in xrange(kmax) :
			dat = palette[data[:,:,z] ].flatten('F')
			img = QImage(dat,imax,jmax,QImage.Format_ARGB32)
			imgs.append(QPixmap.fromImage(img) )
		
		self._images = imgs
		self._images.reverse()
		
		self._tex_inds = None
	
	############################################
	#
	#	display
	#
	############################################
	def draw (self, view, mode) :
		vx = self._vx
		vy = self._vy
		vz = self._vz
		
		if mode == DRAW_MODE.DRAFT :
			ogl.glPushAttrib(ogl.GL_LIGHTING_BIT)
			ogl.glDisable(ogl.GL_LIGHTING)
			ogl.glColor3f(0.8,0.8,0.8)
			
			for k,img in enumerate(self._images) :
				xmax = img.width() * vx / 2.
				ymax = img.height() * vy / 2.
				z = k * vz
				ogl.glBegin(ogl.GL_LINE_LOOP)
				ogl.glVertex3f(-xmax,-ymax,z)
				ogl.glVertex3f( xmax,-ymax,z)
				ogl.glVertex3f( xmax, ymax,z)
				ogl.glVertex3f(-xmax, ymax,z)
				ogl.glEnd()
			
			ogl.glPopAttrib()
		elif mode == DRAW_MODE.NORMAL :
			if self._tex_inds is None :
				self._tex_inds = [view.bindTexture(img) \
				                  for img in self._images]
			
			tex = self._tex_inds
			rect = QRectF(0.,0.,1.,1.)
			for k,img in enumerate(self._images) :
				xmax = img.width() * vx
				ymax = img.height() * vy
				z = k * vz
				ogl.glPushMatrix()
				ogl.glMultMatrixd( (xmax,0.,0.,0.,
				                    0.,ymax,0.,0.,
				                    0.,0.,1.,0.,
				                    - xmax / 2.,- ymax / 2.,z,1.) )
				view.drawTexture(rect,tex[k])
				ogl.glPopMatrix()
		else :
			print "toto"
	
	#########################################################
	#
	#		geometrical attributes
	#
	#########################################################
	def bounding_box (self) :
		"""Bounding box of the displayed element
		
		:Returns Type: :class:BoundingBox
		"""
		from vplants.plantgl.scenegraph import BoundingBox
		if len(self._images) == 0 :
			return None
		else :
			img = self._images[0]
			xmax = img.width() * self._vx / 2.
			ymax = img.height() * self._vy / 2.
			zmax = len(self._images) * self._vz
			return BoundingBox( (-xmax,-ymax,0),(xmax,ymax,zmax) )
	
	def position (self) :
		"""Position of the displayed element
		
		:Returns Type: Vector
		"""
		return Vec(0,0,0)
	
	def center (self) :
		"""Position of the center of the element
		
		:Returns Type: Vector
		"""
		return Vec(0,0,0)

