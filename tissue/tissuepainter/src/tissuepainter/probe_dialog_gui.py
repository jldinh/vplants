from PyQt4.QtCore import Qt,SIGNAL
from PyQt4.QtGui import QWidget,QDockWidget
from openalea.pglviewer import ClippingProbeGUI
from probe_dialog_ui import Ui_Form

class ProbeGUI (ClippingProbeGUI) :
	"""
	a specialized gui for painter
	"""
	def __init__ (self, probe, painter_gui) :
		ClippingProbeGUI.__init__(self,probe)
		self._painter_gui = painter_gui
	
	def setup_ui (self, main_window) :
		if ClippingProbeGUI.setup_ui(self,main_window) :
			ui = self.ui
			#dock widget
			ui.dock_widget = QDockWidget()
			ui.probe_widget = QWidget()
			self.dock_ui = Ui_Form()
			self.dock_ui.setupUi(ui.probe_widget)
			ui.dock_widget.setWidget(ui.probe_widget)
			#special actions
			main_window.connect(self.dock_ui.initButton, \
			                    SIGNAL("clicked(bool)"), \
			                    self.init_slicing)
	
	def install (self, main_window) :
		ClippingProbeGUI.install(self,main_window)
		main_window.addDockWidget(Qt.RightDockWidgetArea, \
		                          self.ui.dock_widget)
	
	def uninstall (self, main_window) :
		ClippingProbeGUI.uninstall(self,main_window)
		main_window.removeDockWidget(self.ui.dock_widget)
	
	##################################
	#
	#	specific actions
	#
	##################################
	def init_slicing (self) :
		"""
		gather all informations
		and change probe location
		"""
		ui = self.dock_ui
		f = self._painter_gui.tissue_file()
		cfg = f.read_config("info")
		f.close()
		current_tab = ui.sliceTabWidget.currentIndex()
		if current_tab == 0 : #translation
			exec "axis = %s" % str(ui.translationAxisEdit.text())
			exec "offset = %s" % str(ui.translationOffsetEdit.text())
			incr = str(ui.translationIncrementEdit.text())
			print "translation","axis",axis,"offset",offset,"incr",incr
		elif current_tab == 1 : #rotation
			axis = str(ui.rotationAxisEdit.text())
			offset = str(ui.rotationOffsetEdit.text())
			incr = str(ui.rotationIncrementEdit.text())
			print "rotation","axis",axis,"offset",offset,"incr",incr
		else :
			raise UserWarning("curren tab zarby")
			
		
	

