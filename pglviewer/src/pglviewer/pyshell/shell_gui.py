from PyQt4.QtCore import Qt,SIGNAL,QPoint
from PyQt4.QtGui import QAction,QApplication,QIcon
try :
	from scishell import SciShell as Shell
except ImportError :
	from shell import PyCutExt as Shell
import pyshell_rc

class MessagedShell (Shell) :
	"""Subclass of shell that send relevant signals.
	"""
	def __init__ (self, local_variables) :
		"""Create a shell.
		"""
		Shell.__init__(self, local_variables)
		self.setMinimumSize(600,500)
		self._last_position = None
	
	def setVisible (self, visible) :
		if visible :
			if self._last_position is not None :
				self.move(self._last_position)
		Shell.setVisible(self,visible)
	
	def closeEvent (self, event) :
		self.emit(SIGNAL("closed") )
		Shell.closeEvent(self,event)
	
	def moveEvent (self, event) :
		Shell.moveEvent(self,event)
		if self.isVisible() :
			self._last_position = QPoint(self.pos() )
	
	def keyPressEvent (self, event) :
		if event.key() == Qt.Key_Escape :
			event.setAccepted(True)
		else :
			Shell.keyPressEvent(self,event)
	
	def keyReleaseEvent (self, event) :
		if event.key() == Qt.Key_Escape :
			event.setAccepted(True)
			self.close()
		else :
			Shell.keyReleaseEvent(self,event)

class ActionDisplayShell (QAction) :
	"""Action that display a python shell.
	"""
	def __init__ (self, local_variables, parent) :
		QAction.__init__(self,"display shell",parent)
		self.setCheckable(True)
		self.setIcon(QIcon(":image/shell.png") )
		self._shell = MessagedShell(local_variables)
		
		self.connect(self,SIGNAL("triggered(bool)"),self.set_visible)
		self.connect(self._shell,SIGNAL("closed"),self.shell_closed)
	
	def register (self, main_window) :
		main_window.register_window(self._shell)
		self._main_window = main_window
	
	def discard (self, main_window) :
		main_window.discard_window(self._shell)
		self._main_window = None
	
	def set_visible (self, visible) :#TODO find the complete size of main_window
		if self._shell._last_position is None :
			main_window = self._main_window
			#geometry handler
			desktop = QApplication.instance().desktop()
			#try to put it on the side
			if desktop.width() - main_window.width() > 600 :
				#put it on the right
				if desktop.width() - main_window.width() - main_window.x() > 600 :
					pos = QPoint(main_window.x() + main_window.width(),main_window.y() )
				#put it on the left
				else :
					pos = QPoint(main_window.x() - 600,main_window.y() )
			#try to put it above or below
			elif desktop.height() - main_window.height() > 500 :
				#put it below
				if desktop.height() - main_window.height() - main_window.y() > 500 :
					pos = QPoint(main_window.x(),main_window.y() + main_window.height() )
				#put it above
				else :
					pos = QPoint(main_window.x(),main_window.y() - 500)
			#put it on (0,0)
			else :
				pos = QPoint(0,0)
			
			self._shell.move(pos)
		
		self._shell.setVisible(visible)
	
	def shell_closed (self) :
		self.setChecked(False)


