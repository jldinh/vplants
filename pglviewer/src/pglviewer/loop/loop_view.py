from PyQt4.QtCore import SIGNAL,QCoreApplication
from ..elm_view import ElmView
from loop import Loop

class LoopView (ElmView) :
	"""Call a set of tasks at regular time interval
	"""
	def __init__ (self, scheduler_or_loop, init_func = None) :
		"""Constructor
		
		.. warning:: for this object to works fine,
		   especially with `reinit` method, tasks
		   must be registered in the scheduler prior
		   to construct this object
		
		:Parameters:
		 - `scheduler_or_loop` (Scheduler) - a scheduler
		    to manage each step or a loop object
		 - `init_func` (function) - a function
		        that take no arguments and will be 
		        called at each reinitialisation
		        (including this constructor)
		"""
		ElmView.__init__(self,"task")
		if isinstance(scheduler_or_loop,Loop):
			self._loop = scheduler_or_loop
			if init_func:
				self._loop.add_init_processing(init_func)
			self._loop.add_post_step_processing(self.emit_step)
		else:
			self._loop = Loop(scheduler_or_loop,self.emit_step,init_func)
	
	def emit_step (self) :
		self.emit(SIGNAL("step"),self._loop.current_step() )
		QCoreApplication.processEvents()
	
	def tasks (self) :
		for task in self._loop._scheduler.tasks() :
			yield task
	
	###############################################
	#
	#    loop interface
	#
	###############################################
	def running (self) :
		return self._loop.running()
	
	def current_step (self) :
		return self._loop.current_step()
	
	def reinit (self) :
		self.emit(SIGNAL("reinit") )
		return self._loop.reinit()
	
	def step (self) :
		return self._loop.step()
	
	def play (self) :
		self._loop.play()
		self.emit(SIGNAL("play") )
	
	def pause (self) :
		self._loop.pause()
		self.emit(SIGNAL("pause") )

