from openalea.core import Factory
from openalea.core.interface import *

__name__ = "tissuedb.script"
__alias__ = []
__version__ = '0.0.2'
__license__ = "Cecill-C"
__authors__ = 'OpenAlea Consortium'
__institutes__ = 'INRIA/CIRAD'
__description__ = 'System Node library.'
__url__ = 'http://openalea.gforge.inria.fr'

__all__ = []

###############################################
#
#	admin
#
###############################################
dbwarning = Factory( name= "DBwarning", 
				description= "",
				category = "",
				nodemodule = "admin",
				nodeclass = "dbwarning",
				inputs=(),
				outputs=(),
			)

__all__.append('dbwarning')

debug = Factory( name= "debug", 
				description= "",
				category = "",
				nodemodule = "admin",
				nodeclass = "debug",
				inputs=(dict(name="i1", interface=None, value = None),),
				outputs=(),
			)

__all__.append('debug')

###############################################
#
#	tissue
#
###############################################
topen = Factory( name= "topen", 
				description= "",
				category = "",
				nodemodule = "tissue",
				nodeclass = "topen",
				inputs=(dict(name="filename", interface=IFileStr,),
						dict(name="mode", interface=IStr, value='r'),),
				outputs=(dict(name="filestream", interface=None,),),
			)

__all__.append('topen')


