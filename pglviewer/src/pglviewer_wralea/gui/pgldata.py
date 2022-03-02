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
data embbeding function for pglviewer
"""

__license__= "Cecill-C"
__revision__=" $Id: pgldata.py 9205 2010-07-01 15:49:20Z chopard $ "

from os.path import basename,splitext,join
from PyQt4.QtCore import Qt
from PyQt4.QtGui import QIcon,QLineEdit
from openalea.core import ScriptLibrary
from openalea.pglviewer import ElmGUI

############################################
#
#	predefined GUI
#
############################################
def viewer_gui () :
	from openalea.pglviewer import ViewerGUI
	return ViewerGUI(vars() ),

def viewer_gui_script (inputs, outputs) :
	lib = ScriptLibrary()
	gui, = outputs
	gui = lib.register(gui,"gui")
	
	script = "from openalea.pglviewer import ViewerGUI\n"
	script += "%s = ViewerGUI(vars() )\n" % gui
	
	return script

def view3d_gui () :
	from openalea.pglviewer import View3DGUI
	return View3DGUI(),

def view3d_gui_script (inputs, outputs) :
	lib = ScriptLibrary()
	gui, = outputs
	gui = lib.register(gui,"gui")
	
	script = "from openalea.pglviewer import View3DGUI\n"
	script += "%s = View3DGUI()\n" % gui
	
	return script

def undo_gui () :
	from openalea.pglviewer import UndoGUI
	return UndoGUI(),

def undo_gui_script (inputs, outputs) :
	lib = ScriptLibrary()
	gui, = outputs
	gui = lib.register(gui,"gui")
	
	script += "from openalea.pglviewer import UndoGUI\n"
	script += "%s = UndoGUI()\n" % gui
	
	return script

def scene_gui (scene_view) :
	from openalea.pglviewer import SceneGUI
	return SceneGUI(scene_view),

def scene_gui_script (inputs, outputs) :
	lib = ScriptLibrary()
	view, = inputs
	view,script = lib.name(view,"")
	gui, = outputs
	gui = lib.register(gui,"gui")
	
	script += "from openalea.pglviewer import SceneGUI\n"
	script += "%s = SceneGUI(%s)\n" % (gui,view)
	
	return script

def loop_gui (loop_view) :
	from openalea.pglviewer import LoopGUI
	return LoopGUI(loop_view),

def loop_gui_script (inputs, outputs) :
	lib = ScriptLibrary()
	view, = inputs
	view,script = lib.name(view,"")
	gui, = outputs
	gui = lib.register(gui,"gui")
	
	script += "from openalea.pglviewer import LoopGUI\n"
	script += "%s = LoopGUI(%s)\n" % (gui,view)
	
	return script

def color_scale_gui (title, color_map_func, template) :
	from openalea.pglviewer import ColorScaleGUI
	return ColorScaleGUI(title,color_map_func,template),

def color_scale_gui_script (inputs, outputs) :
	lib = ScriptLibrary()
	title,color_map_func,template = inputs
	cmap,script = lib.name(color_map_func,"")
	gui, = outputs
	gui = lib.register(gui,"gui")
	
	script += "from openalea.pglviewer import ColorScaleGUI\n"
	script += "%s = ColorScaleGUI('%s',%s,'%s')\n" % (gui,title,cmap,template)
	
	return script

def probe_gui (probe_view) :
	from openalea.pglviewer import ClippingProbeGUI
	return ClippingProbeGUI(probe_view),

def probe_gui_script (inputs, outputs) :
	lib = ScriptLibrary()
	view, = inputs
	view,script = lib.name(view,"")
	gui, = outputs
	gui = lib.register(gui,"gui")
	
	script += "from openalea.pglviewer import ClippingProbeGUI\n"
	script += "%s = ClippingProbeGUI(%s)\n" % (gui,view)
	
	return script

#########################################
#
#	user GUI
#
#########################################
def create_template_gui (name, actions, tools, create_menu, tools_position) :
	"""Create a template GUI and fill it with actions.
	"""
	from openalea.pglviewer import TemplateGUI
	gui = TemplateGUI(name)
	
	#actions
	if actions is not None :
		if type(actions[0]) == str :
			gui.add_action_descr(*actions)
		else :
			for action in actions :
				gui.add_action_descr(*action)
	
	#tools
	if tools is not None :
		if type(tools[0]) == str :
			gui.add_tool_descr(*tools)
		else :
			for tool in tools :
				gui.add_tool_descr(*tool)
	
	gui.set_tools_position(tools_position)
	
	#return
	return gui,

def create_template_gui_script (inputs, outputs) :
	lib = ScriptLibrary()
	name,actions,tools,create_menu,tools_position = inputs
	gui, = outputs
	gui = lib.register(gui,"gui")
	
	script = "from openalea.pglviewer import TemplateGUI\n"
	script += "%s = TemplateGUI('%s')\n" % (gui,name)
	
	#actions
	if actions is not None :
		try :
			for action in actions :
				action,script = lib.name(action,script)
				script += "%s.add_action_descr(*%s)\n" % (gui,action)
		except TypeError :
			action,script = lib.name(actions,script)
			script += "%s.add_action_descr(*%s)\n" % (gui,action)
	
	#tools
	if tools is not None :
		try :
			for tool in tools :
				tool,script = lib.name(tool,script)
				script += "%s.add_tool_descr(*%s)\n" % (gui,tool)
		except TypeError :
			tool,script = lib.name(tools,script)
			script += "%s.add_tool_descr(*%s)\n" % (gui,tool)
	
	return script

def create_action_descr (func, name_or_icon, descr) :
	if name_or_icon.endswith(".png") :
		name = splitext(basename(name_or_icon) )[0]
		icon = QIcon(name_or_icon)
	else :
		name = name_or_icon
		icon = None
	
	return (name,func,icon,descr),

def create_action_descr_script (inputs, outputs) :
	lib = ScriptLibrary()
	func,name_or_icon,descr = inputs
	func,script = lib.name(func,"")
	action, = outputs
	lib.register(action,"action")
	
	if name_or_icon.endswith(".png") :
		name = splitext(basename(name_or_icon) )[0]
		script += "from PyQt4.QtGui import QIcon\n"
		script += "%s = ('%s',%s,QIcon('%s'),'%s')\n" % (action,
		                                                 name,
		                                                 func,
		                                                 name_or_icon,
		                                                 descr)
	else :
		script += "%s = ('%s',%s,None,'%s')\n" % (action,
		                                          name_or_icon,
		                                          func,
		                                          descr)
	
	return script

def create_tool_descr (func, draw_func, name_or_icon, descr) :
	if name_or_icon.endswith(".png") :
		name = splitext(basename(name_or_icon) )[0]
		icon = QIcon(name_or_icon)
	else :
		name = name_or_icon
		icon = None
	
	return (name,func,draw_func,icon,descr),

def create_tool_descr_script (inputs, outputs) :
	lib = ScriptLibrary()
	func,draw_func,name_or_icon,descr = inputs
	func,script = lib.name(func,"")
	draw_func,script = lib.name(draw_func,script)
	tool, = outputs
	lib.register(tool,"tool")
	
	if name_or_icon.endswith(".png") :
		name = splitext(basename(name_or_icon) )[0]
		script += "from PyQt4.QtGui import QIcon\n"
		script += "%s = ('%s',%s,%s,QIcon('%s'),'%s')\n" % (tool,
		                                              name,
		                                              func,
		                                              draw_func,
		                                              name_or_icon,
		                                              descr)
	else :
		script += "%s = ('%s',%s,%s,None,'%s')\n" % (tool,
		                                       name_or_icon,
		                                       func,
		                                       draw_func,
		                                       descr)
	
	return script

#########################################
#
#	scheduler GUI
#
#########################################
class CounterGUI (ElmGUI) :
	"""Display the value of a counter
	"""
	def __init__ (self) :
		ElmGUI.__init__(self)
		self._step = None
		self._step_ui = None
	
	def setup_ui (self) :
		if ElmGUI.setup_ui(self) :
			self._step_ui = QLineEdit("")
			self._step_ui.setMaximumWidth(50)
			self._step_ui.setAlignment(Qt.AlignRight)
			
			if self._step is not None :
				self._step_ui.setText("%d" % self._step)
	
	def clean (self) :
		pass
	
	def install (self, main_window) :
		ElmGUI.install(self,main_window)
		self.add_status_widget(main_window,self._step_ui,False)
	
	def uninstall (self, main_window) :
		ElmGUI.uninstall(self,main_window)
		self.remove_status_widget(main_window,self._step_ui)
	
	def __call__ (self, cycle) :
		self._step = cycle
		if self._step_ui is not None :
			self._step_ui.setText("%d" % cycle)
		
		return self,

