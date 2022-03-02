from PyQt4.QtCore import Qt,SIGNAL
from PyQt4.QtGui import QColor
import OpenGL.GL as ogl
from PyQGLViewer import QGLViewer,Vec,WorldConstraint
from xcamera import XCamera,VIEW
from cursor import Cursor3D
from constants import DRAW_MODE,ROTATION_ANCHOR

ogl_clipping_planes = [ogl.GL_CLIP_PLANE0,
                       ogl.GL_CLIP_PLANE1,
                       ogl.GL_CLIP_PLANE2,
                       ogl.GL_CLIP_PLANE3,
                       ogl.GL_CLIP_PLANE4,
                       ogl.GL_CLIP_PLANE5]

class View3D (QGLViewer) :
	"""A subclass of QGLViewer with added features
	like :
	    Xcamera
	    Cursor
	    improved loops
	    selection
	"""
	def __init__ (self, parent=None) :
		QGLViewer.__init__(self,parent)
		#viewer settings
		#self.setStateFileName("")
		self.setShortcut(QGLViewer.ANIMATION, 0)
		self.setShortcut(QGLViewer.CAMERA_MODE, 0)
		
		#view
		cam = XCamera(self.camera(),self.sceneRadius() )
		self.setCamera(cam)
		self.connect(cam._emitter,SIGNAL("set_view_mode"),self.update)
		self._background_color = QColor(150,150,150)
		
		#attributes
		self._worlds = []
		
		#curseur 3D
		self._cursor = Cursor3D()
		self._cursor_visibility = True
		self.connect(self._cursor,SIGNAL("set_position"),self.cursor_moved)
		
		#mouse
		self._rotation_center = ROTATION_ANCHOR.CURSOR
		self._mouse_tool_activated = False
		self._moved = False
		self._tool = None
		
		#selection
		self._draw_with_names = None
		self._post_selection = None
		
		#clipping planes
		self._free_planes = list(ogl_clipping_planes)
	
	def init (self) :
		QGLViewer.init(self)
		self.setBackgroundColor(self._background_color)
		
#		ogl.glEnable(ogl.GL_LIGHTING)
#		ogl.glLightfv(ogl.GL_LIGHT0,
#		              ogl.GL_POSITION,
#		              (0,0,1,0) )
	
	def clear (self) :
		for world in self.worlds() :
			self.disconnect(world,SIGNAL("update"),self.update)
		del self._worlds[:]
	
	def background_color (self) :
		return self._background_color
	
	def set_background_color (self, color) :
		self._background_color = color
		self.setBackgroundColor(color)
		self.emit(SIGNAL("set_background_color"),color)
	
	def keyPressEvent (self, event) :
		if event.key() == Qt.Key_Escape :
			pass
		else :
			QGLViewer.keyPressEvent(self,event)
	
	def keyReleaseEvent (self, event) :
		if event.key() == Qt.Key_Escape :
			self.emit(SIGNAL("echap pressed"),)
		else :
			QGLViewer.keyReleaseEvent(self,event)
	
	def _update (self, *args) :
		QGLViewer.update(self)
		self.updateGL()
	
	def update (self, *args) :
		self._update()
		self.emit(SIGNAL("update") )
	
	#############################################
	#
	#		world
	#
	#############################################
	def worlds (self) :
		"""Access to the displayed worlds.
		"""
		return iter(self._worlds)
	
	def add_world (self, world) :
		"""Add a new world to display.
		"""
		self._worlds.append(world)
		self.bound_to_worlds()
		self.connect(world,SIGNAL("update"),self.update)
		self.emit(SIGNAL("add_world"),world)
	
	def remove_world (self, world) :
		"""Remove a world from display.
		"""
		try :
			self._worlds.remove(world)
			self.bound_to_worlds()
			self.disconnect(world,SIGNAL("update"),self.update)
			self.emit(SIGNAL("remove_world"),world)
		except ValueError :
			raise
	
	def set_world (self, world) :
		"""Set a new single world to display.
		"""
		self.clear()
		self.add_world(world)
	
	##############################################
	#
	#		managment of 3D cursor
	#
	##############################################
	def cursor (self) :
		"""Access to the cursor.
		"""
		return self._cursor
	
	def cursor_visibility (self) :
		"""Tell wether the cursor is visible.
		"""
		return self._cursor_visibility
	
	def set_cursor_visibility (self, visible=True) :
		"""Set wether or not the cursor is visible.
		"""
		self._cursor_visibility = visible
		self.update()
		self.emit(SIGNAL("set_cursor_visibility"),visible)
	
	def cursor_moved (self, pos) :
		"""slot called when position of the cursor has changed.
		"""
		if self._rotation_center == ROTATION_ANCHOR.CURSOR :
			self.define_rotation_center()
		self.update()
		
	def move_cursor (self, screen_pos) :
		"""Move the cursor position according
		to a point defined in the screen 2D frame.
		"""
		old_pos = self.camera().projectedCoordinatesOf(self.cursor().position() )
		pos = self.camera().unprojectedCoordinatesOf(Vec(screen_pos.x(),screen_pos.y(),old_pos.z) )
		self.cursor().set_position(pos)
	
	#############################################
	#
	#		display
	#
	#############################################
	def draw (self) :
		"""Actually redraw the current world.
		"""
		for world in self.worlds() :
			world._draw(self,DRAW_MODE.NORMAL)
		if self.cursor_visibility() :
			self._cursor.draw(self)
	
	def fastDraw (self) :
		"""Redraw the view in draft mode.
		"""
		for world in self.worlds() :
			world._draw(self,DRAW_MODE.DRAFT)
		if self.cursor_visibility() :
			self._cursor.draw(self)
	
	#############################################
	#
	#		view
	#
	#############################################
	def dimension (self) :
		"""Return the current number of dimension shown.
		"""
		if self.camera().frame().constraint() is None :
			return 3
		else :
			return 2
	
	def set_dimension (self, dim=2) :
		"""Set the dimension of the view to either 2 or 3.
		"""
		if dim == 2 :
			cam = self.camera()
			cam.set_view_mode(VIEW.TOP)
			cam.setType(cam.ORTHOGRAPHIC)
			self.show_entire_world()
			cons = WorldConstraint()
			cons.setRotationConstraintType(cons.FORBIDDEN)
			cam.frame().setConstraint(cons)
		elif dim == 3 :
			cam = self.camera()
			cam.setType(cam.PERSPECTIVE)
			cam.frame().setConstraint(None)
		else :
			raise NotImplementedError("cannot accept a display if in such dimension (%s)" % str(dim))
		self.update()
		self.emit(SIGNAL("set_dimension"),dim)
	
	def bound_to_worlds (self) :#a revoir pour ameliorer sans faire reference a des methodes pgl
		"""Change radius of display to match the current worlds.
		"""
		radius = 0
		for world in self.worlds() :
			bb = world.bounding_box()
			if bb is not None :
				if self._rotation_center == ROTATION_ANCHOR.WORLD :
					loc_radius = max(bb.getSize() )
					self.setSceneCenter(Vec(*tuple(bb.getCenter() ) ) )
				else :
					loc_radius = max(bb.lowerLeftCorner.__norm__(),
					             bb.upperRightCorner.__norm__())
				radius = max(radius,loc_radius)
		if radius > 0 :
			self.setSceneRadius(radius)
			self.update()
			self.emit(SIGNAL("bound_to_worlds"),radius)
	
	def show_entire_world (self) :
		"""Try to display the entire world in the window.
		"""
		self.camera().showEntireScene()
		self.emit(SIGNAL("show_entire_world") )
	
	################################################
	#
	#		rotation view
	#
	################################################
	def rotation_center (self) :
		"""Return the actual rotation center.
		"""
		return self._rotation_center
	
	def set_rotation_center (self, anchor=ROTATION_ANCHOR.CURSOR) :
		"""Set the rotation center.
		"""
		self._rotation_center = anchor
		self.define_rotation_center()
		self.emit(SIGNAL("set_rotation_center"),anchor)
	
	def define_rotation_center (self) :
		"""Register informations relative to the rotating center.
		"""
		if self._rotation_center == ROTATION_ANCHOR.CURSOR :
			self.setSceneCenter(self.cursor().position() )
		elif self._rotation_center == ROTATION_ANCHOR.WORLD :
			for world in self.worlds() :
				cent = world.center()
				if cent is not None :
					self.setSceneCenter(Vec(*tuple(cent) ) )
		elif self._rotation_center == ROTATION_ANCHOR.SPACE :
			self.setSceneCenter(Vec(0,0,0) )
		else :
			raise UserWarning("undefined center")
	##########################################################
	#
	#		selection
	#
	##########################################################
	def set_select_functions (self, draw, post) :
		"""Register 2 functions for selection.
		
		draw: a draw with labels functions
		post: a callback function
		"""
		self._draw_with_names = draw
		self._post_selection = post
	
	def clear_select_functions (self) :
		"""Remove functions.
		"""
		self._draw_with_names = None
		self._post_selection = None
	
	def drawWithNames (self) :
		"""Subclass QGLViewer to call draw_with_names.
		"""
		if self._draw_with_names is not None :
			self._draw_with_names(self)
	
	def postSelection (self, point) :
		"""Subclass QGLViewer to call post_selection.
		"""
		if self._post_selection is not None :
			self._post_selection(self,point)
	
	################################################
	#
	#		mouse managment
	#
	################################################
	def tool (self) :
		return self._tool

	def set_tool (self, tool) :
		self._tool = tool
	
	def mousePressEvent (self, event) :
		"""Dispatch mouse press event.
		"""
		if self._tool is None :
			QGLViewer.mousePressEvent(self, event)
		else :
			self._tool.mousePressEvent(self, event)
	
	def mouseMoveEvent (self, event) :
		"""Dispatch mouse move event.
		"""
		if self._tool is None :
			QGLViewer.mouseMoveEvent(self, event)
			self._moved = True
		else :
			self._tool.mouseMoveEvent(self, event)

	def mouseReleaseEvent (self, event) :
		"""Dispatch mouse release event.
		"""
		if self._tool is None :
			QGLViewer.mouseReleaseEvent(self, event)
			if self._moved :
				self._moved = False
			else :
				if self.cursor_visibility() \
				        and event.button() == Qt.LeftButton \
				        and event.modifiers() == Qt.NoModifier :
					self.move_cursor(event.pos() )
					self.update()
		else :
			self._tool.mouseReleaseEvent(self, event)
	
	def mouseDoubleClickEvent (self, event) :
		"""Dispatch mouse double click event.
		"""
		if self._tool is None :
			QGLViewer.mouseDoubleClickEvent(self, event)
		else :
			self._tool.mouseDoubleClickEvent(self, event)
	
	def wheelEvent (self, event) :#TODO bug
		"""Dispatch wheel event.
		"""
		if self._tool is None :
			QGLViewer.wheelEvent(self, event)
		else :
			self._tool.wheelEvent(self, event)
	
	################################################
	#
	#		clipping planes
	#
	################################################
	def get_plane (self) :
		"""Get an available clipping plane.
		"""
		if len(self._free_planes) == 0 :
			raise UserWarning("no more OpenGl clipping plane available")
		return self._free_planes.pop(0)
	
	def release_plane (self, plane) :
		"""Release a used clipping plane.
		"""
		self._free_planes.append(plane)
		self._free_planes.sort()

