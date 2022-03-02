# -*- python -*-
#
#       spatialsbml: templating SBML
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
node definition for spatialsbml package
"""

__license__= "Cecill-C"
__revision__=" $Id: $ "

from openalea.core import Factory
from openalea.core.interface import *

__name__ = "spatialSBML"
__alias__ = []
__version__ = '0.0.2'
__license__ = "Cecill-C"
__authors__ = 'Jerome Chopard'
__institutes__ = 'INRIA/CIRAD'
__description__ = 'SpatialSBML Node library.'
__url__ = 'http://openalea.gforge.inria.fr'
__icon__ = "icon.png"

__all__ = []

#########################################
#
#	file
#
#########################################
read = Factory( name= "read", 
				description= "",
				category = "",
				nodemodule = "tissue",
				nodeclass = "read",
				inputs=(dict(name="filename", interface=IFileStr,),),
				outputs=(dict(name="tissuedb", interface=None,),),
				toscriptclass_name = "read_script",
			)

__all__.append('read')

write = Factory( name= "write", 
				description= "",
				category = "",
				nodemodule = "tissue",
				nodeclass = "write",
				inputs=(dict(name="tissuedb", interface=None,),
				        dict(name="filename", interface=IFileStr,),),
				outputs=(dict(name="tissuedb", interface=None,),),
				toscriptclass_name = "write_script",
			)

__all__.append('write')

info = Factory( name= "info", 
				description= "",
				category = "",
				nodemodule = "tissue",
				nodeclass = "info",
				inputs=(dict(name="tissuedb", interface=None,),
				        dict(name="widget", interface=IBool, value=True),),
				outputs=(),
				toscriptclass_name = "info_script",
			)

__all__.append('info')

project = Factory( name= "info", 
				description= "",
				category = "",
				nodemodule = "tissue",
				nodeclass = "info",
				inputs=(dict(name="tissuedb", interface=None,),
				        dict(name="widget", interface=IBool, value=True),),
				outputs=(),
				toscriptclass_name = "info_script",
			)

__all__.append('project')

