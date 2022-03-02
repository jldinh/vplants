# -*- python -*-
#
#       growth: geometrical transformations to grow tissues
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
node definition for growth package
"""

__license__= "Cecill-C"
__revision__=" $Id: $ "

from openalea.core import Factory
from openalea.core.interface import *

__name__ = "tissue.growth"
__alias__ = []
__version__ = '0.0.2'
__license__ = "Cecill-C"
__authors__ = 'Jerome Chopard'
__institutes__ = 'INRIA/CIRAD'
__description__ = 'Growth Node library.'
__url__ = 'http://openalea.gforge.inria.fr'
__icon__ = "icon.png"

__all__ = []

#########################################
#
#	geometry
#
#########################################
uniform = Factory( name= "uniform", 
				description= "",
				category = "",
				nodemodule = "geometry",
				nodeclass = "uniform",
				inputs=(dict(name="pos", interface=None,),
				        dict(name="scaling", interface=ISequence,),
				        dict(name="dt", interface=IFloat,),),
				outputs=(dict(name="func", interface=IFunction,),),
				toscriptclass_name = "uniform_script",
			)

__all__.append('uniform')

radial = Factory( name= "radial", 
				description= "",
				category = "",
				nodemodule = "geometry",
				nodeclass = "radial",
				inputs=(dict(name="pos", interface=None,),
				        dict(name="center", interface=ISequence,),
				        dict(name="speed_rate", interface=IFloat,),
				        dict(name="dt", interface=IFloat,),),
				outputs=(dict(name="func", interface=IFunction,),),
				toscriptclass_name = "radial_script",
			)

__all__.append('radial')

linear = Factory( name= "linear", 
				description= "",
				category = "",
				nodemodule = "geometry",
				nodeclass = "linear",
				inputs=(dict(name="pos", interface=None,),
				        dict(name="displacement_func", interface=None,),
				        dict(name="axis", interface=ISequence,),
				        dict(name="center", interface=ISequence,),
				        dict(name="dt", interface=IFloat,),),
				outputs=(dict(name="func", interface=IFunction,),),
				toscriptclass_name = "linear_script",
			)

__all__.append('linear')

unconstrained1D = Factory( name= "unconstrained", 
				description= "",
				category = "",
				nodemodule = "geometry",
				nodeclass = "unconstrained",
				inputs=(dict(name="pos", interface=None,),
				        dict(name="mesh", interface=None,),
				        dict(name="root", interface=IInt,),
				        dict(name="growth_speed", interface=IDict,),
				        dict(name="dt", interface=IFloat,),),
				outputs=(dict(name="func", interface=IFunction,),),
				toscriptclass_name = "unconstrained_script",
			)

__all__.append('unconstrained')

#########################################
#
#	pgl
#
#########################################
vector = Factory( name= "vec", 
				description= "",
				category = "",
				nodemodule = "geometry",
				nodeclass = "vectorize",
				inputs=(dict(name="x", interface=IFloat, value=0.),
				        dict(name="y", interface=IFloat, value=0.),
				        dict(name="z", interface=IFloat, value=None),),
				outputs=(dict(name="vec", interface=ISequence,),),
				toscriptclass_name = "vectorize_script",
			)

__all__.append('vector')


