from PyQt4.QtCore import SIGNAL
from PyQt4.QtGui import QDialog
try :
	from openalea.tissuedb import topen
except ImportError :
	from openalea.celltissue import topen

from tissue_property_dialog_ui import Ui_Dialog

class TissuePropertyDialog (QDialog) :
	"""
	dialog widget to find a property
	inside a tissue file
	"""
	def __init__ (self, tissuename, mode='r', parent = None) :
		QDialog.__init__(self,parent)
		ui = Ui_Dialog()
		self.ui = ui
		ui.setupUi(self)
		#window title
		if mode == 'r' :
			self.setWindowTitle("read property")
		elif mode == 'w' :
			self.setWindowTitle("write property")
		else :
			raise UserWarning("mode %s not recognized" % str(mode))
		#signal slots
		self.connect(ui.propertyListWidget,SIGNAL("itemSelectionChanged()"),self.select_name)
		self.connect(ui.propertyListWidget,SIGNAL("itemDoubleClicked(QListWidgetItem*)"),self.accept_name)
		#fill fields
		f = topen(tissuename,'r')
		names = list(f.properties())
		f.close()
		names.sort()
		#add names to list widget
		for propname in names :
			ui.propertyListWidget.addItem(propname)
		if mode == 'w' :
			#propose a new name
			state_names = [name for name in names if name.startswith("state")]
			if len(state_names) == 0 :
				proposed_name = "state"
			else :
				ind_list = []
				for name in state_names :
					try :
						ind_list.append(int(name[5:]))
					except ValueError :
						pass
				if len(ind_list) == 0 :
					proposed_name = "state000"
				else :
					ind_list.sort()
					proposed_name = "state%.3d" % (ind_list[-1] + 1)
			ui.propertyNameEdit.setText(proposed_name)
		"""else :
			ui.propertyNameEdit.setEnabled(False)"""
	##########################################
	#
	#		SIGNAL SLOT
	#
	##########################################
	def select_name (self) :
		"""
		a new name has been selected
		"""
		item = list(self.ui.propertyListWidget.selectedItems())[0]
		self.ui.propertyNameEdit.setText(item.text())
	
	def accept_name (self, item) :
		"""
		the selected name has been approved
		"""
		self.ui.propertyNameEdit.setText(item.text())
		self.accept()
	##########################################
	#
	#		accessors
	#
	##########################################
	def property_name (self) :
		"""
		return the selected property name
		"""
		return str(self.ui.propertyNameEdit.text())

