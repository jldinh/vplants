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

__name__ = "tissue.pglviewer"
__alias__ = ['pglviewer']
__version__ = '0.0.2'
__license__ = "Cecill-C"
__authors__ = 'Jerome Chopard'
__institutes__ = 'INRIA/CIRAD'
__description__ = 'Pglviewer Node library.'
__url__ = 'http://openalea.gforge.inria.fr'

__all__ = []

#########################################
#
#	Viewer
#
#########################################
viewer = Factory( name= "viewer", 
				description= "",
				category = "",
				nodemodule = "viewer",
				nodeclass = "display",
				inputs=(dict(name="world", interface=None,),
				        dict(name="GUI", interface=None,),
				        dict(name="is2D", interface=IBool, value=False),
				        dict(name="asso viewers", interface=None),
				        dict(name="title", interface=IStr, value="Viewer"),),
				outputs=(dict(name="viewer", interface=None,),),
				lazy = False,
				toscriptclass_name = "display_script",
			)

__all__.append('viewer')

viewer_widget = Factory( name= "ViewerW", 
				description= "",
				category = "",
				nodemodule = "viewer_widget",
				nodeclass = "ViewerFunctor",
				widgetmodule = "viewer_widget",
				widgetclass = "ViewerWidget",
				inputs=(dict(name="world", interface=None,),
				        dict(name="GUI", interface=None,),),
				outputs=(dict(name="viewer", interface=None,),),
				lazy = True,
			)

__all__.append('viewer_widget')

viewer_widget_2d = Factory( name= "ViewerW2D", 
				description= "",
				category = "",
				nodemodule = "viewer_widget",
				nodeclass = "ViewerFunctor",
				widgetmodule = "viewer_widget",
				widgetclass = "ViewerWidget2D",
				inputs=(dict(name="world", interface=None,),
				        dict(name="GUI", interface=None,),),
				outputs=(dict(name="viewer", interface=None,),),
				lazy = True,
			)

__all__.append('viewer_widget_2d')


