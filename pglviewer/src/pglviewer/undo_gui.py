from PyQt4.QtCore import Qt,SIGNAL,QObject
from PyQt4.QtGui import QUndoView,QUndoStack, \
                        QToolBar,QIcon,QDockWidget
from elm_gui import ElmGUI

import pglviewer_rc

class UndoGUI (ElmGUI) :
	"""GUI used to undo a set of operations.
	"""
	def __init__ (self) :
		"""Initialize GUI
		"""
		ElmGUI.__init__(self)
		self._undo_view = None
	
	def setup_ui (self) :
		if ElmGUI.setup_ui(self) :
			#actions
			self._action_bar = QToolBar("undo")
			
			self._undo_stack = QUndoStack()
			
			self._action_undo = self._undo_stack.createUndoAction(self._action_bar)
			self._action_undo.setIcon(QIcon(":image/undo.png") )
			self._action_bar.addAction(self._action_undo)
			
			self._action_redo = self._undo_stack.createRedoAction(self._action_bar)
			self._action_redo.setIcon(QIcon(":image/redo.png") )
			self._action_bar.addAction(self._action_redo)
			
			self._dock_widget = QDockWidget("history")
			self._undo_view = QUndoView(self._undo_stack)
			self._dock_widget.setWidget(self._undo_view)
			
			return True
		else :
			return False
	
	def clean (self) :
		ElmGUI.clean(self)
	
	def install (self, main_window) :
		ElmGUI.install(self,main_window)
		self.add_action_bar(main_window,self._action_bar)
		main_window.addDockWidget(Qt.RightDockWidgetArea,self._dock_widget)
		QObject.connect(main_window,
		                SIGNAL("undo command"),
		                self.add_undo_command)
		self._dock_widget.show()
	
	def uninstall (self, main_window) :
		ElmGUI.uninstall(self,main_window)
		self.remove_bar(main_window,self._action_bar)
		main_window.removeDockWidget(self._dock_widget)
		self._dock_widget.setParent(None)
		QObject.disconnect(main_window,
		                   SIGNAL("undo command"),
		                   self.add_undo_command)
		self._dock_widget.hide()
	
	###############################################
	#
	#	actions
	#
	###############################################
	def add_undo_command (self, cmd) :
		"""add a new undo command in the list.
		"""
		if self._undo_view is not None :
			stack = self._undo_view.stack()
			stack.push(cmd)

