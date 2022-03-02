# -*- python -*-
#
#       pglviewer.icons: icons examples
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
__revision__=" $Id: __wralea__.py 9869 2010-11-04 17:31:41Z dbarbeau $ "

from glob import glob
from os.path import dirname,join,basename
from openalea.core import DataFactory

__name__ = "tissue.pglviewer.icons"
__alias__ = ["pglviewer.icons"]
__version__ = '0.0.2'
__license__ = "Cecill-C"
__authors__ = 'Jerome Chopard'
__institutes__ = 'INRIA/CIRAD'
__description__ = 'data nodes for pglviewer icons.'
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
				description= "Credits: Jerome Chopard",
                editors=None,
                includes=None,
			)
""" % (i,icon_name)
	exec cmd
	
	__all__.append('i%d' % i)

