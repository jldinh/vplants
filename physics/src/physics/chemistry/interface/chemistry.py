# -*- python -*-
# -*- coding: latin-1 -*-
#
#       IChemistry,ISubstance : physics package
#
#       Copyright or © or Copr. 2006 INRIA - CIRAD - INRA  
#
#       File author(s): Jerome Chopard <jerome.chopard@sophia.inria.fr>
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
# 
#       VPlants WebSite : https://gforge.inria.fr/projects/vplants/
#

__doc__="""
This module provide an interface for chemistry reactions
"""

__license__= "Cecill-C"
__revision__=" $Id: chemistry.py 7882 2010-02-08 18:36:38Z cokelaer $ "

class IChemistry (object) :
	"""
	interface for all algorithms that modify
	a substance (chemical)
	"""
	def react (self, substance, dt) :
		"""
		modify in place substance
		"""
		raise NotImplementedError

