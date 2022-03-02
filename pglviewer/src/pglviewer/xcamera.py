from math import sqrt
from PyQt4.QtCore import Qt,SIGNAL,QObject
from PyQGLViewer import Camera,Vec,ManipulatedCameraFrame
from constants import VIEW

class XCameraFrame (ManipulatedCameraFrame) :
	"""Extend the Camera frame in PyQGLViewer
	adding different predefined views.
	"""
	def __init__(self, frame, default_dist=10.) :
		ManipulatedCameraFrame.__init__(self,frame)
		#managment of different type of views
		self._current_view_mode = VIEW.SPACE
		self._last_view_pos = {VIEW.RIGHT:Vec(0,default_dist,0),
		                       VIEW.LEFT:Vec(0,-default_dist,0),
		                       VIEW.FRONT:Vec(default_dist,0,0),
		                       VIEW.BACK:Vec(-default_dist,0,0),
		                       VIEW.TOP:Vec(0,0,default_dist),
		                       VIEW.BOTTOM:Vec(0,0,-default_dist)}
	
	def set_view_mode (self, view_type) :
		"""Specify a predefined view.
		"""
		self._current_view_mode = view_type
		if view_type == VIEW.SPACE :
			pass
		else :
			if view_type == VIEW.RIGHT :
				self.setOrientation(0.,sqrt(2)/2,sqrt(2)/2,0.)
			elif view_type == VIEW.LEFT :
				self.setOrientation(sqrt(2)/2,0.,0.,sqrt(2)/2.)
			elif view_type == VIEW.FRONT :
				self.setOrientation(0.5,0.5,0.5,0.5)
			elif view_type == VIEW.BACK :
				self.setOrientation(0.5,-0.5,-0.5,0.5)
			elif view_type == VIEW.TOP :
				self.setOrientation(0.,0.,0.,1.)
			elif view_type == VIEW.BOTTOM :
				self.setOrientation(0.,1.,0.,0.)
			else :
				raise UserWarning("not available")
			self.setPosition(self._last_view_pos[view_type])
	
	def update_view_position (self) :
		"""Record view position for further usage.
		"""
		pos = self.position()
		if self._current_view_mode == VIEW.RIGHT :
			self._last_view_pos[VIEW.RIGHT] = Vec(pos.x,pos.y,pos.z)
			self._last_view_pos[VIEW.LEFT] = Vec(pos.x,-pos.y,pos.z)
		elif self._current_view_mode == VIEW.LEFT :
			self._last_view_pos[VIEW.LEFT] = Vec(pos.x,pos.y,pos.z)
			self._last_view_pos[VIEW.RIGHT] = Vec(pos.x,-pos.y,pos.z)
		elif self._current_view_mode == VIEW.FRONT :
			self._last_view_pos[VIEW.FRONT] = Vec(pos.x,pos.y,pos.z)
			self._last_view_pos[VIEW.BACK] = Vec(-pos.x,pos.y,pos.z)
		elif self._current_view_mode == VIEW.BACK :
			self._last_view_pos[VIEW.BACK] = Vec(pos.x,pos.y,pos.z)
			self._last_view_pos[VIEW.FRONT] = Vec(-pos.x,pos.y,pos.z)
		elif self._current_view_mode == VIEW.TOP :
			self._last_view_pos[VIEW.TOP] = Vec(pos.x,pos.y,pos.z)
			self._last_view_pos[VIEW.BOTTOM] = Vec(pos.x,pos.y,-pos.z)
		elif self._current_view_mode == VIEW.BOTTOM :
			self._last_view_pos[VIEW.BOTTOM] = Vec(pos.x,pos.y,pos.z)
			self._last_view_pos[VIEW.TOP] = Vec(pos.x,pos.y,-pos.z)
	
	def wheelEvent (self, event, camera) :
		ManipulatedCameraFrame.wheelEvent(self,event,camera)
		self.update_view_position()
	
	def mouseReleaseEvent (self, event, camera) :
		ManipulatedCameraFrame.mouseReleaseEvent(self,event,camera)
		self.update_view_position()
	
	def mouseMoveEvent (self, event, camera) :
		if not event.buttons() ^ Qt.LeftButton :
			self.set_view_mode(VIEW.SPACE)
		ManipulatedCameraFrame.mouseMoveEvent(self,event,camera)

class XCamera (Camera) :
	"""Extend the Camera in PyQGLViewer, adding a XCameraFrame.
	"""
	def __init__ (self, cam, dist=10.) :
		import pdb; pdb.set_trace()
		Camera.__init__(self)
		self.setFrame(XCameraFrame(self.frame(),dist) )
		self._ortho_size = None
		self._emitter = QObject()
	
	def set_view_mode (self, view_mode) :
		self.frame().set_view_mode(view_mode)
		self._emitter.emit(SIGNAL("set_view_mode"),view_mode)
	
	def setType (self, cam_type) :
		Camera.setType(self,cam_type)
		self._emitter.emit(SIGNAL("setType"),cam_type)
	
	def set_ortho_size (self, size) :
		self._ortho_size = size
	
	def getOrthoWidthHeight (self) :
		if self._ortho_size is None :
			return Camera.getOrthoWidthHeight(self)
		else :
			return self._ortho_size,self._ortho_size
