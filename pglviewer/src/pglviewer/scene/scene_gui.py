from os.path import splitext
from PyQt4.QtCore import Qt,SIGNAL,QObject
from PyQt4.QtGui import QAction,QIcon,QToolBar,QMenu,QFileDialog, \
                        QUndoCommand
from PyQGLViewer import Vec,Quaternion
from vplants.plantgl.algo import GLRenderer
from ..elm_gui import ElmGUI
from ..elm_tools import SelectTool,\
                        FrameManipulator,UndoFrameManipulation

import scene_rc
#############################################
#
#	file
#
#############################################
class ActionLoadScene (QAction) :
	"""Load a new scene.
	"""
	def __init__ (self, scene, parent) :
		QAction.__init__(self,"load",parent)
		self._scene = scene
		self.setIcon(QIcon(":image/load.png") )
		self.connect(self,SIGNAL("triggered(bool)"),self.load)
	
	def load (self) :
		filename = QFileDialog.getOpenFileName(self.parent().window(),
		                                       "open geom scene",
		                                       "",
		                                       "*.geom")
		if not filename.isNull() :
			scene = self._scene
			scene.clear()
			scene.read(str(filename) )

class ActionSaveScene (QAction) :
	"""Save a scene.
	"""
	def __init__ (self, scene, parent) :
		QAction.__init__(self,"save",parent)
		self._scene = scene
		self.setIcon(QIcon(":image/save.png") )
		self.connect(self,SIGNAL("triggered(bool)"),self.save)
	
	def save (self) :
		filename = QFileDialog.getSaveFileName(self.parent().window(),
		                                       "save geom scene",
		                                       "",
		                                       "*.geom")
		if not filename.isNull() :
			filename = str(filename)
			filename,ext = splitext(filename)
			if ext == "" :
				filename = "%s.geom" % filename
			self._scene.save(filename)

#############################################
#
#	display mode
#
#############################################
class ActionDisplayMode (QAction) :
	"""Display using a specified mode.
	"""
	def __init__ (self, scene, mode, txt, parent) :
		QAction.__init__(self,txt,parent)
		self._scene = scene
		self._mode = mode
		self.setCheckable(True)
		self.setChecked(scene.display_mode() == mode)
		self.setIcon(QIcon(":image/display_%s" % txt) )
		self.connect(self,SIGNAL("triggered(bool)"),self.set_mode)
		self.connect(scene,SIGNAL("set_display_mode"),self.mode_set)
	
	def set_mode (self) :
		self._scene.set_display_mode(self._mode)
	
	def mode_set (self, mode) :
		self.setChecked(mode == self._mode)

#############################################
#
#	frame
#
#############################################
class ActionDrawFrame (QAction) :
	"""Toggle the drawing of the frame.
	"""
	def __init__ (self, scene, parent) :
		QAction.__init__(self,"draw frame",parent)
		self.setCheckable(True)
		self.setChecked(scene.draw_frame() )
		self.setIcon(QIcon(":image/draw_frame.png") )
		self.connect(self,SIGNAL("triggered(bool)"),scene.set_draw_frame)
		self.connect(scene,SIGNAL("set_draw_frame"),self.setChecked)

class ActionClearFrame (QAction) :
	"""Clear position and rotation.
	"""
	def __init__ (self, scene, parent, gui = None) :
		QAction.__init__(self,"clear frame",parent)
		self.setIcon(QIcon(":image/clear_frame.png") )
		self.connect(self,SIGNAL("triggered(bool)"),self.clear_frame)
		self._scene = scene
		self._gui = gui
	
	def clear_frame (self) :
		sc = self._scene
		old_pos = Vec(sc.position() )
		old_orientation = Quaternion(sc.orientation() )
		sc.clear_frame()
		if self._gui is not None :
			new_pos = Vec(sc.position() )
			new_orientation = Quaternion(sc.orientation() )
			if new_pos != old_pos \
			   or new_orientation != old_orientation :
				undo = UndoFrameManipulation(sc,old_pos,new_pos,
				                             old_orientation,new_orientation)
				self._gui.emit("undo command",undo)

#############################################
#
#	selection tools
#
#############################################
class UndoSelectionChange (QUndoCommand) :
	"""Undo redo a change in the content of
	scene selection.
	"""
	def __init__ (self, scene, old_selection, new_selection) :
		QUndoCommand.__init__(self,"selection change")
		self._scene = scene
		self._old_selection = old_selection
		self._new_selection = new_selection
	
	def undo (self) :
		self._scene.set_selection(self._old_selection)
	
	def redo (self) :
		self._scene.set_selection(self._new_selection)

class SelectOneTool (SelectTool) :
	"""Select a unique element in a scene.
	"""
	def __init__ (self, scene, parent, gui = None) :
		"""Initialize the tool.
		"""
		SelectTool.__init__(self,
		                    parent,
		                    "select",
		                    scene.selection_draw)
		self.setIcon(QIcon(":image/select_one.png") )
		self._scene = scene
		self._gui = gui
	
	def post_selection (self, elmid) :
		sc = self._scene
		
		#find object id
		if sc.idmode == GLRenderer.ShapeId \
		   and elmid is not None :
			try :
				shp = sc.find(elmid)
				elmid = shp.getSceneObjectId()
			except IndexError :
				print "bad id %s" % str(elmid)
				elmid = None
		
		#change selection
		old_selection = set(sc.selection() )
		if elmid is None :
			sc.clear_selection()
		else :
			sc.set_selection([elmid])
		new_selection = set(sc.selection() )
		
		#undo
		if self._gui is not None \
		    and old_selection != new_selection :
			self._gui.emit("undo command",
			                UndoSelectionChange(sc,
			                                    old_selection,
			                                    new_selection) )

class SelectAddTool (SelectTool) :
	"""append a unique element from a scene in the selection.
	"""
	def __init__ (self, scene, parent, gui = None) :
		"""Initialize the tool.
		"""
		SelectTool.__init__(self,
		                    parent,
		                    "select+",
		                    scene.selection_draw)
		self.setIcon(QIcon(":image/select_add.png") )
		self._scene = scene
		self._gui = gui
	
	def post_selection (self, elmid) :
		sc = self._scene
		
		#find scene object id
		if sc.idmode == GLRenderer.ShapeId \
		   and elmid is not None :
			try :
				shp = sc.find(elmid)
				elmid = shp.getSceneObjectId()
			except IndexError :
				print "bad id %s" % str(elmid)
				elmid = None
		
		if elmid is not None :
			#change selection
			old_selection = set(sc.selection() )
			if elmid not in old_selection :
				selection = sc.selection()
				selection.add(elmid)
				sc.set_selection(selection)
				new_selection = set(sc.selection() )
				
				#undo
				if self._gui is not None :
					self._gui.emit("undo command",
					                UndoSelectionChange(sc,
					                                    old_selection,
					                                    new_selection) )

class SelectRemoveTool (SelectTool) :
	"""remove a unique element from a scene in the selection.
	"""
	def __init__ (self, scene, parent, gui = None) :
		"""Initialize the tool.
		"""
		SelectTool.__init__(self,
		                    parent,
		                    "select-",
		                    scene.selection_draw)
		self.setIcon(QIcon(":image/select_remove.png") )
		self._scene = scene
		self._gui = gui
	
	def post_selection (self, elmid) :
		sc = self._scene
		
		#find scene object id
		if sc.idmode == GLRenderer.ShapeId \
		   and elmid is not None :
			try :
				shp = sc.find(elmid)
				elmid = shp.getSceneObjectId()
			except IndexError :
				print "bad id %s" % str(elmid)
				elmid = None
		
		if elmid is not None :
			#change selection
			old_selection = set(self._scene.selection() )
			if elmid in old_selection :
				selection = self._scene.selection()
				selection.discard(elmid)
				self._scene.set_selection(selection)
				new_selection = set(self._scene.selection() )
				
				#undo
				if self._gui is not None :
					self._gui.emit("undo command",
					                UndoSelectionChange(self._scene,
					                                    old_selection,
					                                    new_selection) )

#############################################
#
#	GUI
#
#############################################
class SceneGUI (ElmGUI) :
	"""GUI for a (framed) PlantGL scene.
	"""
	def __init__ (self, scene) :
		ElmGUI.__init__(self)
		self._scene = scene
	
	###############################################################
	#
	#		IInteractive
	#
	###############################################################
	def setup_ui (self) :
		if ElmGUI.setup_ui(self) :
			scene = self._scene
			
			self._action_bar = QToolBar("scene actions")
			self._tool_bar = QToolBar("scene tools")
			self._menu = QMenu("Scene")
			#actions
			self._action_load_scene = ActionLoadScene(scene,self._action_bar)
			self._action_bar.addAction(self._action_load_scene)
			self._menu.addAction(self._action_load_scene)
			
			self._action_save_scene = ActionSaveScene(scene,self._action_bar)
			self._action_bar.addAction(self._action_save_scene)
			self._menu.addAction(self._action_save_scene)
			
			self._actions_display_mode = []
			self._action_bar.addSeparator()
			menu = self._menu.addMenu("Display")
			for mode,txt in [(scene.DISPLAY.SOLID,"solid"),
			                 (scene.DISPLAY.WIREFRAME,"wireframe"),
			                 (scene.DISPLAY.BOTH,"both")] :
				action = ActionDisplayMode(scene,mode,txt,self._action_bar)
				self._actions_display_mode.append(action)
				self._action_bar.addAction(action)
				menu.addAction(action)
			
			self._action_bar.addSeparator()
			menu = self._menu.addMenu("Frame")
			self._action_draw_frame = ActionDrawFrame(scene,self._action_bar)
			self._action_bar.addAction(self._action_draw_frame)
			menu.addAction(self._action_draw_frame)
			
			self._action_clear_frame = ActionClearFrame(scene,self._action_bar,self)
			self._action_bar.addAction(self._action_clear_frame)
			menu.addAction(self._action_clear_frame)
			
			#tools
			self._tool_select_one = SelectOneTool(scene,self._tool_bar,self)
			self._tool_bar.addAction(self._tool_select_one)
			
			self._tool_select_add = SelectAddTool(scene,self._tool_bar,self)
			self._tool_bar.addAction(self._tool_select_add)
			
			self._tool_select_remove = SelectRemoveTool(scene,self._tool_bar,self)
			self._tool_bar.addAction(self._tool_select_remove)
			
			if scene.frame() is None :
				self._frame_manipulator = None
				QObject.connect(scene,SIGNAL("set_frame"),self.frame_added)
			else :
				self.create_manipulator(scene)
			
			return True
		else :
			return False
	
	############################################
	#
	#	frame
	#
	############################################
	def create_manipulator (self, scene) :
		self._frame_manipulator = FrameManipulator(scene,scene,"frame manip",self)
		self._frame_manipulator.tooltype = "frame"
		self._frame_manipulator.setIcon(QIcon(":image/manip.png") )
		self._tool_bar.insertAction(self._tool_select_one,self._frame_manipulator)
		self._tool_bar.insertSeparator(self._tool_select_one)
	
	def frame_added (self, frame) :
		self.create_manipulator(self._scene)
		main_window = self.installed()
		if main_window is not None :
			main_window.addToolBar(Qt.LeftToolBarArea,self._tool_bar)
			main_window.add_tool(self._frame_manipulator)
	
	############################################
	#
	#	GUI install
	#
	############################################
	def install (self, main_window) :
		ElmGUI.install(self,main_window)
		main_window.menuBar().addMenu(self._menu)
		self.add_action_bar(main_window,self._action_bar)
		self.add_tool_bar(main_window,self._tool_bar)
	
	def uninstall (self, main_window) :
		ElmGUI.uninstall(self,main_window)
		main_window.menuBar().removeAction(self._menu.menuAction() )
		self.remove_bar(main_window,self._action_bar)
		self.remove_bar(main_window,self._tool_bar)
