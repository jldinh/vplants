from PyQt4.QtOpenGL import QGLFramebufferObject
from celltissue.simulation import Process

class Redraw (Process) :
	def __init__ (self, object_view) :
		Process.__init__(self,"redraw")
		self._object_view=object_view
	
	def __call__ (self, *args) :
		self._object_view.redraw()

class Snapshot (Process) :
	def __init__ (self, view) :
		Process.__init__(self,"snapshot")
		self._view=view
	
	def __call__ (self, *args) :
		framegl=QGLFramebufferObject(600,600)
		framegl.bind()
		self._view.updateGL()
		framegl.release()
		framegl.toImage().save("snapshot.png")

