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
This module defines functions to edit tissue properties
"""

__license__= "Cecill-C"
__revision__=" $Id: $ "

from PyQt4.QtCore import Qt,SIGNAL,QObject
from PyQt4.QtGui import QAction,QIcon,QToolBar,QMenu, \
                        QFileDialog,QLineEdit,QComboBox, \
                        QUndoCommand
from openalea.pglviewer import ElmGUI,SelectTool

import tissueedit_rc

class UndoClearValues (QUndoCommand) :
	"""Undo redo change of current values
	"""
	def __init__ (self, gui, old_values, new_values) :
		QUndoCommand.__init__(self,"clear")
		self._gui = gui
		self._old_values = old_values
		self._new_values = new_values
	
	def undo (self) :
		self._gui._view.set_values(self._old_values)
	
	def redo (self) :
		self._gui._view.set_values(self._new_values)

class UndoCurrentValue (QUndoCommand) :
	"""Undo redo change of current value.
	"""
	def __init__ (self, gui, old_value, new_value) :
		QUndoCommand.__init__(self,"current value")
		self._gui = gui
		self._old_value = old_value
		self._new_value = new_value
	
	def undo (self) :
		self._gui._set_current_value(self._old_value)
	
	def redo (self) :
		self._gui._set_current_value(self._new_value)

class UndoSetValue (QUndoCommand) :
	"""Undo redo change of a value.
	"""
	def __init__ (self, gui, wid, old_value, new_value) :
		QUndoCommand.__init__(self,"set value")
		self._gui = gui
		self._wid = wid
		self._old_value = old_value
		self._new_value = new_value
	
	def undo (self) :
		self._gui._view.set_value(self._wid,self._old_value)
	
	def redo (self) :
		self._gui._view.set_value(self._wid,self._new_value)

class UndoFillValues (QUndoCommand) :
	"""Undo redo change of a set of values.
	"""
	def __init__ (self, gui, old_values, new_values) :
		QUndoCommand.__init__(self,"fill")
		self._gui = gui
		self._old_values = old_values
		self._new_values = new_values
	
	def undo (self) :
		self._gui._view.set_values(self._old_values)
	
	def redo (self) :
		self._gui._view.set_values(self._new_values)

class ScalarPropEditGUI (ElmGUI) :
	"""GUI used to edit a scalar property.
	"""
	def __init__ (self, scalar_prop_view, prop_type=None, select_func=None) :
		"""Initialize GUI
		"""
		ElmGUI.__init__(self)
		
		self._view = scalar_prop_view
		
		if prop_type is None :
			typ = scalar_prop_view.prop_type()
			if typ is None :
				raise UserWarning("don't know the type of this prop")
			prop_type = eval(typ)
		
		self._prop_type = prop_type
		
		if select_func is None :
			self._select_func = self._view.selection_draw
		else :
			self._select_func = select_func
		self._current_value = None
	
	def setup_ui (self) :
		if ElmGUI.setup_ui(self) :
			#actions
			self._action_bar = QToolBar("scalar prop actions")
			
			self._action_clear_values = self._action_bar.addAction("clear")
			self._action_clear_values.setIcon(QIcon(":image/clear_values.png") )
			QObject.connect(self._action_clear_values,
			               SIGNAL("triggered(bool)"),
			               self.clear_values)
			
			self._action_apply = self._action_bar.addAction("apply")
			self._action_apply.setIcon(QIcon(":image/apply.png") )
			QObject.connect(self._action_apply,
			               SIGNAL("triggered(bool)"),
			               self.apply)
			
			self._edit_current_value = QLineEdit("None")
			QObject.connect(self._edit_current_value,
			                SIGNAL("editingFinished()"),
			                self.edit_current_value)
			self._action_bar.addWidget(self._edit_current_value)
			
			#tools
			self._tool_bar = QToolBar("scalar prop tools")
			
			self._tool_pick = SelectTool(self._tool_bar,
			                             "pick",
			                             self._select_func)
			self._tool_pick.setIcon(QIcon(":image/pick_value.png") )
			QObject.connect(self._tool_pick,
			                SIGNAL("elm selected"),
			                self.pick_value)
			self._tool_bar.addAction(self._tool_pick)
			
			self._tool_set = SelectTool(self._tool_bar,
			                             "set",
			                             self._select_func)
			self._tool_set.setIcon(QIcon(":image/set_value.png") )
			QObject.connect(self._tool_set,
			                SIGNAL("elm selected"),
			                self.slot_set_value)
			self._tool_bar.addAction(self._tool_set)
			
			self._tool_fill = SelectTool(self._tool_bar,
			                             "fill",
			                             self._select_func)
			self._tool_fill.setIcon(QIcon(":image/fill_value.png") )
			QObject.connect(self._tool_fill,
			                SIGNAL("elm selected"),
			                self.slot_fill_value)
			self._tool_bar.addAction(self._tool_fill)
			
			#view interactions
			QObject.connect(self._view,
			                SIGNAL("set_value"),
			                self.update)
			QObject.connect(self._view,
			                SIGNAL("set_values"),
			                self.update)
			QObject.connect(self._view,
			                SIGNAL("clear_values"),
			                self.update)
			QObject.connect(self._view,
			                SIGNAL("fill"),
			                self.update)
	
	def clean (self) :
		ElmGUI.clean(self)
	
	def install (self, main_window) :
		ElmGUI.install(self,main_window)
		self.add_action_bar(main_window,self._action_bar)
		self.add_tool_bar(main_window,self._tool_bar)
	
	def uninstall (self, main_window) :
		ElmGUI.uninstall(self,main_window)
		self.remove_bar(main_window,self._action_bar)
		self.remove_bar(main_window,self._tool_bar)
	
	def update (self, *args) :
		self._view.redraw()
	
	###############################################
	#
	#	accessors
	#
	###############################################
	def current_value (self) :
		return self._current_value
	
	def _set_current_value (self, value) :
		self._current_value = value
		self._edit_current_value.setText(str(value) )
	
	def set_current_value (self, value) :
		old_value = self.current_value()
		if value != old_value :
			self._set_current_value(value)
			self.emit("undo command",UndoCurrentValue(self,old_value,value) )
	
	###############################################
	#
	#	actions
	#
	###############################################
	def clear_values (self) :
		"""Clear the property
		"""
		old_values = dict(self._view.values() )
		if len(old_values) > 0 :
			self._view.clear_values()
			new_values = dict(self._view.values() )
			self.emit("undo command",UndoClearValues(self,old_values,new_values) )
	
	def apply (self) :
		"""Apply changes on the property.
		"""
		self.update()
	
	def edit_current_value (self) :
		txt = str(self._edit_current_value.text() )
		if txt.startswith("None") :
			self.set_current_value(None)
		else :
			self.set_current_value(self._prop_type(txt) )
	###############################################
	#
	#	interactions
	#
	###############################################
	def find_id (self, elmid) :
		"""Find the user id of an element
		"""
		sc = self._view
		if sc.idmode == sc.IDMODE.SHAPE :
			return elmid
		else :
			shp = sc.findSceneObject(elmid)
			return shp.id
	
	def pick_value (self, elmid) :
		if elmid is None :
			self.set_current_value(None)
		else :
			wid = self.find_id(elmid)
			print "value",self._view.value(wid),'of element',wid
			self.set_current_value(self._view.value(wid) )
	
	def slot_set_value (self, elmid) :
		if elmid is not None :
			wid = self.find_id(elmid)
			old_value = self._view.value(wid)
			value = self.current_value()
			if old_value != value :
				self._view.set_value(wid,value)
				self.emit("undo command",UndoSetValue(self,wid,old_value,value) )
	
	def slot_fill_value (self, elmid) :
		if elmid is not None :
			wid = self.find_id(elmid)
			old_value = self._view.value(wid)
			value = self.current_value()
			if old_value != value :
				old_values = dict(self._view.values() )
				self._view.fill(wid,self.current_value() )
				new_values = dict(self._view.values() )
				self.emit("undo command",UndoFillValues(self,old_values,new_values) )
	


