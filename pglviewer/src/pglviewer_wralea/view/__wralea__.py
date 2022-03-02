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

__name__ = "tissue.pglviewer.view"
__alias__ = ["pglviewer.view"]
__version__ = '0.0.2'
__license__ = "Cecill-C"
__authors__ = 'Jerome Chopard'
__institutes__ = 'INRIA/CIRAD'
__description__ = 'Pglviewer Node library.'
__url__ = 'http://openalea.gforge.inria.fr'

__all__ = []

#########################################
#
#	view
#
#########################################
scene_view = Factory( name= "scene", 
				description= "",
				category = "",
				nodemodule = "pgldata",
				nodeclass = "scene_view",
				inputs=(dict(name="sc", interface=None,),),
				outputs=(dict(name="view", interface=None),
				         dict(name="select", interface=IFunction),),
				toscriptclass_name = "scene_view_script",
			)

__all__.append('scene_view')

#########################################
#
#	loop
#
#########################################
loop_view = Factory( name= "loop", 
				description= "",
				category = "",
				nodemodule = "pgldata",
				nodeclass = "loop_view",
				inputs=(dict(name="sch", interface=None,),),
				outputs=(dict(name="loop", interface=None),),
				toscriptclass_name = "loop_view_script",
			)

__all__.append('loop_view')

#########################################
#
#	probe
#
#########################################
probe_view = Factory( name= "probe", 
				description= "",
				category = "",
				nodemodule = "pgldata",
				nodeclass = "probe_view",
				inputs=(dict(name="worlds", interface=None,),),
				outputs=(dict(name="probe", interface=None),
				         dict(name="select", interface=IFunction),),
				toscriptclass_name = "probe_view_script",
			)

__all__.append('probe_view')

