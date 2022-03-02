# -*- python -*-
#
#       tissueedit: function used to edit tissue
#
#       Copyright 2006 INRIA - CIRAD - INRA  
#
#       File author(s): Jerome Chopard <jerome.chopard@sophia.inria.fr>
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
# 
#       OpenAlea WebSite : http://openalea.gforge.inria.fr
#

__doc__="""
This module defines functions to load a tissue property name
"""

__license__= "Cecill-C"
__revision__=" $Id: $ "

from PyQt4.QtCore import QObject,SIGNAL
from PyQt4.QtGui import QDialog,QFileDialog
from openalea.celltissue import TissueDB

import tissue_prop_dialog_ui

class TissuePropDialog (QDialog) :
	"""Dialog to find a tissue property name.
	"""
	
	def __init__ (self, parent, mode = 'r') :
		QDialog.__init__(self,parent)
		
		#GUI
		self.ui = tissue_prop_dialog_ui.Ui_Dialog()
		
		self.ui.setupUi(self)
		
		if mode == 'r' :
			self.ui.propNameBox.setEditable(False)
		elif mode == 'w' :
			self.ui.propNameBox.setEditable(True)
		else :
			raise UserWarning("unrecognized mode %s" % str(mode) )
		
		#attributes
		self._mode = mode
		
		#signal slot connection
		QObject.connect(self.ui.tissueNameButton,
		                SIGNAL("clicked(bool)"),
		                self.load_tissue_name)
		
		QObject.connect(self.ui.tissueNameEdit,
		                SIGNAL("textChanged(const QString &)"),
		                self.load_tissue)
		
		QObject.connect(self.ui.propNameBox,
		                SIGNAL(""),
		                self.load_prop_name)
	
	def get_infos (self) :
		"""Retrieve tissue and property name
		"""
		tname = str(self.ui.tissueNameEdit.text() )
		pname = str(self.ui.propNameBox.currentText() )
		if pname == "None" :
			pname = None
		
		return tname,pname
	
	def set_tissue_name (self, tissue_name) :
		"""Set name of tissue that will hold the property
		"""
		self.ui.tissueNameEdit.setText(tissue_name)
	
	def set_prop_name (self, prop_name) :
		"""Set the name of the property
		"""
		if str(self.ui.tissueNameEdit.text() ) == "" :
			return
		
		ind = self.ui.propNameBox.findText(prop_name)
		if ind >= 0 :
			self.ui.propNameBox.setCurrentIndex(ind)
		else :
			if self._mode == 'w' :
				self.ui.propNameBox.setItemText(0,prop_name)
	
	##############################################
	#
	#	internal slots
	#
	##############################################
	def load_tissue_name (self) :
		filename = QFileDialog.getOpenFileName(None,
		                                       "load property from",
		                                       "",
		                                       "tissue (*.zip)")
		if filename.isEmpty() :
			return
		
		self.set_tissue_name(filename)
	
	def load_tissue (self) :
		self.ui.propNameBox.clear()
		try :
			tname = str(self.ui.tissueNameEdit.text() )
			db = TissueDB()
			db.read(tname)
			if self._mode == 'w' :
				self.ui.propNameBox.addItem("None")
			for propname in db.properties() :
				self.ui.propNameBox.addItem(propname)
		except IOError :
			pass
	
	def load_prop_name (self, name) :
		self.ui.propNameEdit.setText(name)





def get_load_tissue_prop_name (tissue_name = None) :
	dia = TissuePropDialog(None,'r')
	if tissue_name is not None :
		dia.set_tissue_name(tissue_name)
	ret = dia.exec_()
	if ret == dia.Accepted :
		tname,pname = dia.get_infos()
		if tname == "" :
			return None
		if pname is None or pname == "" :
			return None
		return tname,pname
	else :
		return None

def get_save_tissue_prop_name (tissue_name = None, prop_name = None) :
	dia = TissuePropDialog(None,'w')
	if tissue_name is not None :
		dia.set_tissue_name(tissue_name)
		if prop_name is not None :
			dia.set_prop_name(prop_name)
	ret = dia.exec_()
	if ret == dia.Accepted :
		tname,pname = dia.get_infos()
		if tname == "" :
			return None
		if pname is None or pname == "" :
			return None
		return tname,pname
	else :
		return None

