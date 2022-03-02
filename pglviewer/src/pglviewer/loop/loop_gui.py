from PyQt4.QtCore import Qt,SIGNAL,QObject
from PyQt4.QtGui import QAction,QIcon,QToolBar,QMenu,QLineEdit
from ..elm_gui import ElmGUI

import loop_rc

def clone_action (ref_action, clone) :
	clone.setText(ref_action.text() )
	clone.setIcon(ref_action.icon() )
	clone.setToolTip(ref_action.toolTip() )
	clone.setShortcuts(ref_action.shortcuts() )

#############################################
#
#	GUI
#
#############################################
class LoopGUI (ElmGUI) :
	"""Simple GUI for a loop.
	"""
	def __init__ (self, loop) :
		ElmGUI.__init__(self)
		self._loop = loop
	
	###############################################################
	#
	#		IInteractive
	#
	###############################################################
	def setup_ui (self) :
		if ElmGUI.setup_ui(self) :
			loop = self._loop
			
			self._action_bar = QToolBar("loop actions")
			self._menu = QMenu("Loop")
			
			#actions
			self._reinit_loop = QAction("reinit",loop)
			self._reinit_loop.setIcon(QIcon(":image/stop.png") )
			self._action_bar.addAction(self._reinit_loop)
			QObject.connect(self._reinit_loop,
			                SIGNAL("triggered(bool)"),
			                loop.reinit)
			self._menu.addAction(self._reinit_loop)
			self._reinit_loop.setEnabled(loop._loop._init_func is not None)
			
			self._play_loop = QAction("play",loop)
			self._play_loop.setIcon(QIcon(":image/play.png") )
			self._play_loop.setShortcut("Return")
			
			self._pause_loop = QAction("pause",loop)
			self._pause_loop.setIcon(QIcon(":image/pause.png") )
			self._pause_loop.setShortcut("Return")
			
			self._toggle_running = QAction("toggle",loop)
			QObject.connect(self._toggle_running,
			                SIGNAL("triggered(bool)"),
			                self.toggle_running)
			self._action_bar.addAction(self._toggle_running)
			self._menu.addAction(self._toggle_running)
			
			self._step_loop = QAction("step",loop)
			self._step_loop.setIcon(QIcon(":image/step.png") )
			self._step_loop.setShortcut("Ctrl+Return")
			QObject.connect(self._step_loop,
			                SIGNAL("triggered(bool)"),
			                loop.step)
			self._action_bar.addAction(self._step_loop)
			self._menu.addAction(self._step_loop)
			
			self.pause()
			
			#tasks managing
			self._menu.addSeparator()
			self._menu_tasks = self._menu.addMenu("tasks")
			for task in loop.tasks() :
				ac = self._menu_tasks.addAction(task.name() )
				ac.setCheckable(True)
				ac.setChecked(task.evaluation_enabled() )
				QObject.connect(ac,
				                SIGNAL("toggled(bool)"),
				                task.enable_evaluation)
			
			self._action_bar.addAction(self._menu_tasks.menuAction() )
			
			#status bar
			self._display_current_step = QLineEdit("")
			self._display_current_step.setMaximumWidth(50)
			self._display_current_step.setAlignment(Qt.AlignRight)
			self.set_step_value(loop.current_step() )
			
			#signals
			QObject.connect(loop,
			                SIGNAL("play"),
			                self.play)
			QObject.connect(loop,
			                SIGNAL("pause"),
			                self.pause)
			QObject.connect(loop,
			                SIGNAL("reinit"),
			                self.reinit)
			QObject.connect(loop,
			                SIGNAL("step"),
			                self.set_step_value)
			
			return True
		else :
			return False
	
	def clean (self) :
		"""Make sure the loop stop before finishing.
		"""
		self._loop.pause()
	############################################
	#
	#	GUI install
	#
	############################################
	def install (self, main_window) :
		ElmGUI.install(self,main_window)
		main_window.menuBar().addMenu(self._menu)
		self.add_action_bar(main_window,self._action_bar)
		self.add_status_widget(main_window,self._display_current_step,False)
		
#		main_window.connect(self._loop,
#		                    SIGNAL("reinit"),
#		                    main_window.view().update)
#		
#		main_window.connect(self._loop,
#		                    SIGNAL("step"),
#		                    main_window.view().update)
	
	def uninstall (self, main_window) :
		ElmGUI.uninstall(self,main_window)
		main_window.menuBar().removeAction(self._menu.menuAction() )
		self.remove_bar(main_window,self._action_bar)
		self.remove_status_widget(main_window,self._display_current_step)
		
#		main_window.disconnect(self._loop,
#		                       SIGNAL("reinit"),
#		                       main_window.view().update)
#		
#		main_window.disconnect(self._loop,
#		                       SIGNAL("step"),
#		                       main_window.view().update)
	
	############################################
	#
	#	animate
	#
	############################################
	def reinit (self) :
		self.pause()
		#self._loop.reinit()
		self.set_step_value(self._loop.current_step() )
	
	def step (self) :
		self._loop.step()
	
	def toggle_running (self) :
		if self._loop.running() :
			self._loop.pause()
		else :
			self._loop.play()
	
	def play (self) :
		self._step_loop.setEnabled(False)
		clone_action(self._pause_loop,self._toggle_running)
		#self._loop.play()
	
	def pause (self) :
		#self._loop.pause()
		self._step_loop.setEnabled(True)
		clone_action(self._play_loop,self._toggle_running)
	
	############################################
	#
	#	animate
	#
	############################################
	def set_step_value (self, val) :
		self._display_current_step.setText("%d" % val)

