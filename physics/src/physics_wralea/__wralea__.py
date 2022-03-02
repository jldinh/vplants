# -*- python -*-
#
#       physics: physics algorithms
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
node definition for physics package
"""

__license__= "Cecill-C"
__revision__=" $Id: __wralea__.py 7882 2010-02-08 18:36:38Z cokelaer $ "

from openalea.core import Factory
from openalea.core.interface import *

__name__ = "tissue.physics"
__alias__ = ["physics"]
__version__ = '0.0.2'
__license__ = "Cecill-C"
__authors__ = 'Jerome Chopard'
__institutes__ = 'INRIA/CIRAD'
__description__ = 'Physics Node library.'
__url__ = 'http://openalea.gforge.inria.fr'

__all__ = []

#########################################
#
#	chemistry
#
#########################################
diffusion = Factory( name= "diffusion", 
				description= "",
				category = "",
				nodemodule = "chemistry",
				nodeclass = "diffusion",
				inputs=(dict(name="graph", interface=None,),
				        dict(name="D", interface=None,),
				        dict(name="V", interface=None,),
				        dict(name="subst", interface=None,),
				        dict(name="dt", interface=IFloat,),),
				outputs=(dict(name="func", interface=IFunction,),),
				toscriptclass_name = "diffusion_script",
			)

__all__.append('diffusion')

reaction = Factory( name= "reaction", 
				description= "",
				category = "",
				nodemodule = "chemistry",
				nodeclass = "reaction",
				inputs=(dict(name="alpha", interface=None,),
				        dict(name="beta", interface=None,),
				        dict(name="subst", interface=None,),
				        dict(name="dt", interface=IFloat,),),
				outputs=(dict(name="func", interface=IFunction,),),
				toscriptclass_name = "reaction_script",
			)

__all__.append('reaction')


