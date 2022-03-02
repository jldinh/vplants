from PyQt4.QtCore import Qt,SIGNAL
from PyQt4.QtGui import QAction,QUndoCommand
from PyQGLViewer import ManipulatedFrame,Vec,Quaternion

class MouseTool (QAction) :
	"""A minimalist implementation of a tool
	that does nothing.
	"""
	def __init__ (self, parent, txt="tool") :
		QAction.__init__(self,txt,parent)
		self.tooltype = None
		self._running = False
		self.setCheckable(True)
	
	def start (self, view) :
		"""Start tool.
		"""
		self._running = True
	
	def stop (self, view) :
		"""Stop tool.
		"""
		self._running = False
	
	def running (self) :
		"""Tells wether this tool is currently activated.
		"""
		return self._running
	
	def mousePressEvent (self, view, event) :
		"""Reimplement for specific behaviour.
		"""
		pass
	
	def mouseMoveEvent (self, view, event) :
		"""Reimplement for specific behaviour.
		"""
		pass
	
	def mouseReleaseEvent (self, view, event) :
		"""Reimplement for specific behaviour.
		"""
		pass
	
	def mouseDoubleClickEvent (self, view, event) :
		"""Reimplement for specific behaviour.
		"""
		pass
	
	def wheelEvent (self, view, event) :
		"""Reimplement for specific behaviour.
		"""
		pass
	
class SelectTool (MouseTool) :
	"""Allow to select an item by clicking inside a view
	must be subclassed to provide a draw_with_names function
	when activated, generate an 'elm selected' event with
	the id of the clicked element.
	"""
	def __init__ (self, parent, txt, draw_func) :
		MouseTool.__init__(self,parent,txt)
		self._draw_func = draw_func
	
	def start (self, view) :
		MouseTool.start(self,view)
		view.set_select_functions(self.draw_with_names,
		                          self._post_selection)
	
	def stop (self, view) :
		MouseTool.stop(self,view)
		view.clear_select_functions()
	
	def draw_with_names (self, view) :
		self._draw_func(view)
	
	def _post_selection (self, view, point) :
		ind = view.selectedName()
		if ind == -1 :
			ind = None
		self.post_selection(ind)
	
	def post_selection (self, ind) :
		self.emit(SIGNAL("elm selected"),ind)
	
	def mousePressEvent (self, view, event) :
		self._moved = False
	
	def mouseMoveEvent (self, view, event) :
		self._moved = True
	
	def mouseReleaseEvent (self, view, event) :
		if self._moved :
			self._moved = False
		else :
			view.select(event.pos() )
			view.update()

class UndoFrameManipulation (QUndoCommand) :
	"""Undo redo frame manipulation.
	"""
	def __init__ (self, frame, old_pos, new_pos, old_orientation, new_orientation) :
		QUndoCommand.__init__(self,"frame changed")
		self._frame = frame
		self._old_pos = old_pos
		self._new_pos = new_pos
		self._old_orientation = old_orientation
		self._new_orientation = new_orientation
	
	def undo (self) :
		self._frame.setPosition(self._old_pos)
		self._frame.setOrientation(self._old_orientation)
	
	def redo (self) :
		self._frame.setPosition(self._new_pos)
		self._frame.setOrientation(self._new_orientation)

class FrameManipulator (MouseTool) :
	"""Manipulate a frame using the mouse.
	"""
	def __init__ (self, frame, parent, txt, gui = None) :
		MouseTool.__init__(self,parent,txt)
		tooltype = "frame"
		#self.setIcon(QIcon(":/images/icons/emacs.png"))
		self._frame = frame
		self._view = None
		self._gui = gui
	
	def frame (self) :
		return self._frame
	
	def set_frame (self, frame) :
		running = self.running()
		if running :
			self.stop(self._view)
		self._frame = frame
		if running :
			self.start(self._view)
	
	def manipulated_frame (self) :
		if self._view is None :
			return None
		else :
			return self._view.manipulatedFrame()
	
	def register_frame (self) :
		frame = self.frame()
		if frame is not None :
			self._old_pos = Vec(frame.position() )
			self._old_orientation = Quaternion(frame.orientation() )
	
	def start (self, view) :
		MouseTool.start(self,view)
		self._view = view
		
		frame = self._frame
		if frame is not None :
			manip = ManipulatedFrame()
			manip.setConstraint(frame.constraint() )
			
			self.connect(frame,SIGNAL("set_position"),self.position_set)
			self.connect(frame,SIGNAL("set_orientation"),self.orientation_set)
			self.connect(frame,SIGNAL("set_reference_frame"),self.frame_updated)
			
			view.setManipulatedFrame(manip)
			self.frame_updated()
	
	def stop (self, view) :
		MouseTool.stop(self,view)
		
		frame = self._frame
		if frame is not None :
			view.setManipulatedFrame(None)
			
			self.disconnect(frame,SIGNAL("set_position"),self.position_set)
			self.disconnect(frame,SIGNAL("set_orientation"),self.orientation_set)
			self.disconnect(frame,SIGNAL("set_reference_frame"),self.frame_updated)
		
		self._view = None
	
	def position_set (self) :
		frame = self.frame()
		manip = self.manipulated_frame()
		
		manip.setPosition(frame.position() )
	
	def orientation_set (self) :
		frame = self.frame()
		manip = self.manipulated_frame()
		
		manip.setOrientation(frame.orientation() )
	
	def frame_updated (self) :
		frame = self.frame()
		manip = self.manipulated_frame()
		
		manip.setPosition(frame.position() )
		manip.setOrientation(frame.orientation() )
	
	def update_frame (self, view) :
		frame = self.frame()
		manip = self.manipulated_frame()
		if frame is not None and manip is not None :
			frame.setPosition(manip.position() )
			frame.setOrientation(manip.orientation() )
	
	def mousePressEvent (self, view, event) :
		self.register_frame()
	
	def mouseMoveEvent (self, view, event) :
		self.update_frame(view)
		view.update()
	
	def mouseReleaseEvent (self, view, event) :
		self.update_frame(view)
		view.update()
		if self._gui is not None and self.frame() is not None :
			undo = UndoFrameManipulation(self.frame(),
			                             self._old_pos,
			                             Vec(self.frame().position() ),
			                             self._old_orientation,
			                             Quaternion(self.frame().orientation() ) )
			self._gui.emit("undo command",undo)
	
	def wheelEvent (self, view, event) :
		self.update_frame(view)
		view.update()

