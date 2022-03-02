# -*- python -*-
#
#       celltissue.data: tissue examples
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
node definition for celltissue examples
"""

__license__= "Cecill-C"
__revision__=" $Id: $ "

from openalea.core import DataFactory

__name__ = "tissue.data"
__alias__ = []
__version__ = '0.0.2'
__license__ = "Cecill-C"
__authors__ = 'Jerome Chopard'
__institutes__ = 'INRIA/CIRAD'
__description__ = 'Celltissue Data library.'
__url__ = 'http://openalea.gforge.inria.fr'
__icon__ = "icon.png"

__all__ = []

#########################################
#
#	file
#
#########################################
t1 = DataFactory( name= "linear1D.zip", 
				description= "Credits: Jerome Chopard",
                editors=None,
                includes=None,
			)

__all__.append('t1')

t2 = DataFactory( name= "surface3D.zip", 
				description= "Credits: Jerome Chopard",
                editors=None,
                includes=None,
			)

__all__.append('t2')

