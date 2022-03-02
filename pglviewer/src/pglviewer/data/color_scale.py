from PyQt4.QtCore import Qt,SIGNAL,QObject
from PyQt4.QtGui import QWidget,QLabel,QPixmap,\
                        QColor,QPen,QPainter,\
                        QBoxLayout,QSizePolicy,\
                        QDockWidget,QFrame
from ..elm_gui import ElmGUI

pix_size = 100

class ColorGradientWidget (QLabel) :
	"""Display a range of colors.
	"""
	def __init__ (self, parent, vmin, vmax, color_map_func, orientation = Qt.Vertical) :
		QLabel.__init__(self,parent)
		self.setScaledContents(True)
		#self.setSizePolicy(QSizePolicy.Minimum,QSizePolicy.Minimum)
		self._vmin = vmin
		self._vmax = vmax
		self._color_map_func = color_map_func
		self.set_orientation(orientation)
	
	def set_orientation (self, orientation) :
		vmin = self._vmin
		vmax = self._vmax
		color_map_func = self._color_map_func
		
		if orientation == Qt.Horizontal :
			self.setFixedHeight(10)
			self.setMinimumWidth(pix_size)
			self.setMaximumWidth(16777215)
			pix = QPixmap(pix_size,1)
			paint = QPainter(pix)
			for i in xrange(pix_size + 1) :
				color = QColor(*color_map_func(vmin + (vmax - vmin) * i / pix_size ).i3tuple() )
				paint.setPen(QPen(color) )
				paint.drawPoint(i,0)
		else :
			self.setFixedWidth(10)
			self.setMinimumHeight(pix_size)
			self.setMaximumHeight(16777215)
			pix = QPixmap(1,pix_size)
			paint = QPainter(pix)
			for i in xrange(pix_size + 1) :
				color = QColor(*color_map_func(vmin + (vmax - vmin) * i / pix_size ).i3tuple() )
				paint.setPen(QPen(color) )
				paint.drawPoint(0,pix_size - i)
		self.setPixmap(pix)
		self._pix = pix

class ScaleWidget (QWidget) :
	"""Display a range of textual values.
	"""
	def __init__ (self, parent, vmin, vmax, template = "%.2f", orientation = Qt.Vertical) :
		QWidget.__init__(self,parent)
		#self.setFrameShape(QFrame.Box)
		#self.setSizePolicy(QSizePolicy.Minimum,QSizePolicy.Minimum)
		self._vmin = vmin
		self._vmax = vmax
		self._template = template
		self._lab_txt = [QLabel("toto") for i in xrange(11)]
		self._lab_txt[0].setText(template % vmax)
		self._lab_txt[-1].setText(template % vmin)
		self._txt_size = self._lab_txt[0].fontMetrics().size(Qt.TextSingleLine,self._lab_txt[0].text() )
		self._txt_size *= 1.5
		self._layout = QBoxLayout(QBoxLayout.LeftToRight)
		self._layout.setSizeConstraint(QBoxLayout.SetMinimumSize)
		self.setLayout(self._layout)
		self.set_orientation(orientation)
	
	def set_orientation (self, orientation) :
		self._orientation = orientation
		if orientation == Qt.Horizontal :
			self.setFixedHeight(self._txt_size.height() )
			self.setMinimumWidth(self._txt_size.width() )
			self.setMaximumWidth(16777215)
			self._layout.setDirection(QBoxLayout.LeftToRight)
		else :
			self.setFixedWidth(self._txt_size.width() )
			self.setMinimumHeight(self._txt_size.height() )
			self.setMaximumHeight(16777215)
			self._layout.setDirection(QBoxLayout.TopToBottom)
		#self.recompute_labels()
		self.updateGeometry()
	
	def clear_layout (self) :
		"""Remove all widgets from the layout.
		"""
		for i in xrange(self._layout.count() ) :
			self._layout.removeItem(self._layout.itemAt(0) )
		for w in self._lab_txt :
			w.setParent(None)
		self._layout.invalidate()
	
	def recompute_labels (self) :
		"""Recompute labels.
		"""
		if self._orientation == Qt.Horizontal :
			nb_max_items = self.size().width() / self._txt_size.width()
		else :
			nb_max_items = self.size().height() / self._txt_size.height()
		nb_max_items = min(nb_max_items,len(self._lab_txt) )
		if (2 * nb_max_items - 1) == self._layout.count() :
			return
		self.clear_layout()
		tpl = self._template
		vmin = self._vmin
		vmax = self._vmax
		
		#set new text
		for i in xrange(1,nb_max_items - 1) :
			self._lab_txt[i].setText(tpl % (vmin + (vmax - vmin) \
			                                     * (nb_max_items - i - 1) \
			                                     / (nb_max_items - 1) ) )
		#fill layout
		for i in xrange(nb_max_items - 1) :
			self._layout.addWidget(self._lab_txt[i])
			self._layout.addStretch(1)
		self._layout.addWidget(self._lab_txt[-1])
	
	def resizeEvent (self, event) :
		QWidget.resizeEvent(self,event)
		self.recompute_labels()

class ColorScaleWidget (QWidget) :
	"""Display both a gradient and the txt values.
	"""
	def __init__ (self, parent, color_map_func, template, orientation = Qt.Vertical) :
		QWidget.__init__(self,parent)
		#self.setFrameShape(QFrame.Box)
		#self.setSizePolicy(QSizePolicy.Minimum,QSizePolicy.Minimum)
		vmin = color_map_func._value_min
		vmax = color_map_func._value_max
		self._orientation = None
		self._color_widget = ColorGradientWidget(self,vmin,vmax,color_map_func,orientation)
		self._txt_widget = ScaleWidget(self,vmin,vmax,template,orientation)
		self._layout = QBoxLayout(QBoxLayout.LeftToRight)
		self._layout.setSizeConstraint(QBoxLayout.SetMinimumSize)
		#self._layout.setSpacing(0)
		self.setLayout(self._layout)
		self.set_orientation(orientation)
	
	def clear_layout (self) :
		"""Remove all widgets from the layout.
		"""
		for i in xrange(self._layout.count() ) :
			self._layout.removeItem(self._layout.itemAt(0) )
		self._layout.invalidate()
		#self._txt_widget.setParent(None)
		#self._color_widget.setParent(None)
	
	def set_orientation (self, orientation) :
		if orientation == self._orientation : #do nothing
			return
		
		self.clear_layout()
		self._txt_widget.set_orientation(orientation)
		#self._txt_widget.recompute_labels()
		self._color_widget.set_orientation(orientation)
		if orientation == Qt.Vertical :
			self._layout.setDirection(QBoxLayout.LeftToRight)
			self.setFixedWidth(self._color_widget.minimumWidth() \
			                 + self._txt_widget.minimumWidth() )
			self.setMinimumHeight(10)
			self.setMaximumHeight(16777215)
		else :
			self._layout.setDirection(QBoxLayout.TopToBottom)
			self.setFixedHeight(self._color_widget.minimumHeight() \
			                  + self._txt_widget.minimumHeight() )
			self.setMinimumWidth(10)
			self.setMaximumWidth(16777215)
		
		self._layout.addWidget(self._color_widget)
		self._layout.addWidget(self._txt_widget)
		#self._layout.addStretch(1)
		#self.resize(self.minimumSize() )
		self._orientation = orientation
		#self.updateGeometry()
		#self._layout.activate()

class ColorScaleGUI (ElmGUI) :
	"""A GUI for a color map.
	"""
	def __init__ (self, title, color_map_func, template) :
		ElmGUI.__init__(self)
		self._title = title
		self._color_map_func = color_map_func
		self._template = template
	
	def setup_ui (self) :
		if ElmGUI.setup_ui(self) :
			self._dock_widget = QDockWidget(self._title)
			#self._dock_widget.setSizePolicy(QSizePolicy.Minimum,QSizePolicy.Minimum)
			self._color_scale_widget = ColorScaleWidget(None,self._color_map_func,self._template)
			self._dock_widget.setWidget(self._color_scale_widget)
			
			QObject.connect(self._dock_widget,
			                SIGNAL("dockLocationChanged(Qt::DockWidgetArea)"),
			                self.dock_area_changed)
			
			return True
		else :
			return False
	
	############################################
	#
	#	GUI install
	#
	############################################
	def install (self, main_window) :
		ElmGUI.install(self,main_window)
		main_window.addDockWidget(Qt.RightDockWidgetArea,self._dock_widget)
		self._dock_widget.show()
	
	def uninstall (self, main_window) :
		ElmGUI.uninstall(self,main_window)
		main_window.removeDockWidget(self._dock_widget)
		self._dock_widget.setParent(None)
		self._dock_widget.hide()
	
	def clean (self) :
		if self._dock_widget.isFloating() :
			self._dock_widget.close()
	############################################
	#
	#	interaction
	#
	############################################
	def dock_area_changed (self, dock_area) :
		"""Called when the dock has been moved to a new area.
		"""
		csw = self._color_scale_widget
		if dock_area in (Qt.LeftDockWidgetArea,
		                 Qt.RightDockWidgetArea) :
			csw.set_orientation(Qt.Vertical)
			#self._dock_widget.setFixedWidth(csw._color_widget.minimumWidth() \
			#                                + csw._txt_widget.minimumWidth() )
		else :
			csw.set_orientation(Qt.Horizontal)
		"""self._color_scale_widget.resize(10,10)
		self._dock_widget.resize(10,10)"""
		#self._dock_widget.updateGeometry()
		#self._dock_widget.layout().activate()



