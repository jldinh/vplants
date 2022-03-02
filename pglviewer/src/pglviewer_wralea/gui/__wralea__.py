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
node definition for pglviewer package
"""

__license__= "Cecill-C"
__revision__=" $Id: __wralea__.py 9869 2010-11-04 17:31:41Z dbarbeau $ "

from openalea.core import Factory
from openalea.core.interface import *

__name__ = "tissue.pglviewer.gui"
__alias__ = ["pglviewer.gui"]
__version__ = '0.0.2'
__license__ = "Cecill-C"
__authors__ = 'Jerome Chopard'
__institutes__ = 'INRIA/CIRAD'
__description__ = 'Pglviewer Node library.'
__url__ = 'http://openalea.gforge.inria.fr'

__all__ = []

#########################################
#
#	predefined GUI
#
#########################################
viewer_gui = Factory( name= "viewergui", 
				description= "",
				category = "",
				nodemodule = "pgldata",
				nodeclass = "viewer_gui",
				inputs=(),
				outputs=(dict(name="gui", interface=None),),
				toscriptclass_name = "viewer_gui_script",
			)

__all__.append('viewer_gui')

view3d_gui = Factory( name= "view3dgui", 
				description= "",
				category = "",
				nodemodule = "pgldata",
				nodeclass = "view3d_gui",
				inputs=(),
				outputs=(dict(name="gui", interface=None),),
				toscriptclass_name = "view3d_gui_script",
			)

__all__.append('view3d_gui')

undo_gui = Factory( name= "undogui", 
				description= "",
				category = "",
				nodemodule = "pgldata",
				nodeclass = "undo_gui",
				inputs=(),
				outputs=(dict(name="gui", interface=None),),
				toscriptclass_name = "undo_gui_script",
			)

__all__.append('undo_gui')

scene_gui = Factory( name= "scgui", 
				description= "",
				category = "",
				nodemodule = "pgldata",
				nodeclass = "scene_gui",
				inputs=(dict(name="scview", interface=None,),),
				outputs=(dict(name="gui", interface=None),),
				toscriptclass_name = "scene_gui_script",
			)

__all__.append('scene_gui')

loop_gui = Factory( name= "loopgui", 
				description= "",
				category = "",
				nodemodule = "pgldata",
				nodeclass = "loop_gui",
				inputs=(dict(name="schview", interface=None,),),
				outputs=(dict(name="gui", interface=None),),
				toscriptclass_name = "loop_gui_script",
			)

__all__.append('loop_gui')

color_scale_gui = Factory( name= "cmapgui", 
				description= "",
				category = "",
				nodemodule = "pgldata",
				nodeclass = "color_scale_gui",
				inputs=(dict(name="title", interface=IStr, value="scale"),
				        dict(name="cfunc", interface=None),
				        dict(name="template", interface=IStr, value="%.2f"),),
				outputs=(dict(name="gui", interface=None),),
				toscriptclass_name = "color_scale_gui_script",
			)

__all__.append('color_scale_gui')

probe_gui = Factory( name= "probegui", 
				description= "",
				category = "",
				nodemodule = "pgldata",
				nodeclass = "probe_gui",
				inputs=(dict(name="probeview", interface=None,),),
				outputs=(dict(name="gui", interface=None),),
				toscriptclass_name = "probe_gui_script",
			)

__all__.append('probe_gui')

#########################################
#
#	user GUI
#
#########################################
template_gui = Factory( name= "tplgui", 
				description= "",
				category = "",
				nodemodule = "pgldata",
				nodeclass = "create_template_gui",
				inputs=(dict(name="name", interface=IStr,),
				        dict(name="actions", interface=ISequence, value=None),
				        dict(name="tools", interface=ISequence, value=None),
				        dict(name="create menu", interface=IBool, value=False),
				        dict(name="tools position", interface=IStr, value="left"),),
				outputs=(dict(name="gui", interface=None),),
				toscriptclass_name = "create_template_gui_script",
			)

__all__.append('template_gui')

create_action = Factory( name= "action", 
				description= "",
				category = "",
				nodemodule = "pgldata",
				nodeclass = "create_action_descr",
				inputs=(dict(name="func", interface=None,),
				        dict(name="name_or_icon", interface=IStr),
				        dict(name="descr", interface=IStr, value=""),),
				outputs=(dict(name="action descr", interface=None),),
				toscriptclass_name = "create_action_descr_script",
			)

__all__.append('create_action')

create_tool = Factory( name= "tool", 
				description= "",
				category = "",
				nodemodule = "pgldata",
				nodeclass = "create_tool_descr",
				inputs=(dict(name="func", interface=None,),
				        dict(name="draw func", interface=None,),
				        dict(name="name_or_icon", interface=IStr),
				        dict(name="descr", interface=IStr, value=""),),
				outputs=(dict(name="tool descr", interface=None),),
				toscriptclass_name = "create_tool_descr_script",
			)

__all__.append('create_tool')

#########################################
#
#	sch GUI
#
#########################################
counter = Factory( name= "countergui", 
				description= "",
				category = "",
				nodemodule = "pgldata",
				nodeclass = "CounterGUI",
				inputs=(dict(name="cycle", interface=IInt, value=0),),
				outputs=(dict(name="gui", interface=None),),
			)

__all__.append('counter')


