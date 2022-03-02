# -*- python -*-
#
#       simulation.template: example simulation package
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
This module defines the gui of a simulation
"""

__license__= "Cecill-C"
__revision__=" $Id: $ "

from PyQt4.QtCore import SIGNAL
from PyQt4.QtGui import QToolBar,QDockWidget,QWidget,QComboBox,\
						QIcon,QAction
from openalea.pglviewer import ElmGUI
from simu_ui import Ui_Form

style_list = ["wire","fill","nurbs"]

class SimuGUI (ElmGUI) :
	"""
	defines the user interactions during the simulation
	"""
	def __init__ (self, simu_view) :
		ElmGUI.__init__(self)
		self.install(simu_view)
	###############################################################
	#
	#		IInteractive
	#
	###############################################################
	def setup_ui (self, main_window) :
		ElmGUI.setup_ui(self)
		view = self.element()
		
		self.action_reload_tissue = QAction(QIcon("icons/reload_tissue.png"),"reload tissue",main_window)
		main_window.connect(self.action_reload_tissue,SIGNAL("activated()"),self.reload_tissue)
		
		self.display_style_select = QComboBox()
		for style in style_list :
			self.display_style_select.addItem(style)
		self.display_style_select.setCurrentIndex(style_list.index(view._display_style))
		main_window.connect(self.display_style_select,SIGNAL("activated(const QString&)"),view.display_style)
		main_window.connect(view,SIGNAL("display_style"),self.style_changed)
			
		self.action_display_cids = QAction(QIcon("icons/display_cids.png"),"display cids",main_window)
		self.action_display_cids.setCheckable(True)
		self.action_display_cids.setChecked(view._display_cids)
		main_window.connect(self.action_display_cids,SIGNAL("toggled(bool)"),view.display_cids)
		main_window.connect(view,SIGNAL("display_cids"),self.cids_displayed)
		
		self.toolbar = QToolBar("pattern")
		self.toolbar.addAction(self.action_reload_tissue)
		self.toolbar.addWidget(self.display_style_select)
		self.toolbar.addAction(self.action_display_cids)
		
		self.dock_widget = QDockWidget()
		self.division_widget = QWidget()
		self.division_ui = Ui_Form()
		self.division_ui.setupUi(self.division_widget)
		self.dock_widget.setWidget(self.division_widget)
		
		#connection SIGNAL SLOT
		main_window.connect(self.division_ui.applyButton,SIGNAL("clicked()"),self.divide_cell)
		main_window.connect(self.division_ui.applyAllButton,SIGNAL("clicked()"),self.divide_all_cells)
	
	def toolbars (self) :
		return (self.toolbar,)
	
	def docked_widgets (self) :
		return ((self.dock_widget,True),)
	#########################################
	#
	#	methods
	#
	#########################################
	def update_draw (self) :
		self.element().redraw()
		self.update_view()
	
	def selected_cell (self) :
		"""
		return id of current selected cell
		"""
		#validate selected cell
		cid_str = str(self.division_ui.selectedCellEdit.text())
		try :
			return int(cid_str)
			if not self.element().mesh.has_wisp(2,cid) :
				raise UserWarning("invalid cell")
		except ValueError :
			raise UserWarning("invalid literal for cell id")
	
	def retrieve_weights (self) :
		"""
		find weights
		"""
		main_axis_weight = self.division_ui.mainAxisSlider.value()
		smallest_wall_weight = self.division_ui.smallWallSlider.value()
		perpendicular_weight = self.division_ui.perpendicularSlider.value()
		daughters_size_weight = self.division_ui.daughtersSizeSlider.value()
		tot = main_axis_weight + smallest_wall_weight + perpendicular_weight + daughters_size_weight
		if tot == 0 :
			raise UserWarning("at least one argument must have some weight")
		tot = float(tot)
		main_axis_weight /= tot
		smallest_wall_weight /= tot
		perpendicular_weight /= tot
		daughters_size_weight /= tot
		return main_axis_weight,smallest_wall_weight,perpendicular_weight,daughters_size_weight
		
	def retrieve_shrink_factor (self) :
		"""
		find shrink factor
		"""
		shrink_factor = self.division_ui.shrinkSpinBox.value()
		return shrink_factor
	
	def retrieve_precision (self) :
		"""
		find precision
		"""
		precision = self.division_ui.precisionSlider.value()
		return precision
	
	def cell_division (self, cid, precision, weights, shrink_factor) :
		"""
		divide a cell
		"""
		main_axis_weight,smallest_wall_weight,perpendicular_weight,daughters_size_weight = weights
		point,axis = self.element().test_cell_division (cid,precision,
														main_axis_weight,
														smallest_wall_weight,
														perpendicular_weight,
														daughters_size_weight)
		self.element().divide_cell_full(cid,point,axis,shrink_factor)
	#########################################
	#
	#	actions
	#
	#########################################
	def reload_tissue (self) :
		self.element().reload_tissue()
		self.update_draw()
	
	def style_changed (self, style) :
		ind = self.display_style_select.findText(style)
		if ind == -1 :
			raise UserWarning("unable to find style: %s" % style)
		self.display_style_select.setCurrentIndex(ind)
		self.update_draw()
	
	def cids_displayed (self, display) :
		self.action_display_cids.setChecked(display)
		self.update_draw()
	
	def divide_cell (self) :
		cid = self.selected_cell()
		weights = self.retrieve_weights()
		shrink_factor = self.retrieve_shrink_factor()
		prec = self.retrieve_precision()
		self.cell_division(cid,prec,weights,shrink_factor)
		self.update_draw()

	def divide_all_cells (self) :
		weights = self.retrieve_weights()
		shrink_factor = self.retrieve_shrink_factor()
		prec = self.retrieve_precision()
		for cid in list(self.element().mesh.wisps(2)) :
			self.cell_division(cid,prec,weights,shrink_factor)
			self.update_draw()
			

