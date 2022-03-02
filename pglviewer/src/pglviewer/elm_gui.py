from PyQt4.QtCore import Qt,SIGNAL
from PyQt4.QtGui import QAction,QToolBar,QIcon
from elm_tools import MouseTool,SelectTool

class ElmGUI (object) :
	"""an empty implementation of a GUI that do nothing
	"""
	def __init__ (self) :
		"""initialize the GUI.
		"""
		self._created = False
		self._installed = None
	
	###########################################
	#
	#		GUI interface
	#
	###########################################
	def setup_ui (self) :
		"""Create all GUI components.
		
		return True if components need to be created
		"""
		if self._created :
			#do nothing, this method has already been called
			return False
		else :
			self._created = True
			return True
	
	def clean (self) :
		"""Clean the gui if needed.
		"""
		pass
	
	def installed (self) :
		"""Return the viewer in which this gui
		is currently installed or None if
		the gui is not installed
		"""
		return self._installed
	
	def install (self, main_window) :
		"""Install all GUI components in the main window.
		"""
		self._installed = main_window
	
	def uninstall (self, main_window) :
		"""Uninstall all GUI components from the main window.
		"""
		self._installed = None
	
	def emit (self, signal, args) :
		"""Force the viewer to emit a signal.
		If the GUI is not installed do nothing.
		"""
		mw = self.installed()
		if mw is not None :
			mw.emit(SIGNAL(signal),args)
	
	###########################################
	#
	#		help functions to install GUI elements
	#
	###########################################
	def add_action_bar (self, main_window, bar) :
		"""Add a toolbar that contains actions.
		"""
		main_window.addToolBar(bar)
		bar.show()
	
	def add_tool_bar (self, main_window,
	                        bar,
	                        bar_position =  Qt.LeftToolBarArea) :
		"""Add a toolbar that contains tools.
		"""
		main_window.addToolBar(bar_position,bar)
		bar.show()
		for action in bar.actions() :
			if isinstance(action,MouseTool) :
				main_window.add_tool(action)
	
	def remove_bar (self, main_window, bar) :
		"""Remove a toolbar from viewer
		either containing tools or actions.
		"""
		main_window.removeToolBar(bar)
		bar.setParent(None)
		for action in bar.actions() :
			if isinstance(action,MouseTool) :
				main_window.remove_tool(action)
	
	def add_status_widget (self, main_window, widget, is_permanent = True) :
		"""Add a widget in the status bar.
		"""
		if is_permanent :
			main_window.statusBar().addPermanentWidget(widget)
		else :
			main_window.statusBar().addWidget(widget)
		widget.show()
	
	def remove_status_widget (self, main_window, widget) :
		"""Remove a widget from the status bar.
		
		As soon as there is no more visible widgets,
		remove the status bar.
		"""
		status = main_window.statusBar()
		status.removeWidget(widget)
		widget.setParent(None)
		if len(status.children() ) == 2 :
			main_window.setStatusBar(None)

class TemplateGUI (ElmGUI) :
	"""A custom class to interactively add elements to a GUI.
	"""
	def __init__ (self, name) :
		ElmGUI.__init__(self)
		self._name = name
		self._action_bar = None
		self._actions = []
		self._tool_bar = None
		self._tools = []
		self._tool_bar_position = Qt.LeftToolBarArea
	
	###############################################
	#
	#		access to attributes
	#
	###############################################
	def set_tools_position (self, position) :
		"""Set the position of the toolbar.
		
		position: a string, either 'left' or 'bottom'.
		"""
		if position == "left" :
			self._tool_bar_position = Qt.LeftToolBarArea
		elif position == "bottom" :
			self._tool_bar_position = Qt.BottomToolBarArea
		else :
			raise UserWarning("position '%s' not recognized (either left or bottom)" % str(position) )
	
	def create_action (self, name, func, icon, descr) :
		"""Create an action from its description.
		assert action_bar is not None.
		"""
		action = self._action_bar.addAction(name)
		if icon is not None :
			if isinstance(icon,QIcon) :
				action.setIcon(icon)
			else :
				action.setIcon(QIcon(icon) )
		if descr == "" :
			action.setToolTip(name)
		else :
			action.setToolTip(descr)
		action.connect(action,SIGNAL("triggered(bool)"),func)
		return action
		
	def add_action_descr (self, name, func, icon = None, descr = "") :
		"""Add a new action from its description.
		"""
		if self._action_bar is None :
			self._actions.append( (name,func,icon,descr) )
		else :
			self._actions.append(self.create_action(name,func,icon,descr) )
	
	def add_action (self, action) :
		"""Add a new action to the GUI.
		"""
		self._actions.append(action)
		if self._action_bar is not None :
			self._action_bar.addAction(action)
	
	def create_tool (self, name, func, draw_func, icon, descr) :
		"""Create a new tool from its description.
		assert tool_bar is not None.
		"""
		toolbar = self._tool_bar
		tool = SelectTool(toolbar,name,draw_func)
		toolbar.addAction(tool)
		if icon is not None :
			if isinstance(icon,QIcon) :
				tool.setIcon(icon)
			else :
				tool.setIcon(QIcon(icon) )
		if descr == "" :
			tool.setToolTip(name)
		else :
			tool.setToolTip(descr)
		
		tool.connect(tool,SIGNAL("elm selected"),func)
		return tool
	
	def add_tool_descr (self, name, func, draw_func, icon = None, descr = "") :
		"""Add a new tool from its description.
		"""
		if self._tool_bar is None :
			self._tools.append( (name,func,draw_func,icon,descr) )
		else :
			self._tools.append(self.create_tool(name,func,draw_func,icon,descr) )
	
	def add_tool (self, tool) :
		"""Add a new tool to the GUI.
		"""
		self._tools.append(tool)
		if self._tool_bar is not None :
			self._tool_bar.addAction(tool)
	
	###############################################
	#
	#		subclass ElmGUI
	#
	###############################################
	def setup_ui (self) :
		if ElmGUI.setup_ui(self) :
			self._action_bar = QToolBar("action_%s" % self._name)
			for i,action in enumerate(self._actions) :
				if not isinstance(action,QAction) :
					action = self.create_action(*action)
					self._actions[i] = action
				self._action_bar.addAction(action)
			
			self._tool_bar = QToolBar("tool_%s" % self._name)
			for i,tool in enumerate(self._tools) :
				if not isinstance(tool,QAction) :
					tool = self.create_tool(*tool)
					self._tools[i] = tool
				self._tool_bar.addAction(tool)
			
			return True
		else :
			return False
	
	def install (self, main_window) :
		ElmGUI.install(self,main_window)
		if len(self._action_bar.actions() ) > 0 :
			self.add_action_bar(main_window,self._action_bar)
		if len(self._tool_bar.actions() ) > 0 :
			self.add_tool_bar(main_window,
			                  self._tool_bar,
			                  self._tool_bar_position)
	
	def uninstall (self, main_window) :
		ElmGUI.uninstall(self,main_window)
		if len(self._action_bar.actions() ) > 0 :
			self.remove_bar(main_window,self._action_bar)
		if len(self._tool_bar.actions() ) > 0 :
			self.remove_bar(main_window,self._tool_bar)

