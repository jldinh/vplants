# -*- python -*-
#
#       TissuePainterGUI: main gui for painter app
#
#       Copyright 2006 INRIA - CIRAD - INRA  
#
#       File author(s): Jerome Chopard <revesansparole@gmail.com>
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
# 
#       OpenAlea WebSite : http://openalea.gforge.inria.fr
#

__doc__="""
This module defines the gui for the color and display attributes
of tissue painter
"""

__license__= "Cecill-C"
__revision__=" $Id: $ "


from random import randint
import re
from PyQt4.QtCore import QObject, Qt, SIGNAL
from PyQt4.QtGui import (QWidget, QListWidget, QListWidgetItem
                       , QDialog, QDialogButtonBox
                       , QPushButton, QAction, QLineEdit, QToolButton
                       , QHBoxLayout, QVBoxLayout
                       , QColor, QPixmap, QIcon)
from vplants.plantgl.scenegraph import Material
from tissue_view import DEFAULT_MAT

color_list = [(255,0,0),(0,255,0),(0,0,255),(0,255,255),\
              (255,0,255),(255,255,0),(200,200,200),\
              (100,0,0),(0,100,0),(0,0,100),\
              (0,100,100),(100,0,100),(100,100,0),(100,100,100)]

color_list = [Material(col) for col in color_list]

class ColorItem (QListWidgetItem) :
	"""Small item that store a color_id
	to be displayed in QListWidget
	"""
	def __init__ (self, color_id, mat, parent) :
		QListWidgetItem.__init__(self, parent)
		self._color_id = color_id
		
		self.set_descr(None)
		
		pix = QPixmap(20, 20)
		col = (mat.ambient.red, mat.ambient.green, mat.ambient.blue)
		pix.fill(QColor(*col) )
		self.setIcon(QIcon(pix) )

	def color_id (self) :
		return self._color_id

	def descr (self) :
		return self._descr
	
	def set_descr (self, descr) :
		self._descr = descr
		
		if descr is None :
			if self._color_id is None :
				self.setText("None")
			else :
				self.setText("color %d" % self._color_id)
		else :
			self.setText("(%s) %s" % (self._color_id, descr) )

class ColorItemEditor (QDialog) :
	"""Small gui to edit properties of item
	"""
	def __init__ (self, parent, view, item) :
		QDialog.__init__(self, parent)

		#edit
		self._edit_descr = QLineEdit()
		d = item.descr()
		if d is None :
			d = ""
		self._edit_descr.setText(d)
		self._edit_color = QToolButton(None)
		self._edit_color.setText("col")
		
		#buttons
		self._button_box = QDialogButtonBox(QDialogButtonBox.Ok
		                                 | QDialogButtonBox.Cancel)
		
		QObject.connect(self._button_box, SIGNAL("accepted()"), self.accept)
		QObject.connect(self._button_box, SIGNAL("rejected()"), self.reject)

		#layout
		self._edit_layout = QHBoxLayout()
		self._edit_layout.addWidget(self._edit_descr)
		self._edit_layout.addStretch(1)
		self._edit_layout.addWidget(self._edit_color)
		
		self._layout = QVBoxLayout()
		self._layout.addLayout(self._edit_layout)
		self._layout.addWidget(self._button_box)
		
		self.setLayout(self._layout)
	
	def descr (self) :
		return str(self._edit_descr.text() )



class ColorDisplayGUI (QWidget) :
	"""Few GUI items to manage a list of colors
	and display attributes
	"""
	def __init__ (self, view, parent) :
		QWidget.__init__(self, parent)
		self._view = view #reference on tissue view
		
		self._current_color = None

		self._checked_state = []#TODO hack for bug qt unable to access
		                        #a signal for when check state change
	
	def setup_ui (self) :
		#main create color display list
		self._w_color = QListWidget(None)
		item = ColorItem(None, DEFAULT_MAT, self._w_color)
		item.setCheckState(Qt.Checked)
		self._checked_state.append(Qt.Checked)
		self._w_color.setCurrentItem(item)
		
		#create actions
		self._ac_new_color = QPushButton("New", None)
		QObject.connect(self._ac_new_color
		              , SIGNAL("clicked()")
		              , self.action_new_color)

		self._ac_del_color = QPushButton("&Del", None)
		QObject.connect(self._ac_del_color
		              , SIGNAL("clicked()")
		              , self.action_del_color)

		QObject.connect(self._w_color
		              , SIGNAL("clicked (const QModelIndex&)")
		              , self.item_clicked)
		QObject.connect(self._w_color
		              , SIGNAL("doubleClicked (const QModelIndex&)")
		              , self.item_double_clicked)
		QObject.connect(self._w_color
		              , SIGNAL("itemChanged (const QListWidgetItem&)")
		              , self.item_clicked)
		
		self._ac_display_all = QPushButton("Display all", None)
		QObject.connect(self._ac_display_all
		              , SIGNAL("clicked()")
		              , self.action_display_all)

		self._ac_display_none = QPushButton("Display None", None)
		QObject.connect(self._ac_display_none
		              , SIGNAL("clicked()")
		              , self.action_display_none)

		#menu
#		self._menu = QMenu("Color")
#		self._menu.addAction(self._ac_new_color.
		#signals from view
		QObject.connect(self._view, SIGNAL("add_color"), self.color_added)
		QObject.connect(self._view
		              , SIGNAL("set_color_description")
		              , self.color_descr_changed)
		QObject.connect(self._view, SIGNAL("del_color"), self.color_deleted)
		
		#layout
		self._top_layout = QHBoxLayout()
		self._top_layout.addWidget(self._ac_new_color)
		self._top_layout.addStretch(1)
		self._top_layout.addWidget(self._ac_del_color)
		
		self._bot_layout = QHBoxLayout()
		self._bot_layout.addWidget(self._ac_display_all)
		self._bot_layout.addWidget(self._ac_display_none)
		self._bot_layout.addStretch(1)
		
		self._main_layout = QVBoxLayout()
		self._main_layout.addLayout(self._top_layout)
		self._main_layout.addWidget(self._w_color)
		self._main_layout.addLayout(self._bot_layout)
		self._main_layout.addStretch(1)
	
		self.setLayout(self._main_layout)
	
	def keyPressEvent (self, event) :
		QWidget.keyPressEvent(self, event)
		if event.key() == Qt.Key_Escape :
			self.emit(SIGNAL("escape") )
	
	########################################################
	#
	#		accessors
	#
	########################################################
	def current_color (self) :
		return self._w_color.currentItem().color_id()

	def set_current_color (self, color_id) :
		lw = self._w_color
		row, = (i for i in range(lw.count() ) \
		        if lw.item(i).color_id() == color_id)
		lw.setCurrentRow(row)
	
	def new_color (self) :
		if len(color_list) > 0 :
			return color_list.pop(0)
		else :
			return Material( (randint(0, 255)
			                , randint(0, 255)
			                , randint(0, 255) ) )
	
	########################################################
	#
	#		actions
	#
	########################################################
	def action_new_color (self) :
		"""add a new item in the list
		"""
		color_id = self._view.add_color(self.new_color() )
	
	def color_added (self, color_id) :
		"""Signal from view
		"""
		mat = self._view.color_def(color_id)
		item = ColorItem(color_id, mat, self._w_color)
		item.setCheckState(Qt.Checked)
		self._checked_state.append(Qt.Checked)
		self._w_color.setCurrentItem(item)
	
	def color_descr_changed (self, color_id) :
		"""Signal from view
		"""
		lw = self._w_color
		item, = (lw.item(i) for i in range(lw.count() ) \
		         if lw.item(i).color_id() == color_id)
		item.set_descr(self._view.color_description(color_id) )
	
	def action_del_color (self) :
		self._view.del_color(self.current_color() )
	
	def color_deleted (self, color_id, mat) :#TODO undo command
		lw = self._w_color
		lw.setCurrentRow(0)
		row, = (i for i in range(lw.count() ) \
		         if lw.item(i).color_id() == color_id)
		lw.takeItem(row)
		del self._checked_state[row]
		
		color_list.insert(0, mat)
	
	def display_color (self, row) :
		item = self._w_color.item(row)
		state = item.checkState()
		if state != self._checked_state[row] :
			self._checked_state[row] = state
			color_id = item.color_id()
			vis = (state == Qt.Checked)
			modif = []
			for cid, col in self._view.state().iteritems() :
				if col == color_id :
					modif.append( (cid, vis) )
			
			self._view.update_display(modif)
	
	def item_clicked (self, index) :
		self.display_color(index.row() )
	
	def item_double_clicked (self, index) :
		if index.row() == 0 :
			return

		item = self._w_color.item(index.row() )
		dialog = ColorItemEditor(self, self._view, item)
		ret = dialog.exec_()
		if ret == dialog.Accepted :
			d = dialog.descr()
			if len(d) == 0 :
				d = None
			
			self._view.set_color_description(item.color_id(), d)
	
	def action_display_all (self) :
		"""Make all colors visible
		"""
		for row in range(self._w_color.count() ) :
			item = self._w_color.item(row)
			item.setCheckState(Qt.Checked)
			self.display_color(row)
	
	def action_display_none (self) :
		"""Make all colors invisible
		"""
		for row in range(self._w_color.count() ) :
			item = self._w_color.item(row)
			item.setCheckState(Qt.Unchecked)
			self.display_color(row)




















