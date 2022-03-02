from ..inrimage import InrImage
from PyQt4.QtCore import Qt,QObject,SIGNAL
from PyQt4.QtGui import (QApplication,QSizePolicy,QLabel,QMainWindow,
                        QSlider,QAction,QKeySequence,QIcon)
from inrimage_widget import compute_palette
from inrimage_stack_widget import InrImageStackWidget
from slide_viewer_ui import Ui_MainWindow

class SlideViewer (QMainWindow) :
	"""Display each image in a stack using a slider
	"""
	def __init__ (self) :
		QMainWindow.__init__(self)
		self.ui = Ui_MainWindow()
		self.ui.setupUi(self)
		
		self._im_view = InrImageStackWidget()
		self.setCentralWidget(self._im_view)
		
		#slider
		self._img_slider = QSlider(Qt.Horizontal)
		self._img_slider.setEnabled(False)
		QObject.connect(self._img_slider,
		                SIGNAL("valueChanged(int)"),
		                self._im_view.change_pix)
		
		self.ui.statusbar.addPermanentWidget(self._img_slider,1)
		
		
		#statusbar
		self._lab_xcoord = QLabel("% 4d" % 0)
		self._lab_ycoord = QLabel("% 4d" % 0)
		self._lab_zcoord = QLabel("% 4d" % 0)
		
		self.ui.statusbar.addPermanentWidget(self._lab_xcoord)
		self.ui.statusbar.addPermanentWidget(self._lab_ycoord)
		self.ui.statusbar.addPermanentWidget(self._lab_zcoord)
		
		#connections
		QObject.connect(self._im_view,SIGNAL("change_pix"),self.pix_changed)
		QObject.connect(self._im_view,SIGNAL("set_image"),self.image_changed)
		QObject.connect(self._im_view,SIGNAL("mouse_move"),self.coord_changed)
		
		QObject.connect(self.ui.action_close,
		                SIGNAL("triggered(bool)"),
		                self.close)
		
		QObject.connect(self.ui.action_snapshot,
		                SIGNAL("triggered(bool)"),
		                self.snapshot)
		
		QObject.connect(self.ui.action_rotate_left,
		                SIGNAL("triggered(bool)"),
		                self.rotate_left)
		
		QObject.connect(self.ui.action_rotate_right,
		                SIGNAL("triggered(bool)"),
		                self.rotate_right)
	
	def view (self) :
		return self._im_view
	
	def pix_changed (self, ind) :
		self._lab_zcoord.setText("% 4d" % ind)
	
	def coord_changed (self, pos, intens) :
		self._lab_xcoord.setText("% 4d" % pos[0])
		self._lab_ycoord.setText("% 4d" % pos[1])
		self._lab_ycoord.setText("% 4d" % pos[2])
	
	def image_changed (self) :
		self._img_slider.setRange(0,self.view().nb_pix() - 1)
		self._img_slider.setEnabled(True)
		self.view().change_pix(self._img_slider.value() )
	
	def snapshot (self) :
		"""write the current image
		"""
		pix = self.view().pixmap()
		pix.save("slice%.4d.png" % self._img_slider.value() )
	
	def wheelEvent (self, event) :
		inc = event.delta() / 8 / 15
		self._img_slider.setValue(self._img_slider.value() + inc)
	
	def rotate_left (self) :
		self.view().rotate(-1)
	
	def rotate_right (self) :
		self.view().rotate(1)

def display (filenames, palette = "grayscale", color_index_max = None) :
	#test for list of images to display
	if isinstance(filenames,str) :
		filenames = [filenames]
	
	qapp = QApplication.instance()
	if qapp is None :
		qapp = QApplication([])
	
	w_list = []
	for fname in filenames :
		img = InrImage()
		img.read(fname)
		
		w = SlideViewer()
		v = w.view()
		if color_index_max is None :
			cmax = img.data().max()
		else :
			cmax = color_index_max
		palette = compute_palette(palette,cmax)
		v.set_palette(palette)
		v.set_image(img)
		
		w.show()
		w.setWindowTitle(fname)
		w_list.append(w)

	qapp.exec_()


