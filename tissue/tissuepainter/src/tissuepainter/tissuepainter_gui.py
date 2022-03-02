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
This module defines the gui of a tissue pattern interactions
"""

__license__= "Cecill-C"
__revision__=" $Id: $ "

__all__ = ["TissuePainterGUI"]


import re
from PyQt4.QtCore import Qt, QObject, SIGNAL
from PyQt4.QtGui import (QAction, QIcon, QDockWidget
                       , QFileDialog, QDialog, QPixmap
                       , QColor, QSplashScreen, QApplication
                       , QMenu, QToolBar, QUndoStack, QUndoCommand)

from openalea.pglviewer import ElmGUI, SelectTool, Vec
from openalea.celltissue import topen

from tissue_property_dialog import TissuePropertyDialog
from openalea.pglviewer import ClippingProbeView
from probe_dialog_gui import ProbeGUI
from color_display_gui import ColorDisplayGUI

import tissuepainter_rc


descr_pattern = re.compile(r"values=\{(.+)\}")

class UndoPaintCommand (QUndoCommand) :
	"""Specific class used to undo-redo paint commands
	"""
	def __init__ (self, name, view, list_of_modif) :
		QUndoCommand.__init__(self, name)
		self._view = view
		self._modif = list_of_modif
	
	def undo (self) :
		change = [(cid, old_col) for cid, old_col, new_col in self._modif]
		self._view.update_colors(change)
	
	def redo (self) :
		change = [(cid, new_col) for cid, old_col, new_col in self._modif]
		self._view.update_colors(change)


class TissuePainterGUI (ElmGUI) :
	"""
	defines the user interactions for painting a mesh
	"""
	def __init__ (self, view) :
		ElmGUI.__init__(self)
		self._view = view #view associated with this gui
		
		self._splash = QSplashScreen(QPixmap(":/images/tissue_splash.png"))
		
		#tissue attributes
		self._current_filename = None#TODO
		
		#edition attributes
		self._undo_stack = QUndoStack()
		self._undo_stack.setUndoLimit(10)
		
		#probe elements
		self._probe_gui = None
	
	########################################################
	#
	#		IInteractive
	#
	########################################################
	def setup_ui (self) :
		if ElmGUI.setup_ui(self) :
			view = self._view

			################################################
			#
			#	tissue actions
			#
			################################################
			self._tissue_bar = QToolBar("tissue actions")
			self._tissue_menu = QMenu("Tissue")
			
			self._ac_open = QAction("Open", None)
			self._ac_open.setShortcut("Ctrl+O")
			self._ac_open.setIcon(QIcon(":/images/icons/load.png") )
			QObject.connect(self._ac_open
			              , SIGNAL("triggered(bool)")
			              , self.action_open)
			
			self._ac_write_state = QAction("Wite state", None)
#			self._ac_write_state.setShortcut("Ctrl+O")
			self._ac_write_state.setIcon(QIcon(":/images/icons/write.png") )
			QObject.connect(self._ac_write_state
			              , SIGNAL("triggered(bool)")
			              , self.action_write_state)
			
			self._ac_read_state = QAction("Read state", None)
#			self._ac_read_state.setShortcut("Ctrl+O")
			self._ac_read_state.setIcon(QIcon(":/images/icons/read.png") )
			QObject.connect(self._ac_read_state
			              , SIGNAL("triggered(bool)")
			              , self.action_read_state)
			
			self._tissue_menu.addAction(self._ac_open)
			self._tissue_menu.addAction(self._ac_write_state)
			self._tissue_menu.addAction(self._ac_read_state)
			
			self._tissue_bar.addAction(self._ac_open)
			self._tissue_bar.addAction(self._ac_write_state)
			self._tissue_bar.addAction(self._ac_read_state)
			
			################################################
			#
			#	edition actions
			#
			################################################
			self._edition_bar = QToolBar("edition actions")
			self._edition_tool = QToolBar("edition tools")
			self._edition_menu = QMenu("Edition")
			
			self._ac_undo = self._undo_stack.createUndoAction(None)
			self._ac_redo = self._undo_stack.createRedoAction(None)
			
			self._ac_clear_colors = QAction("Clear", None)
#			self._ac_clear_colors.setShortcut("Ctrl+O")
			self._ac_clear_colors.setIcon(QIcon(":/images/icons/clear.png") )
			QObject.connect(self._ac_clear_colors
			              , SIGNAL("triggered(bool)")
			              , self.action_clear_colors)
			
			self._ac_expand = QAction("Expand", None)
#			self._ac_expand.setShortcut("Ctrl+O")
			self._ac_expand.setIcon(QIcon(":/images/icons/expand.png") )
			QObject.connect(self._ac_expand
			              , SIGNAL("triggered(bool)")
			              , self.action_expand)
			
			self._ac_shrink = QAction("Shrink", None)
#			self._ac_shrink.setShortcut("Ctrl+O")
			self._ac_shrink.setIcon(QIcon(":/images/icons/shrink.png") )
			QObject.connect(self._ac_shrink
			              , SIGNAL("triggered(bool)")
			              , self.action_shrink)
			
			self._tool_paint = SelectTool(None,
			                              "paint",
			                               self._view.selection_draw)
			self._tool_paint.setIcon(QIcon(":/images/icons/select.png") )
			QObject.connect(self._tool_paint,
			                SIGNAL("elm selected"),
			                self.paint_cell)
			
			self._tool_fill = SelectTool(None,
			                              "fill",
			                               self._view.selection_draw)
			self._tool_fill.setIcon(QIcon(":/images/icons/fill.png") )
			QObject.connect(self._tool_fill,
			                SIGNAL("elm selected"),
			                self.fill_region)
			
			self._tool_pick = SelectTool(None,
			                             "pick color",
			                              self._view.selection_draw)
			self._tool_pick.setIcon(QIcon(":/images/icons/select.png") )#TODO
			QObject.connect(self._tool_pick,
			                SIGNAL("elm selected"),
			                self.pick_color)
			
			self._edition_menu.addAction(self._ac_undo)
			self._edition_menu.addAction(self._ac_redo)
			self._edition_menu.addSeparator()
			self._edition_menu.addAction(self._ac_clear_colors)
			self._edition_menu.addAction(self._ac_expand)
			self._edition_menu.addAction(self._ac_shrink)
			
			self._edition_bar.addAction(self._ac_undo)
			self._edition_bar.addAction(self._ac_redo)
			self._edition_bar.addSeparator()
			self._edition_bar.addAction(self._ac_clear_colors)
			self._edition_bar.addAction(self._ac_expand)
			self._edition_bar.addAction(self._ac_shrink)
			
			self._edition_tool.addAction(self._tool_paint)
			self._edition_tool.addAction(self._tool_fill)
			self._edition_tool.addAction(self._tool_pick)
			
			################################################
			#
			#	color and display management
			#
			################################################
			self._cd_widget = ColorDisplayGUI(self._view, None)
			self._cd_widget.setup_ui()
			
			self._dock_widget = QDockWidget()
			self._dock_widget.setWindowTitle("Color Display")
			self._dock_widget.setWidget(self._cd_widget)
			
			
			#connect view signals
			QObject.connect(view, SIGNAL("tissue_setted"), self.tissue_setted)
			QObject.connect(view, SIGNAL("set_normal_inside"), self.update)
			QObject.connect(view, SIGNAL("set_state"), self.update)
			QObject.connect(view, SIGNAL("clear_colors"), self.update)
			QObject.connect(view, SIGNAL("set_color"), self.update)
			QObject.connect(view, SIGNAL("update_colors"), self.update)
			QObject.connect(view, SIGNAL("del_color"), self.update)
			QObject.connect(view, SIGNAL("update_display"), self.update)
			QObject.connect(view, SIGNAL("expand"), self.update)
			QObject.connect(view, SIGNAL("shrink"), self.update)
			QObject.connect(view, SIGNAL("fill_region"), self.update)
	
	def install (self, main_window) :
		ElmGUI.install(self,main_window)
		main_window.menuBar().addMenu(self._tissue_menu)
		main_window.menuBar().addMenu(self._edition_menu)
#		main_window.menuBar().addMenu(self.ui.menuProbes)
#		main_window.menuBar().addMenu(self.ui.menuDisplay)
		self.add_action_bar(main_window, self._tissue_bar)
		self.add_action_bar(main_window, self._edition_bar)
		self.add_tool_bar(main_window, self._edition_tool)
#		main_window.addToolBar(Qt.LeftToolBarArea,self.ui.toolBar)
		main_window.addDockWidget(Qt.RightDockWidgetArea, \
		                          self._dock_widget)
		QObject.connect(self._cd_widget, SIGNAL("escape"), main_window.close)
	
	def uninstall (self, main_window) :
		ElmGUI.uninstall(self,main_window)
		main_window.menuBar().removeAction(self._tissue_menu.menuAction() )
		main_window.menuBar().removeAction(self._edition_menu.menuAction() )
#		main_window.menuBar().removeAction(self.ui.menuProbes)
#		main_window.menuBar().removeAction(self.ui.menuDisplay)
		self.remove_bar(main_window, self._tissue_bar)
		self.remove_bar(main_window, self._edition_bar)
		self.remove_bar(main_window, self._edition_tool)
#		main_window.removeToolBar(self.ui.toolBar)
		main_window.removeDockWidget(self._dock_widget)
		QObject.disconnect(self._cd_widget, SIGNAL("escape"), main_window.close)
	
	def toto (self) :
		self._mesh_view.emit(SIGNAL("toto"),)
	
	########################################################
	#
	#		accessors
	#
	########################################################
	def current_color (self) :
		return self._cd_widget.current_color()
	
	########################################################
	#
	#		tissue actions
	#
	########################################################
	def action_open (self) :
		"""Find tissue name to open it
		"""
		filename = QFileDialog.getOpenFileName()
		if not filename.isNull() :
			filename = str(filename)
			self.open_tissue(filename)
	
	def open_tissue (self, filename) :
		"""Open a new tissue file
		"""
		mw = self.installed()
		
		print "loading tissue"
		if mw is not None :
			#splash start
			mw.setEnabled(False)
			self._splash.show()
			self._splash.showMessage("Loading tissue")
			QApplication.instance().processEvents()
		
		#read info
		f = topen(filename,'r')
		t = f.read()
		self._current_filename = filename
		
		#set mesh in view
		print "Tissue loaded, computing geometry"
		if mw is not None :
			self._splash.showMessage("Tissue loaded, computing geometry")
			QApplication.instance().processEvents()
		
		self._view.set_tissue(t)
	
	def tissue_setted (self, tissue, old_tissue) :
		"""A new tissue has been set
		"""
		mw = self.installed()

		print "Computing GUI"
		if mw is not None :
			#splash
			self._splash.showMessage("Computing GUI")
			QApplication.instance().processEvents()
		
		#recomputing gui
		self._undo_stack.clear()
		if tissue is None :
			#TODO self.ui.dock_widget.setVisible(False)
			pass
		else :
			#3D view
			if mw is not None :
				view3d = mw.view()
				view3d.bound_to_worlds()
				if old_tissue is None :
					view3d.show_entire_world()
		
		if mw is not None :
			#close splash screen
			mw.setEnabled(True)
			self._splash.hide()
	
	def action_read_state (self) :
		"""Find property name to read state
		"""
		if self._current_filename is None :
			return
		
		dialog = TissuePropertyDialog(self._current_filename, 'r')
		if dialog.exec_() == dialog.Accepted :
			self.read_state(dialog.property_name())
	
	def read_state (self, property_name) :
		"""Read the state as a property inside the current
		tissue
		"""
		if self._current_filename is None :
			return
		
		f = topen(self._current_filename, 'r')
		state, descr = f.read(property_name)
		f.close()
		
		#insert new colors if necessary
		colors = set(state.itervalues() ) - set([None])
		for color_id in (colors - set(self._view.colors() ) ) :
			self._view.add_color(self._cd_widget.new_color(), color_id)
		
		#read color description
		ind = descr.find("values")
		if ind > 0 :
			m = descr_pattern.match(descr[ind:])
			if m is not None :
				col_descr = eval("{%s}" % m.groups()[0])
				#col_descr = {1:'GAN', 2:'AG'}
				for cid in set(col_descr) & colors :
					d = col_descr[cid]
					if d == "none" :
						d = None
					self._view.set_color_description(cid, d)
		
		#set state
		modif = self._view.set_state(state)
		self.push_undo_cmd("load", modif)
	
	def action_write_state (self) :
		"""Find property name to write state
		"""
		if self._current_filename is None :
			return
		
		dialog = TissuePropertyDialog(self._current_filename, 'w')
		if dialog.exec_() == dialog.Accepted :
			self.write_state(dialog.property_name())
	
	def write_state (self, property_name) :
		"""Save the current state as a property
		inside the current tissue
		"""
		if self._current_filename is None :
			return

		state = dict( (cid,col) for cid, col in self._view.state().iteritems() \
		               if col is not None)
		
		descr_items = []
		for col_id in sorted(set(state.values() ) ) :
			d = self._view.color_description(col_id)
			if d is None :
				d = "none"
			descr_items.append("%d:'%s'" % (col_id, d) )

		if len(descr_items) == 0 :
			descr = ""
		else :
			descr = "state values={%s}" % ", ".join(descr_items)
		
		f = topen(self._current_filename, 'a')
		f.write(self._view.state(), property_name, descr)
		f.close()
	
	########################################################
	#
	#		edition
	#
	########################################################
	def push_undo_cmd (self, name, list_of_modif) :
		"""Add an Undo command in the stack
		"""
		if list_of_modif is None or len(list_of_modif) == 0 :
			return
		
		cmd = UndoPaintCommand(name, self._view, list_of_modif)
		self._undo_stack.push(cmd)
	
	def action_clear_colors (self) :
		"""Clear all cell colors
		"""
		modif = self._view.clear_colors()
		self.push_undo_cmd("clear", modif)
	
	def action_expand (self) :
		"""Expand current color zone with a layer of cells
		"""
		modif = self._view.expand(self.current_color() )
		self.push_undo_cmd("expand", modif)
	
	def action_shrink (self) :
		"""Remove a layer of cells around zone with current color
		"""
		modif = self._view.shrink(self.current_color() )
		self.push_undo_cmd("shrink", modif)
	
	##############################################################
	#
	#		probes
	#
	##############################################################
	def add_probe (self) :
		"""
		add a new probe in the scene
		"""
		viewer = self._main_window
		sc = self._mesh_view
		#create probe
		bb = sc.bounding_box()
		R = max(bb.getSize() )
		pb = ClippingProbeView(sc,size = R)
		cent = Vec(*tuple(bb.getCenter() ) )
		pb.set_position(cent)
		#add probe in the view
		viewer.set_world(pb)
		#add probe gui
		self._probe_gui = viewer.add_gui(ProbeGUI(pb,self) )
	
	def remove_probe (self) :
		"""
		remove a probe once setted
		"""
		assert self._probe_gui is not None
		viewer = self._main_window
		sc = self._mesh_view
		#remove probe from the view
		viewer.set_world(sc)
		#remove probe gui
		viewer.remove_gui(self._probe_gui)
		self._probe_gui = None
	
	##############################################################
	#
	#		SIGNAL from mesh_view
	#
	##############################################################
	def update (self, *args) :
		"""Redraw the tissue and force view3D to redraw
		"""
		self._view.redraw()
		#self.update_view()
	
	##############################################################
	#
	#		selection (tools)
	#
	##############################################################
	def paint_cell (self, cid) :
		"""Paint a unique selected cell with current color
		"""
		print "paint", cid
		if cid is None :
			return
		
		modif = self._view.set_color(cid, self.current_color() )
		self.push_undo_cmd("paint", modif)
	
	def fill_region (self, cid) :
		"""Repaint all cells which are both visible and in 
		the same color region than the given cell
		"""
		print "fill", cid
		if cid is None :
			return
		
		modif = self._view.fill_region(cid, self.current_color() )
		self.push_undo_cmd("fill", modif)
	
	def pick_color (self, cid) :
		"""Change current color for the color of the selected cell
		"""
		print "col", cid
		if cid is None :
			self._cd_widget.set_current_color(None)
		else :
			self._cd_widget.set_current_color(self._view.color(cid) )

