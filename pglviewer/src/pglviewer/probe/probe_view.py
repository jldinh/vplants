from math import pi,sqrt
import OpenGL.GL as ogl
from PyQt4.QtCore import SIGNAL
from PyQGLViewer import Vec,Quaternion
from ..elm_view import ElmView
from probe import ClippingProbe

class ProbeView (ElmView) :
	"""A generic view on clipping probes.
	"""
	def __init__ (self, world=None, size=1., name="probe") :
		ElmView.__init__(self,name)
		self._worlds = []
		if world is not None :
			self.add_world(world)
		self._size = size
		self._selected = False
		self._visible = True
	
	def clear (self) :
		for world in self.worlds() :
			self.disconnect(world,SIGNAL("update"),self.update)
		del self._worlds[:]
	
	def update (self) :
		self.emit(SIGNAL("update") )
	
	#########################################
	#
	#	accessors
	#
	#########################################
	def worlds (self) :
		"""Return the worlds managed by this probe.
		"""
		return iter(self._worlds)
	
	def add_world (self, world) :
		"""Add a new world to probe.
		"""
		self._worlds.append(world)
		self.connect(world,SIGNAL("update"),self.update)
		self.emit(SIGNAL("add_world"),world)
	
	def remove_world (self, world) :
		"""Remove a world from probing.
		"""
		try :
			self._worlds.remove(world)
			self.disconnect(world,SIGNAL("update"),self.update)
			self.emit(SIGNAL("remove_world"),world)
		except ValueError :
			raise
	
	def set_world (self, world) :
		"""Set a new single world to display.
		"""
		self.clear()
		self.add_world(world)
	
	def size (self) :
		"""Return the size of the probe.
		"""
		return self._size
	
	def set_size (self, size) :
		"""Set the size of the probe.
		#TODO
		"""
		self._size = size
	
	def selected (self) :
		"""Tells wether this probe is in a selected state.
		"""
		return self._selected
	
	def set_selected (self, state) :
		"""Put this probe in a selected state.
		"""
		self._selected = state
		self.emit(SIGNAL("set_selected"),state)
		self.emit(SIGNAL("update") )
	
	def visible (self) :
		"""Tells wether the probe is visible.
		"""
		return self._visible
	
	def set_visible (self, state) :
		"""Set the visibility of the probe.
		"""
		self._visible = state
		self.emit(SIGNAL("set_visible"),state)
		self.emit(SIGNAL("update") )
	#########################################
	#
	#	ElmView subclass
	#
	#########################################
	def bounding_box (self) :
		"""Bounding box of the world managed by the probe.
		"""
		bb_list = []
		for world in self.worlds() :
			bb = world.bounding_box()
			if bb is not None :
				bb_list.append(bb)
		
		if len(bb_list) == 0 :
			return None
		return reduce(lambda x,y: x | y,bb_list)
	
	def position (self) :
		"""Position of the world managed by the probe.
		"""
		pos_list = []
		for world in self.worlds() :
			pos = world.position()
			if pos is not None :
				pos_list.append(pos)
		
		if len(pos_list) == 0 :
			return None
		return reduce(lambda x,y: x + y,pos_list) / len(pos_list)
	
	def center (self) :
		"""Center of the world managed by the probe.
		"""
		pos_list = []
		for world in self.worlds() :
			pos = world.center()
			if pos is not None :
				pos_list.append(pos)
		
		if len(pos_list) == 0 :
			return None
		return reduce(lambda x,y: x + y,pos_list) / len(pos_list)
	
	#########################################
	#
	#	Probe geometrical informations
	#
	#########################################
	def normal (self) :
		"""
		return a vector normal to the probe
		"""
		return None
	
	def vertical (self) :
		"""
		return a vector standing for the vertical
		"""
		return None
	
	########################################################
	#
	#		persistence
	#
	########################################################
	def save_state (self, state, viewer) :
		"""Write the current state of this
		element in state.
		
		It is the user responsability to
		store in state everything needed
		to restore the state of the view.
		
		.. warning: use a well defined key
		   to store all informations about
		   this element in a submap of state.
		   Default implementation use object
		   name to store informations relative
		   to opengl attributes.
		
		.. warning: state is intented to be
		   pickled. To avoid trouble when
		   restoring state, store only basic
		   python types and not user defined
		   custom classes :)
		
		:Parameters:
		 - `state` (dict of (str,dict of (str,param) ) )
		 - `viewer` (Viewer) - actual viewer
		
		:Return: None, modify state in place
		"""
		ElmView.save_state(self,state,viewer)
		st = state[str(self.name() )]
		
		st["size"] = self.size()
		st["selected"] = self.selected()
		st["visible"] = self.visible()
		
		for world in self.worlds() :
			world.save_state(state,viewer)
	
	def restore_state (self, state, viewer) :
		"""Try to restore the state of this
		element.
		
		Use informations stored in state. If
		informations are not available do nothing.
		
		:Parameters:
		 - `state` (dict of (str,dict of (str,param) ) )
		 - `viewer` (Viewer) - actual viewer
		"""
		ElmView.restore_state(self,state,viewer)
		try :
			st = state[str(self.name() )]
			self.set_size(st["size"])
			self.set_selected(st["selected"])
			self.set_visible(st["visible"])
		except KeyError :
			print "unable to restore state for element %s (ProbeView)" % str(self.name() )
		
		for world in self.worlds() :
			world.restore_state(state,viewer)

class ClippingProbeView (ProbeView) :
	"""Implementation of ProbeView for a single clipping plane.
	"""
	def __init__ (self, world=None, probe=None, size=1., name="cprobe") :
		ProbeView.__init__(self,world,size,name)
		if probe is None :
			self._probe = ClippingProbe()
		else :
			self._probe = probe
	#########################################################
	#
	#		emulation of probe methods
	#
	#########################################################
	def constraint (self) :
		return self._probe.constraint()
	
	def position (self) :
		return self._probe.position()
	
	def setPosition (self, vec) :
		self._probe.setPosition(vec)
		self.emit(SIGNAL("set_position"),vec)
		self.emit(SIGNAL("update") )
	
	def orientation (self) :
		return self._probe.orientation()
	
	def setOrientation (self, quaternion) :
		self._probe.setOrientation(quaternion)
		self.emit(SIGNAL("set_orientation"),quaternion)
		self.emit(SIGNAL("update") )
	
	def matrix (self) :
		return self._probe.matrix()
	
	def world_matrix (self) :
		return self._probe.worldMatrix()
	
	def setReferenceFrame (self, frame) :
		self._probe.setReferenceFrame(frame)
		self.emit(SIGNAL("set_reference_frame"),frame)
		self.emit(SIGNAL("update") )
	
	def activated (self) :
		return self._probe.activated()
	
	def activate (self, view, activation) :
		self._probe.activate(view,activation)
		self.emit(SIGNAL("activate"),activation)
		self.emit(SIGNAL("update") )
	
	def start_clipping (self, view) :
		self._probe.start_clipping(view)
	
	def stop_clipping (self, view) :
		self._probe.stop_clipping(view)
	
	def normal (self) :
		"""
		return a vector normal to the probe
		"""
		return self._probe.inverseCoordinatesOf(Vec(0,0,1) ) - self.position()
	
	def vertical (self) :
		"""
		return a vector standing for the vertical
		"""
		return self._probe.inverseCoordinatesOf(Vec(0,1,0) ) - self.position()
	#########################################################
	#
	#		drawable
	#
	#########################################################
	def draw (self, view, mode) :
		ogl.glPushAttrib(ogl.GL_LIGHTING_BIT)
		ogl.glDisable(ogl.GL_LIGHTING)
		ogl.glPushMatrix()
		ogl.glMultMatrixd(self.world_matrix() )
		#selection state
		if self.selected() :
			ogl.glColor3f(0.3,0.,0.)
		else :
			ogl.glColor3f(0.8,0.8,0.8)
		#visible state
		if self.visible() :
			ogl.glBegin(ogl.GL_QUADS)
		else :
			ogl.glBegin(ogl.GL_LINE_LOOP)
		#draw probe
		r = self.size()
		ogl.glVertex3f(-r, -r, 0.)
		ogl.glVertex3f( r, -r, 0.)
		ogl.glVertex3f( r,  r, 0.)
		ogl.glVertex3f(-r,  r, 0.)
		ogl.glEnd()
		ogl.glPopMatrix()
		ogl.glPopAttrib()
		#draw world
		if self.activated() :
			self.start_clipping(view)
		for world in self.worlds() :
			world._draw(view,mode)
		if self.activated() :
			self.stop_clipping(view)
	
	def selection_draw (self, view) :
		if self.activated() :
			self.start_clipping(view)
		for world in self.worlds() :
			world.selection_draw(view)
		if self.activated() :
			self.stop_clipping(view)
	
	########################################################
	#
	#		persistence
	#
	########################################################
	def save_state (self, state, viewer) :
		"""Write the current state of this
		element in state.
		
		It is the user responsability to
		store in state everything needed
		to restore the state of the view.
		
		.. warning: use a well defined key
		   to store all informations about
		   this element in a submap of state.
		   Default implementation use object
		   name to store informations relative
		   to opengl attributes.
		
		.. warning: state is intented to be
		   pickled. To avoid trouble when
		   restoring state, store only basic
		   python types and not user defined
		   custom classes :)
		
		:Parameters:
		 - `state` (dict of (str,dict of (str,param) ) )
		 - `viewer` (Viewer) - actual viewer
		
		:Return: None, modify state in place
		"""
		ProbeView.save_state(self,state,viewer)
		st = state[str(self.name() )]
		st["x"],st["y"],st["z"] = self.position()
		st["a"],st["b"],st["c"],st["d"] = self.orientation()
		st["activated"] = self.activated()
	
	def restore_state (self, state, viewer) :
		"""Try to restore the state of this
		element.
		
		Use informations stored in state. If
		informations are not available do nothing.
		
		:Parameters:
		 - `state` (dict of (str,dict of (str,param) ) )
		 - `viewer` (Viewer) - actual viewer
		"""
		ProbeView.restore_state(self,state,viewer)
		try :
			st = state[str(self.name() )]
			self.setPosition(Vec(st["x"],st["y"],st["z"]) )
			self.setOrientation(Quaternion(st["a"],st["b"],st["c"],st["d"]) )
			self.activate(viewer.view(),st["activated"])
		except KeyError :
			print "unable to restore state for element %s (CLippingProbeview)" % str(self.name() )





