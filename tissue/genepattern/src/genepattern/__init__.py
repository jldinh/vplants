# -*- python -*-
#
#       genepattern: abstract geometry and functions to use them
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
This module import the main geometrical objects and function to use them
"""

__license__= "Cecill-C"
__revision__=" $Id: $ "

from abstract_geometry import *
from projection import MeshProjector
from zone_morph import read_envelop,write_envelop,compute_envelop,find_zone

class Zone (object) :
	pass

