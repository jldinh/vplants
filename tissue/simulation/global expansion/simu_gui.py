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
from PyQt4.QtGui import QAction,QIcon,QToolBar
from openalea.pglviewer import ElmGUI

class SimuGUI (ElmGUI) :
	"""
	defines the user interactions during the simulation
	"""
	def __init__ (self, simu_view) :
		ElmGUI.__init__(self,simu_view)
	
	def setup_ui (self, main_window) :
		ElmGUI.setup_ui(self,main_window)
		view=self.element()
		#display
		self.action_display_points = QAction(QIcon("icons/display_points.png"),"display points",main_window)
		self.action_display_points.setCheckable(True)
		self.action_display_points.setChecked(view._display_points)
		main_window.connect(self.action_display_points,SIGNAL("toggled(bool)"),view.display_points)
		main_window.connect(view,SIGNAL("display_points"),self.points_displayed)
		
		self.action_display_pids = QAction(QIcon("icons/display_pids.png"),"display pids",main_window)
		self.action_display_pids.setCheckable(True)
		self.action_display_pids.setChecked(view._display_pids)
		main_window.connect(self.action_display_pids,SIGNAL("toggled(bool)"),view.display_pids)
		main_window.connect(view,SIGNAL("display_pids"),self.pids_displayed)
		
		self.action_display_mesh = QAction(QIcon("icons/display_mesh.png"),"display mesh",main_window)
		self.action_display_mesh.setCheckable(True)
		self.action_display_mesh.setChecked(view._display_mesh)
		main_window.connect(self.action_display_mesh,SIGNAL("toggled(bool)"),view.display_mesh)
		main_window.connect(view,SIGNAL("display_mesh"),self.mesh_displayed)
		
		self.action_display_field = QAction(QIcon("icons/display_field.png"),"display field",main_window)
		self.action_display_field.setCheckable(True)
		self.action_display_field.setChecked(view._display_field)
		main_window.connect(self.action_display_field,SIGNAL("toggled(bool)"),view.display_field)
		main_window.connect(view,SIGNAL("display_field"),self.field_displayed)
		
		self.display_toolbar = QToolBar("display",main_window)
		self.display_toolbar.addAction(self.action_display_points)
		self.display_toolbar.addAction(self.action_display_pids)
		self.display_toolbar.addAction(self.action_display_mesh)
		self.display_toolbar.addAction(self.action_display_field)

	def toolbars (self) :
		return (self.display_toolbar,)
	
	def update_draw (self) :
		time = self.view().loop().current_value()
		self.element().redraw(time)
		self.update_view()
	##############################################################
	#
	#		display actions
	#
	##############################################################
	def points_displayed (self, display) :
		self.action_display_points.setChecked(display)
		self.update_draw()
	
	def pids_displayed (self, display) :
		self.action_display_pids.setChecked(display)
		self.update_draw()
	
	def mesh_displayed (self, display) :
		self.action_display_mesh.setChecked(display)
		self.update_draw()
	
	def field_displayed (self, display) :
		self.action_display_field.setChecked(display)
		self.update_draw()
	

