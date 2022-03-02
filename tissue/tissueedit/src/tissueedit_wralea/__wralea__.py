# -*- python -*-
#
#       tissueedit: set of GUI to edit a tissue
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
node definition for tissueedit package
"""

__license__= "Cecill-C"
__revision__=" $Id: $ "

from openalea.core import Factory
from openalea.core.interface import *

__name__ = "tissue.edit"
__alias__ = []
__version__ = '0.0.2'
__license__ = "Cecill-C"
__authors__ = 'Jerome Chopard'
__institutes__ = 'INRIA/CIRAD'
__description__ = 'tissueedit Node library.'
__url__ = 'http://openalea.gforge.inria.fr'
__icon__ = "icon.png"

__all__ = []

#########################################
#
#	PGL ext
#
#########################################
scalar_prop_edit = Factory( name= "scalar_prop_edit", 
				description= "",
				category = "",
				nodemodule = "prop_edit",
				nodeclass = "scalar_prop_edit",
				inputs=(dict(name="scalar_prop_view", interface=None,),
				        dict(name="prop_type", interface=IStr,),
				        dict(name="select_func", interface=IFunction, value=None),),
				outputs=(dict(name="gui", interface=None,),),
				toscriptclass_name = "scalar_prop_edit_script",
			)

__all__.append('scalar_prop_edit')

