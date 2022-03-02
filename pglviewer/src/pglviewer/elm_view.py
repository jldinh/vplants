from PyQt4.QtCore import QObject
import OpenGL.GL as ogl

class ElmView (QObject) :
	"""A basic implementation of a displayable element
	
	display nothing but manage some opengl attributes
	"""
	def __init__ (self, name) :
		"""Constructor
		
		:Parameters:
		 - `name` (str) - name of the object
		"""
		QObject.__init__(self)
		self.setObjectName(name)
		
		#opengl attributes
		self._lightning = True
		self._line_width = None
		self._point_size = None
		self._use_alpha = False
		self._alpha_threshold = 0.16
		self._face_culling = None
	
	########################################################
	#
	#		attributes
	#
	########################################################
	def name (self) :
		"""Name of the object
		
		:Returns Type: str
		"""
		return self.objectName()
	
	def set_name (self, name) :
		"""Set the name of the object
		
		:Parameters:
		 - `name` (str) - name of the object
		"""
		self.setObjectName(name)
	
	def lightning (self) :
		"""Test wether the element receive light
		
		:Returns Type: bool
		"""
		return self._lightning
	
	def set_lightning (self, lightning) :
		"""Force the element to use light or not
		
		:Parameters:
		 - `lighting` (bool) - if False
		    the element will not take opengl
		    lights into account for rendering
		"""
		self._lightning = lightning
	
	def line_width (self) :
		"""Line width used for display
		
		:Returns Type: float or None
		 if this property has not been set
		"""
		return self._line_width
	
	def set_line_width (self, width) :
		"""Set line width used for display
		
		:Parameters:
		 - `width` (float) - new line width
		"""
		self._line_width = width
	
	def point_size (self) :
		"""Point size used for display
		
		:Returns Type: float or None
		 if this property has not been set
		"""
		return self._point_size
	
	def set_point_size (self, size) :
		"""Set point size used for display
		
		:Parameters:
		 - `size` (float) - new point size
		"""
		self._point_size = size
	
	def is_alpha_used (self) :
		"""Is alpha culling enabled
		
		:Returns Type: bool
		"""
		return self._use_alpha
	
	def use_alpha (self, used) :
		"""Set the use of alpha
		
		:Parameters:
		 - `used` (bool)
		"""
		self._use_alpha = used
	
	def alpha_threshold (self) :
		"""Threshold below which an object
		is not displayed.
		
		:Returns Type: float
		"""
		return self._alpha_threshold
	
	def set_alpha_threshold (self, threshold) :
		"""Set threshold below which an
		object is no longer displayed.
		
		:Parameters:
		 - `threshold` (float)
		"""
		self._alpha_threshold = threshold
	
	def face_culling (self) :
		"""Face to be culled or None
		if all faces are displayed.
		
		:Returns Type: None or constants.FACE
		"""
		return self._face_culling
	
	def set_face_culling (self, face) :
		"""Set the type of face to cull
		
		:Parameters:
		 - `face`:
		    - (constants.FACE) face to cull
		    - (None) display all faces
		"""
		self._face_culling = face
	
	########################################################
	#
	#		display
	#
	########################################################
	def pre_draw (self, view, mode) :
		"""Initialise variable before draw
		
		:Parameters:
		 - `view` (View3D) - the view in which
		    the element is to be displayed
		 - `mode` (constants.DRAW_MODE) - type
		    of display
		"""
		if not self._lightning :
			ogl.glPushAttrib(ogl.GL_LIGHTING_BIT)
			ogl.glDisable(ogl.GL_LIGHTING)
		if self._line_width is not None :
			ogl.glLineWidth(self._line_width)
		if self._point_size is not None :
			ogl.glPointSize(self._point_size)
		if self._use_alpha :
			ogl.glEnable(ogl.GL_ALPHA_TEST)
			ogl.glAlphaFunc(ogl.GL_GREATER,
			                self._alpha_threshold)
			ogl.glEnable(ogl.GL_BLEND)
			ogl.glBlendFunc(ogl.GL_SRC_ALPHA,
			                ogl.GL_ONE_MINUS_SRC_ALPHA)
		if self._face_culling is not None :
			ogl.glEnable(ogl.GL_CULL_FACE)
			ogl.glCullFace(self._face_culling)
	
	def draw (self, view, mode) :
		"""Display the element inside the view
		
		:Parameters:
		 - `view` (View3D) - the view in which
		    the element is to be displayed
		 - `mode` (constants.DRAW_MODE) - type
		    of display
		"""
		pass
	
	def post_draw (self, view, mode) :
		"""Release variables after draw
		
		:Parameters:
		 - `view` (View3D) - the view in which
		    the element is to be displayed
		 - `mode` (constants.DRAW_MODE) - type
		    of display
		"""
		if self._face_culling is not None :
			ogl.glDisable(ogl.GL_CULL_FACE)
		if self._use_alpha :
			ogl.glDisable(ogl.GL_BLEND)
			ogl.glDisable(ogl.GL_ALPHA_TEST)
		if self._point_size is not None :
			ogl.glPointSize(1.)
		if self._line_width is not None :
			ogl.glLineWidth(1.)
		if not self._lightning :
			ogl.glPopAttrib()
	
	def _draw (self, view, mode) :
		self.pre_draw(view,mode)
		self.draw(view,mode)
		self.post_draw(view,mode)
	
	#########################################################
	#
	#		geometrical attributes
	#
	#########################################################
	def bounding_box (self) :
		"""Bounding box of the displayed element
		
		:Returns Type: :class:BoundingBox
		"""
		return None
	
	def position (self) :
		"""Position of the displayed element
		
		:Returns Type: Vector
		"""
		return None
	
	def center (self) :
		"""Position of the center of the element
		
		:Returns Type: Vector
		"""
		return None
	
	########################################################
	#
	#		persistence
	#
	########################################################
	def save_state (self, state, viewer) :
		"""Write the current state of this
		element in state.
		
		It is the user responsability to
		store in state everything needed
		to restore the state of the view.
		
		.. warning: use a well defined key
		   to store all informations about
		   this element in a submap of state.
		   Default implementation use object
		   name to store informations relative
		   to opengl attributes.
		
		.. warning: state is intented to be
		   pickled. To avoid trouble when
		   restoring state, store only basic
		   python types and not user defined
		   custom classes :)
		
		:Parameters:
		 - `state` (dict of (str,dict of (str,param) ) )
		 - `viewer` (Viewer) - actual viewer
		
		:Return: None, modify state in place
		"""
		st = {}
		state[str(self.name() )] = st
		
		st["lightning"] = self.lightning()
		st["line_width"] = self.line_width()
		st["point_size"] = self.point_size()
		st["use_alpha"] = self.is_alpha_used()
		st["alpha_threshold"] = self.alpha_threshold()
		st["face_culling"] = self.face_culling()
	
	def restore_state (self, state, viewer) :
		"""Try to restore the state of this
		element.
		
		Use informations stored in state. If
		informations are not available do nothing.
		
		:Parameters:
		 - `state` (dict of (str,dict of (str,param) ) )
		 - `viewer` (Viewer) - actual viewer
		"""
		try :
			st = state[str(self.name() )]
			self.set_lightning(st["lightning"])
			self.set_line_width(st["line_width"])
			self.set_point_size(st["point_size"])
			self.use_alpha(st["use_alpha"])
			self.set_alpha_threshold(st["alpha_threshold"])
			self.set_face_culling(st["face_culling"])
		except KeyError :
			print "unable to restore state for element %s (ElmView)" % str(self.name() )



