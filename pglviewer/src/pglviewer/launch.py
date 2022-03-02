from PyQt4.QtGui import QApplication
from viewer import Viewer
from viewer_gui import ViewerGUI

def display (world, local_variables=None, gui=True) :
	"""Display a simple world.
	"""
	qapp = QApplication.instance()
	if qapp is None :
		qapp = QApplication([])
	v = Viewer()
	v.set_world(world)
	if gui :
		v.add_gui(ViewerGUI(local_variables) )
	v.show()
	v.view().show_entire_world()
	qapp.exec_()

def display2D (world, local_variables=None, gui=True) :
	"""Display a simple world in 2D.
	"""
	qapp = QApplication.instance()
	if qapp is None :
		qapp = QApplication([])
	v = Viewer()
	v.set_world(world)
	if gui :
		v.add_gui(ViewerGUI(local_variables) )
	v.show()
	v.view().set_dimension(2)
	qapp.exec_()

