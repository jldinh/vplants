# -*- python -*-
#
#       simulation.3points bending: example simulation package for mass spring systems
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
from PyQt4.QtGui import QAction,QIcon
from openalea.pglviewer import ElmGUI

from simu_ui import Ui_MainWindow

class SimuGUI (ElmGUI) :
	"""
	defines the user interactions during the simulation
	"""
	def __init__ (self, simu_view) :
		ElmGUI.__init__(self,simu_view)
		self.ui=Ui_MainWindow()
	
	###############################################################
	#
	#		IInteractive
	#
	###############################################################
	def setup_ui (self, main_window) :
		ElmGUI.setup_ui(self,main_window)
		ui=self.ui
		ui.setupUi(main_window)
		view=self.element()
		
		ui.actionDisplay_pid.setChecked(view._display_pid)
		main_window.connect(ui.actionDisplay_pid,SIGNAL("toggled(bool)"),view.display_pid)
		main_window.connect(view,SIGNAL("display_pid"),self.pid_displayed)		ui.actionDisplay_fixed.setChecked(view._display_fixed)
		main_window.connect(ui.actionDisplay_fixed,SIGNAL("toggled(bool)"),view.display_fixed)
		main_window.connect(view,SIGNAL("display_fixed"),self.fixed_displayed)		ui.actionDisplay_top.setChecked(view._display_top)
		main_window.connect(ui.actionDisplay_top,SIGNAL("toggled(bool)"),view.display_top)
		main_window.connect(view,SIGNAL("display_top"),self.top_displayed)		ui.actionDisplay_load.setChecked(view._display_load)
		main_window.connect(ui.actionDisplay_load,SIGNAL("toggled(bool)"),view.display_load)
		main_window.connect(view,SIGNAL("display_load"),self.load_displayed)	
	def toolbars (self) :
		return (self.ui.toolBar,)
	##############################################################
	#
	#		specific actions
	#
	##############################################################
	def pid_displayed (self, display) :
		self.ui.actionDisplay_pid.setChecked(display)
		self.update_view()
	
	def fixed_displayed (self, display) :
		self.ui.actionDisplay_fixed.setChecked(display)
		self.update_view()
	
	def top_displayed (self, display) :
		self.ui.actionDisplay_top.setChecked(display)
		self.update_view()
	
	def load_displayed (self, display) :
		self.ui.actionDisplay_load.setChecked(display)
		self.update_view()


