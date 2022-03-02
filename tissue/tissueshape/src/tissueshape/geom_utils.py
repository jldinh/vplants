# -*- python -*-
#
#       tissueshape: function used to deal with tissue geometry
#
#       Copyright 2006 INRIA - CIRAD - INRA  
#
#       File author(s): Jerome Chopard <revesansparole@gmail.com>
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
# 
#       OpenAlea WebSite : http://openalea.gforge.inria.fr
#

__doc__ = """
This module defines functions to convert between basic python objects
and numpy vectors
"""

__license__ = "Cecill-C"
__revision__ = " $Id: $ "

__all__ = ["tovec"
         , "totup"]

from numpy import array


def tovec (tup) :
	return array(tup, 'f')#force float type

def totup (vec) :
	return tuple(vec)#TODO int vs float?





















