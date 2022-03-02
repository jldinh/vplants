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
basic function for pglviewer
"""

__license__= "Cecill-C"
__revision__=" $Id: viewer.py 8836 2010-05-07 12:32:29Z chopard $ "

from openalea.core import ScriptLibrary
from openalea.pglviewer import Viewer,ElmView,ElmGUI

def display (world_list, GUI_list, is_2D, associated_viewers, title) :
	"""Create a Viewer and display things.
	"""
	v = Viewer()
	
	#worlds
	if world_list is not None :
		if isinstance(world_list,ElmView) :
			v.add_world(world_list)
		else :
			for world in world_list :
				v.add_world(world)
	
	#GUI
	if GUI_list is not None :
		if isinstance(GUI_list,ElmGUI) :
			v.add_gui(GUI_list)
		else :
			for gui in GUI_list :
				v.add_gui(gui)
	
	#associated_viewers
	if associated_viewers is not None :
		try :
			for viewer in associated_viewers :
				v.synchronize(viewer)
		except TypeError :
			v.synchronize(associated_viewers)
	
	#title
	if title != "" :
		v.setWindowTitle(title)
	
	#display
	v.show()
	if is_2D :
		v.view().set_dimension(2)
	
	v.view().show_entire_world()
	
	#return
	return v,

def display_script (inputs, outputs) :
	lib = ScriptLibrary()
	world_list,GUI_list,is_2D,associated_viewers,title = inputs
	v, = outputs
	v = lib.register(v,"viewer")
	
	script = "from openalea.pglviewer import QApplication,Viewer\n"
	script += "qapp = QApplication([])\n\n"
	
	script += "%s = Viewer()\n" % v
	
	#worlds
	if world_list is not None :
		if isinstance(world_list,ElmView) :
			world,script = lib.name(world_list,script)
			script += "%s.add_world(%s)\n" % (v,world)
		else :
			for world in world_list :
				world,script = lib.name(world,script)
				script += "%s.add_world(%s)\n" % (v,world)
	#GUI
	if GUI_list is not None :
		try :
			for gui in GUI_list :
				gui,script = lib.name(gui,script)
				script += "%s.add_gui(%s)\n" % (v,gui)
		except TypeError :
			gui,script = lib.name(GUI_list,script)
			script += "%s.add_gui(%s)\n" % (v,gui)
	
	#associated_viewers
	if associated_viewers is not None :
		try :
			for viewer in associated_viewers :
				viewer,script = lib.name(viewer,script)
				script += "%s.synchronize(%s)\n" % (v,viewer)
		except TypeError :
			viewer,script = lib.name(associated_viewers,script)
			script += "%s.synchronize(%s)\n" % (v,viewer)
	
	#title
	if title != "" :
		script += "%s.setWindowTitle('%s')\n" % (v,title)
	
	#display
	script += "%s.show()\n" % v
	if is_2D :
		script += "%s.view().set_dimension(2)\n" % v
	
	script += "%s.view().show_entire_world()\n" % v
	script += "qapp.exec_()\n"
	
	return script

