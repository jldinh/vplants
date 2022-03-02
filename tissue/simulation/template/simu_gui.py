# -*- python -*-
#
#       simulation.template: example simulation package
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
This module defines the gui of a simulation
"""

__license__= "Cecill-C"
__revision__=" $Id: $ "

from openalea.pglviewer import ElmGUI

class SimuGUI (ElmGUI) :
	"""
	defines the user interactions during the simulation
	"""
	def __init__ (self, simu_view) :
		ElmGUI.__init__(self,simu_view)

