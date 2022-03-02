from PyQt4.QtCore import SIGNAL
from PyQt4.QtGui import QFont,QFontMetrics
import OpenGL.GL as ogl
from PyQGLViewer import Frame,Vec,Quaternion
from vplants.plantgl.math import Matrix4
from vplants.plantgl.scenegraph import Text,Box,Material,Translated,Shape
from vplants.plantgl.algo import Discretizer,GLRenderer,BBoxComputer
from ..elm_view import ElmView
from ..constants import DRAW_MODE
from scene import Scene

class DisplayStyle (object) :
	SOLID = 0
	WIREFRAME = 1
	BOTH = 2

class IdMode (object) : 
	SCENEOBJECT = GLRenderer.SceneObjectId
	SHAPE = GLRenderer.ShapeId

class LightingStyle(object):
	FRONT = 0
	TWO_SIDE = 1

class SceneView (ElmView) :
	"""View on a classical plantgl.scene
	"""
	DISPLAY = DisplayStyle()
	IDMODE = IdMode()
	LIGHTING = LightingStyle()
	
	def __init__ (self, scene=None) :
		ElmView.__init__(self,"scene")
		if scene is None :
			self._scene = Scene()
		else :
			self._scene = scene
		#internal state variables
		self._selection_material = Material( (0,0,0) )
		self.idmode = self.IDMODE.SCENEOBJECT
		self._alpha_threshold = None
		#draw
		self._discretizer = Discretizer()
		self._renderer = GLRenderer(self._discretizer)
		self._renderer.renderingMode = GLRenderer.RenderingMode.Dynamic
		self._display_mode = self.DISPLAY.SOLID
		self._lighting_style = self.LIGHTING.FRONT
		#selection
		self._selected = set()
		self._selected_bbox = []
		#associated frame
		self._frame = None
		self._draw_frame = False
		self._draw_length = 1.
	
	def set_dynamic (self, dynamic=True) :
		if dynamic :
			self._renderer.renderingMode = GLRenderer.RenderingMode.Dynamic
		else :
			self._renderer.renderingMode = GLRenderer.RenderingMode.Normal
	
	def set_alpha_threshold (self, threshold = None) :
		self._alpha_threshold = threshold
	
	def get_alpha_threshold (self) :
		return self._alpha_threshold 
	
	def set_lighting_style(self, style = LightingStyle.FRONT):
		self._lighting_style = style
	
	def get_lighting_style(self):
		return self._lighting_style
	
	#########################################################
	#
	#		emulation of frame methods
	#
	#########################################################
	def constraint (self) :
		if self._frame is None :
			return None
		else :
			return self._frame.constraint()
	
	def position (self) :
		if self._frame is None :
			return None
		else :
			return self._frame.position()
	
	def setPosition (self, vec) :
		if self._frame is None :
			return
		else :
			self._frame.setPosition(vec)
			self.emit(SIGNAL("set_position"),vec)
			self.emit(SIGNAL("update") )
	
	def orientation (self) :
		if self._frame is None :
			return None
		else :
			return self._frame.orientation()
	
	def setOrientation (self, quaternion) :
		if self._frame is None :
			return
		else :
			self._frame.setOrientation(quaternion)
			self.emit(SIGNAL("set_orientation"),quaternion)
			self.emit(SIGNAL("update") )
	
	def matrix (self) :
		if self._frame is None :
			return None
		else :
			return self._frame.matrix()
	
	def world_matrix (self) :
		if self._frame is None :
			return None
		else :
			return self._frame.worldMatrix()
	
	def setReferenceFrame (self, frame) :
		if self._frame is None :
			return
		else :
			self._frame.setReferenceFrame(frame)
			self.emit(SIGNAL("set_reference_frame"),frame)
			self.emit(SIGNAL("update") )
	
	#########################################################
	#
	#		emulation of scene methods
	#
	#########################################################
	def clear (self, send_signal = True) :
		self._scene.clear()
		self._discretizer.clear()
		self._renderer.clear()
		self._selected.clear()
		self._selected_bbox = []
		if send_signal :
			self.emit(SIGNAL("clear") )
			self.emit(SIGNAL("update") )
	
	def remove (self, shape) :
		self._scene.remove(shape)
		self.emit(SIGNAL("remove") )
		self.emit(SIGNAL("update") )


	def __iremove__ (self, shape) :
		self._scene -= shape
		self.emit(SIGNAL("__iremove__") )
		self.emit(SIGNAL("update") )
	
	def add (self, shape) :
		self._scene.add(shape)
		self.emit(SIGNAL("add") )
		self.emit(SIGNAL("update") )
	
	def __iadd__ (self, shape) :
		self._scene += shape
		self.emit(SIGNAL("__iadd__") )
		self.emit(SIGNAL("update") )
		return self
	
	def merge (self, sc, send_signal = True) :
		if isinstance(sc,ElmView) :
			self._scene.merge(sc._scene)
		else :
			self._scene.merge(sc)
		if send_signal :
			self.emit(SIGNAL("merge") )
			self.emit(SIGNAL("update") )
	
	def read (self, filename) :
		self._scene.read(filename)
		self.emit(SIGNAL("read") )
		self.emit(SIGNAL("update") )
	
	def save (self, filename) :
		self._scene.save(filename)
		self.emit(SIGNAL("save") )
	
	def __iter__ (self) :
		return iter(self._scene)
	
	def find (self, shp_id) :
		return self._scene.find(shp_id)
	
	def findSceneObject (self, shp_id) :
		return self._scene.findSceneObject(shp_id)
	
	def user_id (self, shp_id) :
		shp = self._scene.findSceneObject(shp_id)
		return shp.id
	
	########################################################
	#
	#		selection
	#
	########################################################
	def set_selection (self, selected) :
		"""Set a list of selected shapes.
		"""
		self._selected = set(selected)
		self._selected_bbox = []
		bbc = BBoxComputer(self._discretizer)
		for shp_id in selected :
			shp = self.findSceneObject(shp_id)
			shp.apply(bbc)
			bb = bbc.result
			geom = Translated(bb.getCenter(),
			                  Box(bb.getSize() ) )
			self._selected_bbox.append(Shape(geom,self._selection_material) )
		self.emit(SIGNAL("update") )
	
	def selection (self) :
		"""Return the list of selected shapes.
		"""
		return self._selected
	
	def clear_selection (self, send_signal = True) :
		"""Clear the list of selection.
		"""
		self._selected = set()
		self._selected_bbox = []
		if send_signal :
			self.emit(SIGNAL("update") )
	
	########################################################
	#
	#		frame
	#
	########################################################
	def frame (self) :
		"""Access to the associated frame.
		"""
		return self._frame
	
	def set_frame (self, frame) :
		"""Set an associated frame.
		"""
		self._frame = frame
		self.emit(SIGNAL("set_frame"),frame)
		self.emit(SIGNAL("update") )
	
	def create_frame (self) :
		"""Associate an empty frame.
		"""
		self.set_frame(Frame() )
	
	def clear_frame (self) :
		"""Clear position and rotation.
		"""
		self.setPosition(Vec(0,0,0) )
		self.setOrientation(Quaternion() )
	
	def draw_frame (self) :
		"""Tell wether the frame is drawn.
		"""
		return self._draw_frame
	
	def set_draw_frame (self, state) :
		"""Set the display of the associated frame.
		"""
		self._draw_frame = state
		if state and self.frame() is None :
			self.create_frame()
		self.emit(SIGNAL("set_draw_frame"),state)
		self.emit(SIGNAL("update") )
	
	def set_draw_length (self, length) :
		"""Set the length of the small displayed frame vectors.
		"""
		self._draw_length = length
		self.emit(SIGNAL("set_draw_length") )
	
	#########################################################
	#
	#		drawable
	#
	#########################################################
	def display_mode (self) :
		"""Current display mode.
		one of DISPLAY
		"""
		return self._display_mode
	
	def set_display_mode (self, mode) :
		self._display_mode = mode
		self.emit(SIGNAL("set_display_mode"),mode)
		self.emit(SIGNAL("update") )
	
	def bounding_box (self) :#TODO take text shapes into account
		bbc = BBoxComputer(self._discretizer)
		bbc.process(self._scene)
		bb = bbc.result
		if self.frame() is not None :
			mat = Matrix4(*self.frame().getMatrix() )
			bb.transform(mat)
		return bb
	
	def position (self) :
		if self.frame() is not None :
			return self.frame().position()
	
	def center (self) :
		if self.frame() is not None :
			return self.frame().position()
	
	def draw (self, view, mode) :
		if mode == DRAW_MODE.SELECT :
			self.selection_draw(view)
		else :
			self.normal_draw(view,mode)
	
	def frame_draw (self, view, mode) :
		vl = self._draw_length
		ogl.glPushAttrib(ogl.GL_LIGHTING_BIT)
		ogl.glDisable(ogl.GL_LIGHTING)
		#draw axes
		ogl.glBegin(ogl.GL_LINES)
		ogl.glColor3f(1.,0.,0.)
		ogl.glVertex3f(0.,0.,0.)
		ogl.glVertex3f(vl,0.,0.)
		
		ogl.glColor3f(0.,1.,0.)
		ogl.glVertex3f(0.,0.,0.)
		ogl.glVertex3f(0.,vl,0.)
		
		ogl.glColor3f(0.,0.,1.)
		ogl.glVertex3f(0.,0.,0.)
		ogl.glVertex3f(0.,0.,vl)
		ogl.glEnd()
		if mode == DRAW_MODE.NORMAL :
			#draw axes names
			font = QFont("ariana",8)
			ogl.glColor3f(1.,0.,0.)
			view.renderText(1.01 * vl,0.,0.,"X",font)
			ogl.glColor3f(0.,1.,0.)
			view.renderText(0.,1.01 * vl,0.,"Y",font)
			ogl.glColor3f(0.,0.,1.)
			view.renderText(0.,0.,1.01 * vl,"Z",font)
		ogl.glPopAttrib()
	
	def normal_draw (self, view, mode) :
		renderer = self._renderer
		scene = self._scene
		DISPLAY = self.DISPLAY
		LIGHTING = self.LIGHTING
		#begin frame
		frame = self.frame()
		if frame is not None :
			ogl.glPushMatrix()
			ogl.glMultMatrixd(frame.matrix() )
			if self.draw_frame() :
				self.frame_draw(view,mode)
			
		#draw stage
		#face lighting 
		if self._lighting_style == LIGHTING.TWO_SIDE:
			ogl.glPushAttrib(ogl.GL_LIGHTING_BIT)
			ogl.glLightModeli(ogl.GL_LIGHT_MODEL_TWO_SIDE, ogl.GL_TRUE)
		
		#alpha
		if self._alpha_threshold is not None :
			ogl.glAlphaFunc(ogl.GL_GREATER,self._alpha_threshold)
			ogl.glEnable(ogl.GL_ALPHA_TEST)
			ogl.glBlendFunc(ogl.GL_SRC_ALPHA,
			                ogl.GL_ONE_MINUS_SRC_ALPHA)
			ogl.glEnable(ogl.GL_BLEND)
		#scene
		ogl.glPushAttrib(ogl.GL_POLYGON_BIT)
		ogl.glEnable(ogl.GL_NORMALIZE)
		if self._display_mode in [DISPLAY.SOLID,DISPLAY.BOTH] :
			ogl.glPolygonMode(ogl.GL_FRONT_AND_BACK, ogl.GL_FILL)
			scene.apply(renderer)
		if self._display_mode in [DISPLAY.WIREFRAME,DISPLAY.BOTH]:
			ogl.glPolygonMode(ogl.GL_FRONT_AND_BACK, ogl.GL_LINE)
			scene.apply(renderer)
		ogl.glPopAttrib()
		
		if self._lighting_style == LIGHTING.TWO_SIDE:
			ogl.glPopAttrib()
		
		#alpha
		if self._alpha_threshold is not None :
			ogl.glDisable(ogl.GL_BLEND)
			ogl.glDisable(ogl.GL_ALPHA_TEST)
		
		#other draw
		if mode == DRAW_MODE.NORMAL :
			ogl.glPushAttrib(ogl.GL_LIGHTING_BIT)
			ogl.glDisable(ogl.GL_LIGHTING)
			#draw selection
			ogl.glPushAttrib(ogl.GL_POLYGON_BIT)
			ogl.glPolygonMode(ogl.GL_FRONT_AND_BACK, ogl.GL_LINE)
			for shp in self._selected_bbox :
				shp.apply(renderer)
			ogl.glPopAttrib()
			#draw text
			for shp in scene :
				if isinstance(shp.geometry,Text) :
					col = shp.appearance.ambient
					ogl.glColor3f(col.red / 255.,
					              col.green / 255.,
					              col.blue / 255.)
					txt = shp.geometry
					font = QFont(txt.fontstyle.family,txt.fontstyle.size)
					fontm = QFontMetrics(font)
					screen_pos = view.camera().projectedCoordinatesOf(Vec(*tuple(txt.position) ),
					                                                  frame )
					screen_pos.x -= fontm.width(txt.string) / 2.
					screen_pos.y += fontm.xHeight() / 2.
					pos = view.camera().unprojectedCoordinatesOf(screen_pos,
					                                             frame )
					view.renderText(pos.x,
					                pos.y,
					                pos.z,
					                txt.string,
					                font)
			ogl.glPopAttrib()
		#end frame
		if frame is not None :
			ogl.glPopMatrix()
	
	def selection_draw (self, view) :
		renderer = self._renderer
		saved_mode = renderer.renderingMode
		renderer.renderingMode = renderer.RenderingMode.Selection
		renderer.selectionMode = self.idmode
		#begin frame
		frame = self.frame()
		if frame is not None :
			ogl.glPushMatrix()
			ogl.glMultMatrixd(frame.worldMatrix() )
		#draw
		ogl.glPushAttrib(ogl.GL_POLYGON_BIT)
		ogl.glPolygonMode(ogl.GL_FRONT_AND_BACK, ogl.GL_FILL)
		self._scene.apply(renderer)
		ogl.glPopAttrib()
		#end frame
		if frame is not None :
			ogl.glPopMatrix()
		
		renderer.renderingMode = saved_mode
	

