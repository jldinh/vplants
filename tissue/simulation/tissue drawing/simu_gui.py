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
		
		self.action_display_walls = QAction(QIcon("icons/display_walls.png"),"display walls",main_window)
		self.action_display_walls.setCheckable(True)
		self.action_display_walls.setChecked(view._display_walls)
		main_window.connect(self.action_display_walls,SIGNAL("toggled(bool)"),view.display_walls)
		main_window.connect(view,SIGNAL("display_walls"),self.walls_displayed)
		
		self.action_display_cells = QAction(QIcon("icons/display_cells.png"),"display cells",main_window)
		self.action_display_cells.setCheckable(True)
		self.action_display_cells.setChecked(view._display_cells)
		main_window.connect(self.action_display_cells,SIGNAL("toggled(bool)"),view.display_cells)
		main_window.connect(view,SIGNAL("display_cells"),self.cells_displayed)
		
		self.action_display_background = QAction(QIcon("icons/display_background.png"),"display background",main_window)
		self.action_display_background.setCheckable(True)
		self.action_display_background.setChecked(view._display_background)
		main_window.connect(self.action_display_background,SIGNAL("toggled(bool)"),view.display_background)
		main_window.connect(view,SIGNAL("display_background"),self.background_displayed)
		
		self.display_toolbar = QToolBar("display",main_window)
		self.display_toolbar.addAction(self.action_display_points)
		self.display_toolbar.addAction(self.action_display_walls)
		self.display_toolbar.addAction(self.action_display_cells)
		self.display_toolbar.addAction(self.action_display_background)

	def toolbars (self) :
		return (self.display_toolbar,)
	
	def update_draw (self) :
		self.element().redraw()
		self.update_view()
	##############################################################
	#
	#		display actions
	#
	##############################################################
	def points_displayed (self, display) :
		self.action_display_points.setChecked(display)
		self.update_draw()
	
	def walls_displayed (self, display) :
		self.action_display_walls.setChecked(display)
		self.update_draw()
	
	def cells_displayed (self, display) :
		self.action_display_cells.setChecked(display)
		self.update_draw()
	
	def background_displayed (self, display) :
		self.action_display_background.setChecked(display)
		self.update_draw()
	
	
