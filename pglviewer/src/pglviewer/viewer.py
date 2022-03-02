from os.path import expanduser,splitext
from pickle import dump,load
from PyQt4.QtCore import Qt,SIGNAL,QSize
from PyQt4.QtGui import QMainWindow,QActionGroup,QDesktopWidget
from openalea.container import IdDict
from view3d import View3D
from persistence import save_state,restore_state

class Viewer (QMainWindow) :
	"""A high level object to manage GUI around
	a 3D view
	"""
	def __init__ (self, parent = None) :
		QMainWindow.__init__(self, parent)
		self.setWindowTitle("viewer")
		
		#attributes
		self._view = View3D()
		self.setCentralWidget(self._view)
		self.connect(self._view,SIGNAL("echap pressed"),self.close_window)
		self.connect(self._view,SIGNAL("update"),self.view_updated)
		
		self._registered_gui = IdDict()
		self._registered_windows = set()
		self._associated_viewers = set()
		
		#tool
		self._current_tooltype = None
		self._tools_group = QActionGroup(self)
		self.connect(self._tools_group,
		             SIGNAL("triggered(QAction *)"),
		             self.change_tool)
		
		#find widget and icon size
		desktop = QDesktopWidget()
		rect = desktop.availableGeometry(self)
		size = min(rect.width(),rect.height() )
		if size < 1000 :
			iconsize = QSize(16,16)
		else :
			iconsize = QSize(48,48)
		self.setIconSize(iconsize)
		if parent is None :
			self.setGeometry(10,30,rect.width() / 2,rect.height() / 2)
	
	def showEvent (self, event) :
		#show associated viewers
		for viewer in self._associated_viewers :
			viewer.show()
		
		#show self
		QMainWindow.showEvent(self,event)
	
	def closeEvent (self, event) :
		self._view.clear()
		for window in self._registered_windows :
			window.close()
		for viewer in self._associated_viewers :
			viewer.close()
		for gui_id in tuple(self._registered_gui.iterkeys() ) :
			self.remove_gui(gui_id)
		self.emit(SIGNAL("close") )
		QMainWindow.closeEvent(self,event)
	
	def close_window (self) :
		self.window().close()
	
	def debug (self, *args) :
		print "debug",args
	
	def __del__ (self) :
		print "del viewer"
		#self.close()
	
	def view (self) :
		return self._view
	
	def view_updated (self, *args) :
		#associated viewers
		for viewer in self._associated_viewers :
			viewer.view()._update()
	
	def update_view (self, *args) :
		self.view().update()
		#associated viewers
		for viewer in self._associated_viewers :
			viewer.view().update()
	
	def register_window (self, window) :
		"""Add a new window to the list of managed windows.
		"""
		self._registered_windows.add(window)
	
	def discard_window (self, window) :
		"""Discard a window from the list of managed windows.
		"""
		self._registered_windows.discard(window)
	
	def synchronize (self, another_viewer) :
		"""Synchronize the display of this viewer
		with another_viewer
		"""
		self._associated_viewers.add(another_viewer)
		#another_viewer._associated_viewers.append(self)
	
	def desynchronize (self, another_viewer) :
		"""Remove the link between two viewers.
		"""
		#another_viewer._associated_viewers.remove(self)
		self._associated_viewers.discard(another_viewer)
	
	###############################################################
	#
	#		User interface
	#
	###############################################################
	def add_gui (self, gui) :
		"""Add a new gui to the viewer.
		Return an id to further access this gui
		"""
		gui.setup_ui()
		gui.install(self)
		return self._registered_gui.add(gui)
	
	def remove_gui (self, gui_id) :
		"""Remove a gui from the viewer
		
		gui_id: id of gui as given by add_gui
		"""
		gui = self._registered_gui.pop(gui_id)
		gui.clean()
		gui.uninstall(self)
		return gui
	
	def clear_guis (self) :
		"""Clear every GUI in the viewer
		"""
		self.change_tool(None)
		for gui_id in tuple(self._registered_gui) :
			self.remove_gui(gui_id)
	
	##########################################
	#
	#		world
	#
	##########################################
	def set_world (self, world) :
		view = self.view()
		view.clear()
		if world is not None :
			view.set_world(world)
			view.update()
	
	def add_world (self, world) :
		self.view().add_world(world)
	
	def remove_world (self, world) :
		self.view().remove_world(world)
	
	def clear_worlds (self) :
		"""Clear every world in the viewer
		"""
		self.view().clear()
	
	##########################################
	#
	#		tools
	#
	##########################################
	def start_tool (self, tool) :
		view = self.view()
		tool.start(view)
		view.set_tool(tool)
	
	def stop_tool (self, tool) :
		view = self.view()
		tool.stop(view)
		view.set_tool(None)
	
	def change_tool (self, tool) :
		view = self.view()
		if view.tool() is not None :
			self.stop_tool(view.tool() )
		if tool is not None :
			self.start_tool(tool)
	
	def add_tool (self, tool) :
		self._tools_group.addAction(tool)
		if (self._current_tooltype is not None \
			and self._current_tooltype==tool.tooltype) \
			or tool.isChecked() :
				self.change_tool(tool)
				tool.setChecked(True)
				self._current_tooltype = None
	
	def remove_tool (self, tool) :
		if tool == self.view().tool() :
			self.change_tool(None)
			self._current_tooltype = tool.tooltype
		self._tools_group.removeAction(tool)
	##########################################
	#
	#		clear
	#
	##########################################
	def clear (self) :
		"""Clear everything in the viewer
		"""
		self.clear_guis()
		self.clear_worlds()
	
	##########################################
	#
	#		persistence
	#
	##########################################
	def save_state (self) :
		state = save_state(self)
		dump(state,open(expanduser("~/.pglviewer.cfg"),'w') )
	
	def restore_state (self) :
		try :
			state = load(open(expanduser("~/.pglviewer.cfg"),'rb') )
			print state
			restore_state(self,state)
		except IOError :
			print "no available stored state"
	
	##########################################
	#
	#		persistence
	#
	##########################################
	def saveSnapshot (self, imname) :
		"""Save a snapshot of current view
		"""
		self.view().setSnapshotFormat(splitext(imname)[1][1:].upper() )
		self.view().saveSnapshot(imname)
	
