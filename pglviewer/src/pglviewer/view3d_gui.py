from os import path
from PyQt4.QtCore import Qt,SIGNAL,QObject
from PyQt4.QtGui import QAction,QActionGroup,QToolBar,\
                        QMenu,QIcon,QFileDialog,\
                        QColorDialog,QPixmap,QColor,\
                        QStatusBar,QLineEdit
from PyQGLViewer import Camera
from constants import VIEW,ROTATION_ANCHOR
from elm_gui import ElmGUI
import pglviewer_rc

#######################################################
#
#	view
#
#######################################################
class ActionDisplayAll (QAction) :
	"""Action that trigger display_entire_world.
	"""
	def __init__ (self, parent) :
		QAction.__init__(self,"display all",parent)
		self.setIcon(QIcon(":image/display_all") )
		self.connect(self,SIGNAL("triggered(bool)"),self.display_all)
	
	def set_view (self, view) :
		self._view = view
	
	def display_all (self) :
		view = self._view
		if view is not None :
			view.bound_to_worlds()
			view.show_entire_world()

class ActionBackgroundColor (QAction) :
	"""Change the background color fo the view.
	"""
	def __init__ (self, parent) :
		QAction.__init__(self,"background color",parent)
		self._pix = QPixmap(80,80)
		self.setIcon(QIcon(self._pix) )
		self.connect(self,SIGNAL("triggered(bool)"),self.change_color)
	
	def set_view (self, view) :
		if view is not None :
			self.color_changed(view.backgroundColor() )
			self.connect(view,
			             SIGNAL("set_background_color"),
			             self.color_changed)
		else :
			if self._view is not None :
				self.disconnect(self._view,
				                SIGNAL("set_background_color"),
				                self.color_changed)
		
		self._view = view
	
	def color_changed (self, color) :
		self._pix.fill(color)
		self.setIcon(QIcon(self._pix) )
	
	def change_color (self) :
		color = QColorDialog.getColor(self._view.background_color() )
		if color.isValid() :
			self._view.set_background_color(color)

class ActionSnapshot (QAction) :
	"""Take a snapshot of the current frame.
	"""
	def __init__ (self, parent) :
		QAction.__init__(self,"snapshot",parent)
		self.setIcon(QIcon(":image/snapshot") )
		self.setShortcut("Ctrl+B")
		self.connect(self,SIGNAL("triggered(bool)"),self.snapshot)
	
	def set_view (self, view) :
		self._view = view
	
	def snapshot (self) :
		view = self._view
		if view is not None :
			filename = QFileDialog.getSaveFileName(view.parent(),
			                                       "save snapshot",
			                                       ".",
			                                       "*.png")
			if not filename.isNull() :
				filename = str(filename)
				name,ext = path.splitext(filename)
				if len(ext) == 0 :
					ext = "png"
					filename = "%s.png" % filename
				else :
					ext = ext[1:]
				if ext in ("png","bmp","jpg") :
					view.setSnapshotFormat(ext)
				view.saveSnapshot(filename,True)
		
class ActionViewDimension (QAction) :
	"""Change the dimension of the view.
	"""
	def __init__ (self, parent, dim) :
		QAction.__init__(self,"%dD" % dim,parent)
		self._dim = dim
		self.setCheckable(True)
		self.connect(self,SIGNAL("triggered(bool)"),self.change_dimension)
	
	def set_view (self, view) :
		if view is None :
			if self._view is not None :
				self.disconnect(self._view,
				                SIGNAL("set_dimension"),
				                self.dimension_changed)
		else :
			self.dimension_changed(view.dimension() )
			self.connect(view,
			             SIGNAL("set_dimension"),
			             self.dimension_changed)
		
		self._view = view
	
	def change_dimension (self, state) :
		if state and self._view is not None :
			self._view.set_dimension(self._dim)
	
	def dimension_changed (self, dim) :
		self.setChecked(self._dim == dim)	

class ActionCameraOrthographic (QAction) :
	"""Change camera mode.
	"""
	def __init__ (self, parent) :
		QAction.__init__(self,"orthographic",parent)
		self.setCheckable(True)
		self.connect(self,SIGNAL("triggered(bool)"),self.change_camera_type)
	
	def set_view (self, view) :
		if view is None :
			if self._view is not None :
				self.connect(self._view.camera()._emitter,
				             SIGNAL("setType"),
				             self.camera_type_changed)
		else :
			self.camera_type_changed(view.camera().type() )
			self.connect(view.camera()._emitter,
			             SIGNAL("setType"),
			             self.camera_type_changed)
		
		self._view = view
	
	def change_camera_type (self, ortho) :
		if self._view is not None :
			cam = self._view.camera()
			if ortho :
				cam.setType(Camera.ORTHOGRAPHIC)
			else :
				cam.setType(Camera.PERSPECTIVE)
	
	def camera_type_changed (self, cam_type) :
		self.setChecked(cam_type == Camera.ORTHOGRAPHIC)

class ActionViewMode (QAction) :
	"""Action that change the current view mode.
	"""
	def __init__ (self, parent, view_mode, txt, icon_name) :
		QAction.__init__(self,txt,parent)
		self._view_mode = view_mode
		self.setIcon(QIcon(":image/%s" % icon_name) )
		self.connect(self,SIGNAL("triggered(bool)"),self.change_view_mode)
	
	def set_view (self, view) :
		self._view = view
	
	def change_view_mode (self) :
		if self._view is not None :
			self._view.camera().set_view_mode(self._view_mode)

#######################################################
#
#	cursor
#
#######################################################
class ActionCenterCursor (QAction) :
	"""Set the position of the 3D cursor to the
	center of the view.
	"""
	def __init__ (self, parent) :
		QAction.__init__(self,"center cursor",parent)
		self.setIcon(QIcon(":image/center_cursor") )
		self.setShortcut("Shift+C")
		self.connect(self,SIGNAL("triggered(bool)"),self.center_cursor)
	
	def set_view (self, view) :
		self._view = view
	
	def center_cursor (self) :
		if self._view is not None :
			self._view.cursor().set_position( (0,0,0) )

class ActionCursorVisible (QAction) :
	"""Set wether the cursor is visible.
	"""
	def __init__ (self, parent) :
		QAction.__init__(self,"cursor visible",parent)
		self.setIcon(QIcon(":image/cursor_visible") )
		self.setCheckable(True)
		
	
	def set_view (self, view) :
		if view is None :
			if self._view is not None :
				self.disconnect(self,
				                SIGNAL("triggered(bool)"),
				                self._view.set_cursor_visibility)
				self.disconnect(self._view,
				                SIGNAL("set_cursor_visibility"),
				                self.setChecked)
		else :
			self.setChecked(view.cursor_visibility() )
			self.connect(self,
			             SIGNAL("triggered(bool)"),
			             view.set_cursor_visibility)
			self.connect(view,
			             SIGNAL("set_cursor_visibility"),
			             self.setChecked)
		self._view = view

#######################################################
#
#	anchor
#
#######################################################
class ActionChangeAnchor (QAction) :
	"""Change the current rotation anchor.
	"""
	def __init__ (self, parent, anchor, txt) :
		QAction.__init__(self,txt,parent)
		self._anchor = anchor
		self.setCheckable(True)
		self.connect(self,SIGNAL("triggered(bool)"),self.set_rotation_center)
	
	def set_view (self, view) :
		if view is None :
			if self._view is not None :
				self.disconnect(self._view,
				                SIGNAL("set_rotation_center"),
				                self.rotation_center_changed)
		else :
			self.rotation_center_changed(view.rotation_center() )
			self.connect(view,
			             SIGNAL("set_rotation_center"),
			             self.rotation_center_changed)
		
		self._view = view
	
	def set_rotation_center (self, is_set) :
		if is_set and self._view is not None :
			self._view.set_rotation_center(self._anchor)
	
	def rotation_center_changed (self, anchor) :
		self.setChecked(self._anchor == anchor)

class ActionToggleAnchor (QAction) :
	"""Toggle rotation anchor.
	"""
	def __init__ (self, parent) :
		QAction.__init__(self,"toggle",parent)
		self.setShortcut("W")
		self.connect(self,SIGNAL("triggered(bool)"),self.toggle_rotation_center)
	
	def set_view (self, view) :
		self._view = view
	
	def toggle_rotation_center (self) :
		if self._view is not None :
			anchor = self._view.rotation_center()
			if anchor == ROTATION_ANCHOR.CURSOR :
				self._view.set_rotation_center(ROTATION_ANCHOR.WORLD)
			elif anchor == ROTATION_ANCHOR.WORLD :
				self._view.set_rotation_center(ROTATION_ANCHOR.SPACE)
			elif anchor == ROTATION_ANCHOR.SPACE :
				self._view.set_rotation_center(ROTATION_ANCHOR.CURSOR)
			else :
				raise UserWarning("unknown ROTATION_ANCHOR")
#######################################################
#
#	GUI
#
#######################################################
class View3DGUI (ElmGUI) :
	"""Some standard GUI for a 3D view.
	"""
	def __init__ (self) :
		ElmGUI.__init__(self)
	
	def setup_ui (self) :
		if ElmGUI.setup_ui(self) :
			self._action_bar = QToolBar("view3D")
			self._menu = QMenu("View")
			#view
			self._action_display_all = ActionDisplayAll(self._action_bar)
			self._action_bar.addAction(self._action_display_all)
			self._menu.addAction(self._action_display_all)
			
			self._action_background_color = ActionBackgroundColor(self._action_bar)
			self._action_bar.addAction(self._action_background_color)
			self._menu.addAction(self._action_background_color)
			
			self._action_snapshot = ActionSnapshot(self._action_bar)
			self._action_bar.addAction(self._action_snapshot)
			self._menu.addAction(self._action_snapshot)
			
			#dimension
			menu = self._menu.addMenu("dimension")
			self._actions_view_dimension = []
			self._dimension_group = QActionGroup(self._action_bar)
			for dim in (2,3) :
				action = ActionViewDimension(self._action_bar,dim)
				menu.addAction(action)
				self._dimension_group.addAction(action)
				self._actions_view_dimension.append(action)
			
			#camera
			menu = self._menu.addMenu("camera")
			self._action_camera_orthographic = ActionCameraOrthographic(self._action_bar)
			menu.addAction(self._action_camera_orthographic)
			menu.addSeparator()
			self._actions_view_mode = []
			for view_mode,txt,icon_name in [(VIEW.TOP,"top view","xy.png",),
			                                (VIEW.BOTTOM,"bottom view","-xy.png"),
			                                (VIEW.RIGHT,"right view","xz.png"),
			                                (VIEW.LEFT,"left view","-xz.png"),
			                                (VIEW.FRONT,"front view","yz.png"),
			                                (VIEW.BACK,"back view","-yz.png")] :
				action = ActionViewMode(self._action_bar,view_mode,txt,icon_name)
				menu.addAction(action)
				self._actions_view_mode.append(action)
			
			#cursor
			menu = self._menu.addMenu("Cursor")
			self._action_center_cursor = ActionCenterCursor(self._action_bar)
			self._action_bar.addAction(self._action_center_cursor)
			menu.addAction(self._action_center_cursor)
			
			self._action_cursor_visible = ActionCursorVisible(self._action_bar)
			self._action_bar.addAction(self._action_cursor_visible)
			menu.addAction(self._action_cursor_visible)
			
			self._xcoord = QLineEdit("")
			self._xcoord.setMaximumWidth(50)
			self._xcoord.setAlignment(Qt.AlignRight)
			
			self._ycoord = QLineEdit("")
			self._ycoord.setMaximumWidth(50)
			self._ycoord.setAlignment(Qt.AlignRight)
			
			self._zcoord = QLineEdit("")
			self._zcoord.setMaximumWidth(50)
			self._zcoord.setAlignment(Qt.AlignRight)
			
			QObject.connect(self._xcoord,
			                SIGNAL("editingFinished()"),
			                self.change_cursor_position)
			QObject.connect(self._ycoord,
			                SIGNAL("editingFinished()"),
			                self.change_cursor_position)
			QObject.connect(self._zcoord,
			                SIGNAL("editingFinished()"),
			                self.change_cursor_position)
			
			#anchor
			menu = self._menu.addMenu("Rotation center")
			self._actions_rotation_anchor = []
			self._anchor_group = QActionGroup(self._action_bar)
			for anchor,txt in [(ROTATION_ANCHOR.CURSOR,"Cursor"),
			                   (ROTATION_ANCHOR.WORLD,"World"),
			                   (ROTATION_ANCHOR.SPACE,"Space")] :
				action = ActionChangeAnchor(menu,anchor,txt)
				menu.addAction(action)
				self._anchor_group.addAction(action)
				self._actions_rotation_anchor.append(action)
			
			self._action_toggle_anchor = ActionToggleAnchor(self._action_bar)
			menu.addSeparator()
			menu.addAction(self._action_toggle_anchor)
			
			return True
		else :
			return False
	
	def install (self, main_window) :
		ElmGUI.install(self,main_window)
		#install
		main_window.menuBar().addMenu(self._menu)
		self.add_action_bar(main_window,self._action_bar)
		#register view
		for action in (self._action_display_all,
		               self._action_background_color,
		               self._action_snapshot,
		               self._action_camera_orthographic,
		               self._action_center_cursor,
		               self._action_cursor_visible,
		               self._action_toggle_anchor) \
		              + tuple(self._actions_view_dimension) \
		              + tuple(self._actions_view_mode) \
		              + tuple(self._actions_rotation_anchor) :
			action.set_view(main_window.view() )
		
		self.cursor_position_changed(main_window.view().cursor().position() )
		QObject.connect(main_window.view().cursor(),
		                SIGNAL("set_position"),
		                self.cursor_position_changed)
		
		#status bar
		self.add_status_widget(main_window,self._xcoord,True)
		self.add_status_widget(main_window,self._ycoord,True)
		self.add_status_widget(main_window,self._zcoord,True)
	
	def uninstall (self, main_window) :
		ElmGUI.uninstall(self,main_window)
		main_window.menuBar().removeAction(self._menu.menuAction() )
		self.remove_bar(main_window,self._action_bar)
		#discard view
		for action in (self._action_display_all,
		               self._action_background_color,
		               self._action_snapshot,
		               self._action_camera_orthographic,
		               self._action_center_cursor,
		               self._action_cursor_visible,
		               self._action_toggle_anchor) \
		              + tuple(self._actions_view_dimension) \
		              + tuple(self._actions_view_mode) \
		              + tuple(self._actions_rotation_anchor) :
			action.set_view(None)
		
		QObject.disconnect(main_window.view().cursor(),
		                   SIGNAL("set_position"),
		                   self.cursor_position_changed)
		
		#status bar
		self.remove_status_widget(main_window,self._xcoord)
		self.remove_status_widget(main_window,self._ycoord)
		self.remove_status_widget(main_window,self._zcoord)
	
	def change_cursor_position (self) :
		"""Change the cursor position
		according to information in statusbar
		"""
		main_window = self.installed()
		if main_window is not None :
			x = float(str(self._xcoord.text() ) )
			y = float(str(self._ycoord.text() ) )
			z = float(str(self._zcoord.text() ) )
			main_window.view().cursor().set_position( (x,y,z) )
	
	def cursor_position_changed (self, pos) :
		"""Display the new cursor position
		"""
		self._xcoord.setText("%.2f" % pos.x)
		self._ycoord.setText("%.2f" % pos.y)
		self._zcoord.setText("%.2f" % pos.z)



