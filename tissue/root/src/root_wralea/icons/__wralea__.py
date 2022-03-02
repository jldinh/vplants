# -*- python -*-
#
#       root.icons: icons examples
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
data nodes to store some icons
"""

__license__= "Cecill-C"
__revision__=" $Id: $ "

from glob import glob
from os.path import dirname,join,basename
from openalea.core import DataFactory

__name__ = "root.data.icons"
__alias__ = []
__version__ = '0.0.2'
__license__ = "Cecill-C"
__authors__ = 'Jerome Chopard'
__institutes__ = 'INRIA/CIRAD'
__description__ = 'data nodes for root icons.'
__url__ = 'http://openalea.gforge.inria.fr'
__icon__ = "icon.png"

__all__ = []

#########################################
#
#	file
#
#########################################
local_dir = dirname(__file__)
for i,name in enumerate(glob(join(local_dir,"*.png") ) ) :
	icon_name = basename(name)
	cmd = """
i%d = DataFactory( name= "%s", 
				description= "Credits: Mikael Lucas",
                editors=None,
                includes=None,
			)
""" % (i,icon_name)
	exec cmd
	
	__all__.append('i%d' % i)

