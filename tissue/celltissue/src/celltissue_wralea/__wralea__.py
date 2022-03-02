# -*- python -*-
#
#       celltissue: main tissue object and functions to use it
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
node definition for celltissue package
"""

__license__= "Cecill-C"
__revision__=" $Id: $ "

from openalea.core import Factory
from openalea.core.interface import *

__name__ = "tissue.core"
__alias__ = []
__version__ = '0.0.2'
__license__ = "Cecill-C"
__authors__ = 'Jerome Chopard'
__institutes__ = 'INRIA/CIRAD'
__description__ = 'Celltissue Node library.'
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

#########################################
#
#	access
#
#########################################
tissue = Factory( name= "tissue", 
				description= "",
				category = "",
				nodemodule = "tissue",
				nodeclass = "tissue",
				inputs=(dict(name="tissuedb", interface=None,),),
				outputs=(dict(name="tissuedb", interface=None,),
				         dict(name="tissue", interface=None,),),
				toscriptclass_name = "tissue_script",
			)

__all__.append('tissue')

prop = Factory( name= "prop", 
				description= "",
				category = "",
				nodemodule = "tissue",
				nodeclass = "get_property",
				inputs=(dict(name="tissuedb", interface=None,),
				        dict(name="name", interface=IStr,),),
				outputs=(dict(name="tissuedb", interface=None,),
				         dict(name="prop", interface=IDict,),),
				toscriptclass_name = "get_property_script",
			)

__all__.append('prop')

cfg = Factory( name= "cfg", 
				description= "",
				category = "",
				nodemodule = "tissue",
				nodeclass = "get_config",
				inputs=(dict(name="tissuedb", interface=None,),
				        dict(name="name", interface=IStr,),),
				outputs=(dict(name="tissuedb", interface=None,),
				         dict(name="cfg", interface=None,),),
				toscriptclass_name = "cfg_script",
			)

__all__.append('cfg')

topo = Factory( name= "topo", 
				description= "",
				category = "",
				nodemodule = "tissue",
				nodeclass = "get_topology",
				inputs=(dict(name="tissuedb", interface=None,),
				        dict(name="name", interface=IStr,),
				        dict(name="cfg", interface=IStr, value="config"),),
				outputs=(dict(name="tissuedb", interface=None,),
				         dict(name="topo", interface=None,),),
				toscriptclass_name = "get_topology_script",
			)

__all__.append('topo')

#########################################
#
#	edition
#
#########################################
def_property = Factory( name= "def_prop", 
				description= "",
				category = "",
				nodemodule = "tissue",
				nodeclass = "def_property",
				inputs=(dict(name="tissuedb", interface=None,),
				        dict(name="name", interface=IStr,),
				        dict(name="val", interface=IFloat,),
				        dict(name="elm_type", interface=IStr,),
				        dict(name="cfg", interface=IStr, value="config"),
				        dict(name="descr", interface=IStr, value=""),),
				outputs=(dict(name="tissuedb", interface=None,),
				         dict(name="prop", interface=IDict,),),
				toscriptclass_name = "def_property_script",
			)

__all__.append('def_property')

empty_property = Factory( name= "empty_prop", 
				description= "",
				category = "",
				nodemodule = "tissue",
				nodeclass = "empty_property",
				inputs=(dict(name="tissuedb", interface=None,),
				        dict(name="name", interface=IStr,),
				        dict(name="descr", interface=IStr, value=""),),
				outputs=(dict(name="tissuedb", interface=None,),
				         dict(name="prop", interface=IDict,),),
				toscriptclass_name = "empty_property_script",
			)

__all__.append('empty_property')

scaled_property = Factory( name= "scaled_prop", 
				description= "",
				category = "",
				nodemodule = "tissue",
				nodeclass = "scaled_property",
				inputs=(dict(name="tissuedb", interface=None,),
				        dict(name="name", interface=IStr,),
				        dict(name="ref_prop", interface=IDict,),
				        dict(name="scale", interface=IFloat,),),
				outputs=(dict(name="tissuedb", interface=None,),
				         dict(name="prop", interface=IDict,),),
				toscriptclass_name = "scaled_property_script",
			)

__all__.append('scaled_property')

merge_property = Factory( name= "merge_prop", 
				description= "",
				category = "",
				nodemodule = "tissue",
				nodeclass = "merge_property",
				inputs=(dict(name="prop", interface=IDict,),
				        dict(name="ref_prop", interface=IDict,),),
				outputs=(dict(name="prop", interface=IDict,),),
				toscriptclass_name = "merge_property_script",
			)

__all__.append('merge_property')

#########################################
#
#	math
#
#########################################
random_uniform_func = Factory( name= "random_uniform_func", 
				description= "",
				category = "",
				nodemodule = "mathfunc",
				nodeclass = "random_uniform_func",
				inputs=(dict(name="min", interface=IFloat, value=0.),
				        dict(name="max", interface=IFloat, value=1.),),
				outputs=(dict(name="val", interface=IFloat,),),
				toscriptclass_name = "random_uniform_func_script",
			)

__all__.append('random_uniform_func')

#########################################
#
#	file
#
#########################################
create_name_iterator = Factory( name= "name iterator", 
				description= "",
				category = "",
				nodemodule = "filefunc",
				nodeclass = "create_name_iterator",
				inputs=(dict(name="name template", interface=IStr, value="tissue%.4d.zip"),
				        dict(name="ini_ind", interface=IInt, value=0),),
				outputs=(dict(name="func", interface=None,),),
				toscriptclass_name = "create_name_iterator_script",
			)

__all__.append('create_name_iterator')

write_table = Factory( name= "write_table", 
				description= "",
				category = "",
				nodemodule = "filefunc",
				nodeclass = "write_table",
				inputs=(dict(name="filename", interface=IFileStr,),
				        dict(name="dformat", interface=IStr, value="%d"),
				        dict(name="sep", interface=IStr, value="\t"),
				        dict(name="step", interface=IInt, value=0),
				        dict(name="prop", interface=None,),),
				outputs=(dict(name="prop", interface=None,),),
			)

__all__.append('write_table')

