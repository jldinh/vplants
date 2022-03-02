# -*- python -*-
#
#       tissueshape: associate geometry to a tissue
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
node definition for tissueshape package
"""

__license__= "Cecill-C"
__revision__=" $Id: $ "

from openalea.core import Factory
from openalea.core.interface import *

__name__ = "tissue.shape"
__alias__ = []
__version__ = '0.0.2'
__license__ = "Cecill-C"
__authors__ = 'Jerome Chopard'
__institutes__ = 'INRIA/CIRAD'
__description__ = 'tissueshape Node library.'
__url__ = 'http://openalea.gforge.inria.fr'
__icon__ = "icon.png"

__all__ = []

#########################################
#
#	grid
#
#########################################
regular_grid = Factory( name= "regular grid", 
				description= "",
				category = "",
				nodemodule = "grid",
				nodeclass = "create_regular_grid",
				inputs=(dict(name="shape", interface=ISequence,),),
				outputs=(dict(name="tissuedb", interface=None,),),
				toscriptclass_name = "create_regular_grid_script",
			)

__all__.append('regular_grid')

hexagonal_grid = Factory( name= "hexagonal grid", 
				description= "",
				category = "",
				nodemodule = "grid",
				nodeclass = "create_hexagonal_grid",
				inputs=(dict(name="shape", interface=ISequence,),
				        dict(name="shape_geom", interface=IStr, value='hexa'),),
				outputs=(dict(name="tissuedb", interface=None,),),
				toscriptclass_name = "create_hexagonal_grid_script",
			)

__all__.append('hexagonal_grid')

#########################################
#
#	translate pgl
#
#########################################
tovec = Factory( name= "tovec", 
				description= "",
				category = "",
				nodemodule = "shape",
				nodeclass = "tovec",
				inputs=(dict(name="prop", interface=IDict,),
				        dict(name="force 3D", interface=IBool, value=False),),
				outputs=(dict(name="prop", interface=IDict,),),
				toscriptclass_name = "tovec_script",
			)

__all__.append('tovec')

