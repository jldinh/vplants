# -*- python -*-
#
#       pglviewer: display GUI
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
"""
Expose the viewer as a visualea node
"""

__license__= "Cecill-C"
__revision__=" $Id: viewer.py 8836 2010-05-07 12:32:29Z chopard $ "

from openalea.visualea.node_widget import NodeWidget
from openalea.pglviewer import Viewer,ElmView,ElmGUI

class ViewerFunctor (object) :
	def __init__ (self) :
		self._viewer = None
	
	def set_viewer (self, viewer) :
		self._viewer = viewer
	
	def __call__ (self, world_list, gui_list) :
		return self._viewer,

class ViewerWidget(NodeWidget, Viewer):
	"""
	Node Widget associated to a pgl Viewer
	"""
	
	def __init__(self, node, parent) :
		"""
		"""
		Viewer.__init__(self, parent)
		NodeWidget.__init__(self, node)
		
		self.notify(node,("caption_modified",node.get_caption() ) )
		self.notify(node,("input_modified",0) )
		self.notify(node,("input_modified",1) )
		
		node.func.set_viewer(self)
		node.set_output(0,self)
	
	def notify(self, sender, event):
		"""Notification sent by node
		"""
		if event[0] == 'caption_modified' :
			self.window().setWindowTitle(event[1])
		
		elif event[0] == 'input_modified' :
			#worlds
			if event[1] == 0 :
				self.clear_worlds()
				world_list = self.node.get_input(0)
				if world_list is not None :
					if isinstance(world_list,ElmView) :
						self.add_world(world_list)
					else :
						for world in world_list :
							self.add_world(world)
				
				self.view().bound_to_worlds()
				if not self.isVisible() :
					self.view().show_entire_world()
			#GUI
			if event[1] == 1 :
				self.clear_guis()
				GUI_list = self.node.get_input(1)
				if GUI_list is not None :
					if isinstance(GUI_list,ElmGUI) :
						self.add_gui(GUI_list)
					else :
						for gui in GUI_list :
							self.add_gui(gui)


class ViewerWidget2D(ViewerWidget):
	"""
	Node Widget associated to a pgl Viewer 2D
	"""
	
	def __init__(self, node, parent) :
		"""
		"""
		ViewerWidget.__init__(self,node,parent)
		self.view().set_dimension(2)



