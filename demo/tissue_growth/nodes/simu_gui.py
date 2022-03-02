# -*- python -*-
#
#       simulation.global growth: example simulation package of global growth field
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
__revision__=" $Id: simu_gui.py 7897 2010-02-09 09:06:21Z cokelaer $ "

from PyQt4.QtCore import SIGNAL
from PyQt4.QtGui import QAction,QIcon,QToolBar,QActionGroup
from openalea.pglviewer import ElmGUI

import images_rc

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
		self.action_display_pid = QAction(QIcon(":/icons/icons/display_pid.png"),"display pid",main_window)
		self.action_display_pid.setCheckable(True)
		self.action_display_pid.setChecked(view._display_pid)
		main_window.connect(self.action_display_pid,SIGNAL("toggled(bool)"),view.display_pid)
		main_window.connect(view,SIGNAL("display_pid"),self.pid_displayed)
		
		self.action_display_wid = QAction(QIcon(":/icons/icons/display_wid.png"),"display wid",main_window)
		self.action_display_wid.setCheckable(True)
		self.action_display_wid.setChecked(view._display_wid)
		main_window.connect(self.action_display_wid,SIGNAL("toggled(bool)"),view.display_wid)
		main_window.connect(view,SIGNAL("display_wid"),self.wid_displayed)
		
		self.action_display_cid = QAction(QIcon(":/icons/icons/display_cid.png"),"display cid",main_window)
		self.action_display_cid.setCheckable(True)
		self.action_display_cid.setChecked(view._display_cid)
		main_window.connect(self.action_display_cid,SIGNAL("toggled(bool)"),view.display_cid)
		main_window.connect(view,SIGNAL("display_cid"),self.cid_displayed)
		
		self.action_display_wall = QAction(QIcon(":/icons/icons/display_wall.png"),"display wall",main_window)
		self.action_display_wall.setCheckable(True)
		self.action_display_wall.setChecked(view._display_wall)
		main_window.connect(self.action_display_wall,SIGNAL("toggled(bool)"),view.display_wall)
		main_window.connect(view,SIGNAL("display_wall"),self.wall_displayed)
		
		self.action_display_age = QAction(QIcon(":/icons/icons/display_age.png"),"display age",main_window)
		self.action_display_age.setCheckable(True)
		self.action_display_age.setChecked(view._display_age)
		main_window.connect(self.action_display_age,SIGNAL("toggled(bool)"),view.display_age)
		main_window.connect(view,SIGNAL("display_age"),self.age_displayed)
		
		self.action_display_morphogen = QAction(QIcon(":/icons/icons/display_morphogen.png"),"display morphogen",main_window)
		self.action_display_morphogen.setCheckable(True)
		self.action_display_morphogen.setChecked(view._display_morphogen)
		main_window.connect(self.action_display_morphogen,SIGNAL("toggled(bool)"),view.display_morphogen)
		main_window.connect(view,SIGNAL("display_morphogen"),self.morphogen_displayed)
		
		self.group_display_cell = QActionGroup(main_window)
		self.group_display_cell.addAction(self.action_display_morphogen)
		self.group_display_cell.addAction(self.action_display_age)
		
		self.display_toolbar = QToolBar("display",main_window)
		self.display_toolbar.addAction(self.action_display_pid)
		self.display_toolbar.addAction(self.action_display_wid)
		self.display_toolbar.addAction(self.action_display_cid)
		self.display_toolbar.addAction(self.action_display_wall)
		self.display_toolbar.addSeparator()
		self.display_toolbar.addAction(self.action_display_age)
		self.display_toolbar.addAction(self.action_display_morphogen)
	
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
	def pid_displayed (self, display) :
		self.action_display_pid.setChecked(display)
		self.update_draw()
	
	def wid_displayed (self, display) :
		self.action_display_wid.setChecked(display)
		self.update_draw()
	
	def cid_displayed (self, display) :
		self.action_display_cid.setChecked(display)
		self.update_draw()
	
	def wall_displayed (self, display) :
		self.action_display_wall.setChecked(display)
		self.update_draw()
	
	def age_displayed (self, display) :
		self.action_display_age.setChecked(display)
		self.update_draw()
	
	def morphogen_displayed (self, display) :
		self.action_display_morphogen.setChecked(display)
		self.update_draw()

