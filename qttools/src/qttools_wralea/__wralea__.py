# -*- python -*-
#
#       qttools: GUI
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
node definition for Qt
"""

__license__= "Cecill-C"
__revision__=" $Id: __wralea__.py 7883 2010-02-09 07:35:10Z cokelaer $ "

from openalea.core import Factory
from openalea.core.interface import *

__name__ = "openalea.qttools"
__alias__ = []
__version__ = '0.0.2'
__license__ = "Cecill-C"
__authors__ = 'Jerome Chopard'
__institutes__ = 'INRIA/CIRAD'
__description__ = 'Qt Node library.'
__url__ = 'http://openalea.gforge.inria.fr'

__all__ = []

#########################################
#
#	display
#
#########################################
viewer = Factory( name= "txt viewer", 
				description= "",
				category = "",
				nodemodule = "qt_func",
				nodeclass = "text_edit",
				inputs=(),
				outputs=(dict(name="viewer", interface=None,),),
			)

__all__.append('viewer')

append = Factory( name= "append", 
				description= "",
				category = "",
				nodemodule = "qt_func",
				nodeclass = "append_txt",
				inputs=(dict(name="viewer", interface=None,),
				        dict(name="txt", interface=IStr, value=""),),
				outputs=(dict(name="viewer", interface=None,),),
			)

__all__.append('append')


