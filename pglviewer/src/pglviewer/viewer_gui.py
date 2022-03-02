from PyQt4.QtCore import Qt, SIGNAL, QObject
from PyQt4.QtGui import QAction, QToolBar, QMenu, QIcon
from elm_gui import ElmGUI
from pyshell import ActionDisplayShell
import pglviewer_rc

class ViewerGUI (ElmGUI) :
	"""Some standard GUI for the viewer.
	"""
	def __init__ (self, local_variables = {}) :
		ElmGUI.__init__(self)
		self._locals = local_variables

		self._mem_tool = None
	
	def setup_ui (self) :
		if ElmGUI.setup_ui(self) :
			self._action_bar = QToolBar("viewer")
			self._tool_bar = QToolBar("viewer tools")
			self._menu = QMenu("Viewer")
			#shell
			self._display_shell = ActionDisplayShell(self._locals,self._action_bar)
			self._action_bar.addAction(self._display_shell)
			self._menu.addAction(self._display_shell)
			#persistence
			self._menu.addSeparator()
			self._action_save_state = self._menu.addAction("save state")
			self._action_save_state.setShortcut("F2")
			self._action_restore_state = self._menu.addAction("restore state")
			self._action_restore_state.setShortcut("F3")
			#close
			self._menu.addSeparator()
			self._action_close = self._menu.addAction("close")
			self._action_close.setShortcut("Ctrl+W")
			
			#view manip
			self._ac_view_manip = self._tool_bar.addAction("manip")
			self._ac_view_manip.setIcon(QIcon(":image/manip.png") )
			self._ac_view_manip.setShortcut(" ")
			self._ac_view_manip.setCheckable(True)
			self._ac_view_manip.setChecked(True)
			
			QObject.connect(self._ac_view_manip,
			                SIGNAL("triggered(bool)"),
			                self.activate_manipulator)
			
			return True
		else :
			return False
	
	def install (self, main_window) :
		ElmGUI.install(self,main_window)
		#connect
		QObject.connect(self._action_close,
		                SIGNAL("triggered(bool)"),
		                main_window.close)
		QObject.connect(self._action_save_state,
		                SIGNAL("triggered(bool)"),
		                main_window.save_state)
		QObject.connect(self._action_restore_state,
		                SIGNAL("triggered(bool)"),
		                main_window.restore_state)
		
		QObject.connect(main_window._tools_group,
		                SIGNAL("triggered(QAction *)"),
		                self.change_tool)
		
		self._display_shell.register(main_window)
		#install
		main_window.menuBar().addMenu(self._menu)
		self.add_action_bar(main_window, self._action_bar)
		self.add_tool_bar(main_window, self._tool_bar)
	
	def uninstall (self, main_window) :
		ElmGUI.uninstall(self,main_window)
		#disconnect
		QObject.disconnect(self._action_close,
		                   SIGNAL("triggered(bool)"),
		                   main_window.close)
		QObject.disconnect(self._action_save_state,
		                   SIGNAL("triggered(bool)"),
		                   main_window.save_state)
		QObject.disconnect(self._action_restore_state,
		                   SIGNAL("triggered(bool)"),
		                   main_window.restore_state)
		
		QObject.disconnect(main_window._tools_group,
		                   SIGNAL("triggered(QAction *)"),
		                   self.change_tool)
		
		self._display_shell.discard(main_window)
		#uninstall
		main_window.menuBar().removeAction(self._menu.menuAction() )
		self.remove_bar(main_window,self._action_bar)
		self.remove_bar(main_window,self._tool_bar)
	
	def change_tool (self, tool) :
		if self._ac_view_manip.isChecked() :
			self._ac_view_manip.setChecked(False)
	
	def activate_manipulator (self, state) :
		mw = self.installed()
		if mw is None :
			return
		
		if state :
			ac = mw._tools_group.checkedAction()
			if ac is None :
				self._mem_tool = None
			else :
				self._mem_tool = ac
				ac.setChecked(False)
				mw.view().set_tool(None)
		else :
			if self._mem_tool is None :
				self._ac_view_manip.setChecked(True)
			else :
				tool = self._mem_tool
				self._mem_tool = None
				tool.trigger()

















