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
This module defines functions to edit properties
"""

__license__= "Cecill-C"
__revision__=" $Id: $ "

from os.path import splitext
from pickle import load,dump
from PyQt4.QtCore import Qt,SIGNAL,QObject
from PyQt4.QtGui import (QAction,QIcon,QToolBar,QMenu,
                        QFileDialog,
                        QUndoCommand)
from openalea.pglviewer import ElmGUI,SelectTool
from openalea.celltissue import topen
from tissue_prop_dialog import (get_load_tissue_prop_name,
                                get_save_tissue_prop_name)

import tissueedit_rc

class UndoLoadState (QUndoCommand) :
	"""Undo redo change of current state
	"""
	def __init__ (self, gui, old_value, new_value) :
		QUndoCommand.__init__(self,"current state")
		self._gui = gui
		self._old_value = old_value
		self._new_value = new_value
	
	def undo (self) :
		self._gui.change_state(self._old_value)
	
	def redo (self) :
		self._gui.change_state(self._new_value)

class UndoSaveState (QUndoCommand) :
	"""Mark a save operation
	"""
	def __init__ (self) :
		QUndoCommand.__init__(self,"save state")
	
	def undo (self) :
		pass
	
	def redo (self) :
		pass

class PropEditGUI (ElmGUI) :
	"""GUI used to read write a property.
	"""
	
	def __init__ (self, prop, prop_view = None) :
		"""Initialize GUI
		"""
		ElmGUI.__init__(self)
		
		self._prop = prop
		self._associated_view = prop_view
		
		self._current_filename = None
	
	def setup_ui (self) :
		if ElmGUI.setup_ui(self) :
			#actions
			self._action_bar = QToolBar("prop inout")
			
			self._action_save_state_as = self._action_bar.addAction("save as")
			QObject.connect(self._action_save_state_as,
			               SIGNAL("triggered(bool)"),
			               self.save_state_as)
			
			self._action_save_state = self._action_bar.addAction("save")
			self._action_save_state.setIcon(QIcon(":image/save_state.png") )
			QObject.connect(self._action_save_state,
			               SIGNAL("triggered(bool)"),
			               self._save_state)
			
			self._action_load_state = self._action_bar.addAction("load")
			self._action_load_state.setIcon(QIcon(":image/load_state.png") )
			QObject.connect(self._action_load_state,
			               SIGNAL("triggered(bool)"),
			               self.load_state)
	
	def clean (self) :
		ElmGUI.clean(self)
	
	def install (self, main_window) :
		ElmGUI.install(self,main_window)
		self.add_action_bar(main_window,self._action_bar)
	
	def uninstall (self, main_window) :
		ElmGUI.uninstall(self,main_window)
		self.remove_bar(main_window,self._action_bar)
	
	def change_state (self, new_state) :
		"""Change state of the property
		for a new one.
		"""
		self._prop.clear()
		self._prop.update(new_state)
		if self._associated_view is not None :
			self._associated_view.redraw()
	
	###############################################
	#
	#	accessor
	#
	###############################################
	def set_current_filename (self, filename) :
		self._current_filename = filename
		self._load_state()
	
	###############################################
	#
	#	actions
	#
	###############################################
	def save_state_as (self) :
		"""Save the current state of the
		property in a file.
		"""
		raise NotImplementedError
	
	def save_state (self) :
		"""Save the current state of the
		property in a file.
		"""
		raise NotImplementedError
	
	def _save_state (self) :
		if self._current_filename is None :
			self.save_state_as()
		else :
			self.save_state()
	
	def load_state (self) :
		"""load the current state of the
		property from a file.
		"""
		raise NotImplementedError
	
	def _load_state (self) :
		raise NotImplementedError

class FilePropEditGUI (PropEditGUI) :
	"""GUI used to read write a property in a single file.
	"""
	###############################################
	#
	#	actions
	#
	###############################################
	def save_state_as (self) :
		"""Save the current state of the
		property in a file.
		"""
		filename = QFileDialog.getSaveFileName(None,
			                                   "save property in",
			                                   "",
			                                   "pickled (*.pkl)")
		if filename.isEmpty() :
			return
		
		filename = str(filename)
		if len(splitext(filename)[1]) == 0 :
			filename = "%s.pkl" % str(filename)
		
		self._current_filename = filename
		self.save_state()
	
	def save_state (self) :
		"""Save the current state of the
		property in a file.
		"""
		dump(self._prop,open(self._current_filename,'w') )
	
	def load_state (self) :
		"""load the current state of the
		property from a file.
		"""
		filename = QFileDialog.getOpenFileName(None,
			                                   "load property from",
			                                   "",
			                                   "pickled (*.pkl)")
		if filename.isEmpty() :
			return
		
		self.set_current_filename( str(filename) )
	
	def _load_state (self) :
		new_state = load(open(self._current_filename,'rb') )
		old_state = dict(self._prop)
		self.emit("undo command",UndoLoadState(self,old_state,new_state) )
		
		self.change_state(new_state)

class TissuePropEditGUI (PropEditGUI) :
	"""GUI used to read write a property in a tissue file.
	"""
	###############################################
	#
	#	actions
	#
	###############################################
	def save_state_as (self) :
		"""Save the current state of the
		property in a tissue.
		"""
		if self._current_filename is None :
			tname = None
			pname = None
		else :
			tname,pname = self._current_filename
		
		filename = get_save_tissue_prop_name(tname,pname)
		
		if filename is None :
			return
		
		self._current_filename = filename
		self.save_state()
	
	def save_state (self) :
		"""Save the current state of the
		property in a file.
		"""
		tname,propname = self._current_filename
		f = topen(tname,'a')
		f.write(self._prop,propname)
		f.close()
	
	def load_state (self) :
		"""load the current state of the
		property from a file.
		"""
		if self._current_filename is None :
			tname = None
		else :
			tname,pname = self._current_filename
		
		filename = get_load_tissue_prop_name(tname)
		
		if filename is None :
			return
		
		self.set_current_filename(filename)
	
	def _load_state (self) :
		tname,propname = self._current_filename
		
		f = topen(tname,'r')
		new_state,desr = f.read(propname)
		f.close()
		
		old_state = dict(self._prop)
		
		self.emit("undo command",UndoLoadState(self,old_state,new_state) )
		
		self.change_state(new_state)

