import OpenGL.GL as ogl
from PyQGLViewer import Frame

class ClippingProbe (Frame) :
	"""A frame used to orient a clipping plane in space.
	Must be associated to a specified view to be used.
	"""
	def __init__ (self) :
		Frame.__init__(self)
		self._plane_used = None
		
	def activated (self) :
		"""Tells wether this clipping has been activated.
		"""
		return self._plane_used is not None
	
	def activate (self, view, activation=True) :
		"""Activate or not the clipping probe in a specific view.
		"""
		if activation :
			if self._plane_used is None :
				self._plane_used = view.get_plane()
		else :
			if self._plane_used is not None :
				view.release_plane(self._plane_used)
				self._plane_used = None
	
	def start_clipping (self, view) :
		"""Start clipping in an OpenGL stack.
		"""
		ogl.glEnable(self._plane_used)
		ogl.glPushMatrix()
		ogl.glMultMatrixd(self.worldMatrix() )
		ogl.glClipPlane(self._plane_used, [ 0.,0.,-1.,0. ])
		ogl.glPopMatrix()
	
	def stop_clipping (self, view) :
		"""Stop clipping in an OpenGL stack.
		"""
		ogl.glDisable(self._plane_used)
