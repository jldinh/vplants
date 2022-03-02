# -*- python -*-
#
#       vmanalysis: algorithms to analyse images
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
node definition for vmanalysis package
"""

__license__= "Cecill-C"
__revision__=" $Id: $ "

from openalea.core import Factory
from openalea.core.interface import *

__name__ = "tissue.vmanalysis"
__alias__ = []
__version__ = '0.0.1'
__license__ = "Cecill-C"
__authors__ = 'Jerome Chopard'
__institutes__ = 'INRIA/CIRAD'
__description__ = 'vmanalysis Node library.'
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
				nodemodule = "inrimage",
				nodeclass = "read",
				inputs=(dict(name="filename", interface=IFileStr,),),
				outputs=(dict(name="inrimage", interface=None,),),
				toscriptclass_name = "read_script",
			)

__all__.append('read')

write = Factory( name= "write", 
				description= "",
				category = "",
				nodemodule = "inrimage",
				nodeclass = "write",
				inputs=(dict(name="inrimage", interface=None,),
				        dict(name="filename", interface=IFileStr,),),
				outputs=(dict(name="inrimage", interface=None,),),
				toscriptclass_name = "write_script",
			)

__all__.append('write')

#########################################
#
#	access
#
#########################################
split = Factory( name= "split", 
				description= "",
				category = "",
				nodemodule = "inrimage",
				nodeclass = "split",
				inputs=(dict(name="inrimage", interface=None,),),
				outputs=(dict(name="header", interface=IDict,),
				         dict(name="data", interface=None,),),
				toscriptclass_name = "split_script",
			)

__all__.append('split')

merge = Factory( name= "merge", 
				description= "",
				category = "",
				nodemodule = "inrimage",
				nodeclass = "merge",
				inputs=(dict(name="header", interface=IDict,),
				        dict(name="data", interface=None,),),
				outputs=(dict(name="inrimage", interface=None,),),
				toscriptclass_name = "merge_script",
			)

__all__.append('merge')

#########################################
#
#	display
#
#########################################
display = Factory( name= "display", 
				description= "",
				category = "",
				nodemodule = "inrimage",
				nodeclass = "display",
				inputs=(dict(name="inrimages", interface=None),
				        dict(name="palette", interface=IStr, value="grayscale"),
				        dict(name="color_index_max", interface=IInt, value=None),),
				outputs=(dict(name="views", interface=None),),
				toscriptclass_name = "display_script",
			)

__all__.append('display')


