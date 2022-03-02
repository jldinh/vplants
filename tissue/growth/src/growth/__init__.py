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
"""
This module import the main growth algorithms
"""

__license__= "Cecill-C"
__revision__=" $Id: $ "

from geometry import *
from tensorial import apply_strain1D,apply_strain2D

try :
	from spring_growth import MecaGrowth
except ImportError :
	print "unable to import meca growth"

