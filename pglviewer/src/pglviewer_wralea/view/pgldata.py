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
__revision__=" $Id: pgldata.py 7881 2010-02-08 18:33:35Z cokelaer $ "

from openalea.core import ScriptLibrary

############################################
#
#	view
#
############################################
def scene_view (scene) :
	from openalea.pglviewer import SceneView
	view = SceneView(scene)
	return view,view.selection_draw

def scene_view_script (inputs, outputs) :
	lib = ScriptLibrary()
	obj, = inputs
	obj,script = lib.name(obj,"")
	view,select =outputs
	view = lib.register(view,"view")
	select = lib.register(select,"select_func")
	
	script += "from openalea.pglviewer import SceneView\n"
	script += "%s = SceneView(%s)\n" % (view,obj)
	script += "%s = %s.selection_draw\n" % (select,view)
	
	return script

############################################
#
#	loop
#
############################################
def loop_view (scheduler) :
	from openalea.pglviewer import LoopView
	loop = LoopView(scheduler)
	return loop,

def loop_view_script (inputs, outputs) :
	lib = ScriptLibrary()
	obj, = inputs
	obj,script = lib.name(obj,"")
	view, =outputs
	view = lib.register(view,"view")
	
	script += "from openalea.pglviewer import LoopView\n"
	script += "%s = LoopView(%s)\n" % (view,obj)
	
	return script

############################################
#
#	probe
#
############################################
def probe_view (world_list) :
	from openalea.pglviewer import ElmView,ClippingProbeView
	probe = ClippingProbeView()
	
	#worlds
	if world_list is not None :
		if isinstance(world_list,ElmView) :
			probe.add_world(world_list)
		else :
			for world in world_list :
				probe.add_world(world)
	
	#update size
	#TODO
	
	return probe,probe.selection_draw

def probe_view_script (inputs, outputs) :
	from openalea.pglviewer import ElmView
	lib = ScriptLibrary()
	world_list, = inputs
	view,select =outputs
	view = lib.register(view,"view")
	select = lib.register(select,"select_func")
	
	script = "from openalea.pglviewer import ClippingProbeView\n"
	script += "%s = ClippingProbeView()\n" % view
	
	#worlds
	if world_list is not None :
		if isinstance(world_list,ElmView) :
			world,script = lib.name(world_list,script)
			script += "%s.add_world(%s)\n" % (view,world)
		else :
			for world in world_list :
				world,script = lib.name(world,script)
				script += "%s.add_world(%s)\n" % (view,world)
	
	script += "%s = %s.selection_draw\n" % (select,view)
	
	return script


