from PyQt4.QtCore import Qt,SIGNAL
from PyQt4.QtGui import QAction,QIcon,QToolBar,QMenu
from PyQGLViewer import ManipulatedFrame,Vec
from ..elm_gui import ElmGUI
from ..elm_tools import FrameManipulator

import probe_rc

#############################################
#
#	visible
#
#############################################
class ActionProbeVisible (QAction) :
	"""Action to change the visibility of a probe.
	"""
	def __init__ (self, probe) :
		QAction.__init__(self,"visible",probe)
		self.setCheckable(True)
		self.setChecked(probe.visible() )
		self.setIcon(QIcon(":image/visible.png") )
		self.connect(self,SIGNAL("triggered(bool)"),probe.set_visible)
		self.connect(probe,SIGNAL("set_visible"),self.setChecked)

#############################################
#
#	activation
#
#############################################
class ActionProbeActivate (QAction) :
	"""Action to change the activation of a probe.
	"""
	def __init__ (self, probe) :
		QAction.__init__(self,"activate",probe)
		self._view = None
		self._probe = probe
		self.setCheckable(True)
		self.setChecked(probe.activated() )
		self.setShortcut("Ctrl+H")
		self.setIcon(QIcon(":image/activate.png") )
		self.connect(self,SIGNAL("triggered(bool)"),self.activate)
		self.connect(probe,SIGNAL("activate"),self.setChecked)
	
	def set_view (self, view) :
		self._view = view
	
	def activate (self, state) :
		self._probe.activate(self._view,state)

#############################################
#
#	change view
#
#############################################
class ActionStraightenView (QAction) :
	"""Align the view with the probe orientation.
	"""
	def __init__ (self, probe) :
		QAction.__init__(self,"straighten view",probe)
		self._view = None
		self._probe = probe
		#self.setShortcut("Ctrl+F")
		self.setIcon(QIcon(":image/straighten_view.png") )
		self.connect(self,SIGNAL("triggered(bool)"),self.straighten_view)
	
	def set_view (self, view) :
		self._view = view
	
	def straighten_view (self) :
		probe = self._probe
		cam = self._view.camera()
		
		R = (probe.position() - cam.position() ).norm()
		vert = probe.normal()
		cam.setPosition(probe.position() + vert * R)
		cam.setViewDirection(-vert)
		vert = probe.vertical()
		if vert is not None :
			cam.setUpVector(vert,False)
		probe.emit(SIGNAL("update") )

class ActionSideView (QAction) :
	"""Align the view perpendicularly with the probe orientation.
	"""
	def __init__ (self, probe) :
		QAction.__init__(self,"side view",probe)
		self._view = None
		self._probe = probe
		#self.setShortcut("Ctrl+F")
		self.setIcon(QIcon(":image/side_view.png") )
		self.connect(self,SIGNAL("triggered(bool)"),self.side_view)
	
	def set_view (self, view) :
		self._view = view
	
	def side_view (self) :
		probe = self._probe
		cam = self._view.camera()
		
		R = (probe.position() - cam.position() ).norm()
		N = probe.normal()
		vert = probe.vertical()
		if vert is not None :
			ori = vert ^ N
			cam.setPosition(probe.position() + ori * R)
			cam.setViewDirection(-ori)
			cam.setUpVector(vert,False)
			probe.emit(SIGNAL("update") )

#############################################
#
#	GUI
#
#############################################
class ClippingProbeGUI (ElmGUI) :
	"""GUI for a simple clipping probe.
	"""
	def __init__ (self, probe) :
		ElmGUI.__init__(self)
		self._probe = probe
	
	###############################################################
	#
	#		IInteractive
	#
	###############################################################
	def setup_ui (self) :
		if ElmGUI.setup_ui(self) :
			probe = self._probe
			
			self._action_bar = QToolBar("probe actions")
			self._tool_bar = QToolBar("probe tools")
			self._menu = QMenu("Probe")
			#actions
			self._probe_visible = ActionProbeVisible(probe)
			self._action_bar.addAction(self._probe_visible)
			self._menu.addAction(self._probe_visible)
			
			self._probe_activate = ActionProbeActivate(probe)
			self._action_bar.addAction(self._probe_activate)
			self._menu.addAction(self._probe_activate)
			
			self._straighten_view = ActionStraightenView(probe)
			self._action_bar.addAction(self._straighten_view)
			self._menu.addAction(self._straighten_view)
			
			self._side_view = ActionSideView(probe)
			self._action_bar.addAction(self._side_view)
			self._menu.addAction(self._side_view)
			
			#tools
			self._probe_manipulator = FrameManipulator(probe,probe,"probe manip",self)
			self._probe_manipulator.tooltype = "probe"
			self._probe_manipulator.setIcon(QIcon(":image/manip.png") )
			self._tool_bar.addAction(self._probe_manipulator)
			
			return True
		else :
			return False
	
	def install (self, main_window) :
		ElmGUI.install(self,main_window)
		main_window.menuBar().addMenu(self._menu)
		self._probe_activate.set_view(main_window.view() )
		self._straighten_view.set_view(main_window.view() )
		self._side_view.set_view(main_window.view() )
		self.add_action_bar(main_window,self._action_bar)
		self.add_tool_bar(main_window,self._tool_bar,Qt.LeftToolBarArea)
	
	def uninstall (self, main_window) :
		ElmGUI.uninstall(self,main_window)
		main_window.menuBar().removeAction(self._menu.menuAction() )
		self.remove_bar(main_window,self._action_bar)
		self._probe_activate.set_view(None)
		self._straighten_view.set_view(None)
		self._side_view.set_view(None)
		self.remove_bar(main_window,self._tool_bar)

