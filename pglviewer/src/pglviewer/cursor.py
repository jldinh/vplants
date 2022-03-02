import OpenGL.GL as ogl
from PyQGLViewer import Vec
from PyQt4.QtCore import QObject,SIGNAL

class Cursor3D (QObject) :
	"""A cursor in a 3D space.
	"""
	def __init__ (self) :
		QObject.__init__(self)
		self._position = Vec(0,0,0)
	
	def position (self) :
		"""Actual position of the cursor.
		"""
		return self._position
	
	def set_position (self, pos) :
		"""Set the position of the cursor.
		"""
		self._position = Vec(*tuple(pos) )
		self.emit(SIGNAL("set_position"),self._position)
	
	def draw (self, view) :
		"""Draw the cursor on a view.
		"""
		ogl.glPushAttrib(ogl.GL_LIGHTING_BIT)
		ogl.glDisable(ogl.GL_LIGHTING)
		pos = view.camera().projectedCoordinatesOf(self.position() )
		x = int(pos.x)
		y = int(pos.y)
		view.startScreenCoordinatesSystem()
		ogl.glBegin(ogl.GL_LINES)
		ogl.glColor3f(1.,0.,0.)
		ogl.glVertex2i(x + 2,y)
		ogl.glVertex2i(x + 10,y)
		ogl.glVertex2i(x - 2,y)
		ogl.glVertex2i(x - 10,y)
		ogl.glVertex2i(x,y + 2)
		ogl.glVertex2i(x,y + 10)
		ogl.glVertex2i(x,y - 2)
		ogl.glVertex2i(x,y - 10)
		ogl.glEnd()
		view.stopScreenCoordinatesSystem()
		ogl.glPopAttrib()

