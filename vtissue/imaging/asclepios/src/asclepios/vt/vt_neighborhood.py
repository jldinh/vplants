# -*- python -*-
# -*- coding: latin-1 -*-
#
#       mars : reconstruction
#
#       Copyright 2006 - 2010 INRIA - CIRAD - INRA
#
#       File author(s): Eric MOSCARDI <eric.moscardi@gmail.com>
#                       Daniel BARBEAU <daniel.barbeau@inria.fr>
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#       http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
#
#       OpenAlea WebSite : http://openalea.gforge.inria.fr
################################################################################

__license__= "Cecill-C"
__revision__ = " $Id$ "

from ctypes import *

#################################################################################
#                               Enumerations
#################################################################################

class Neighborhood :
    """
    Definition of Neighborhood enumeration

    Voisinages usuels.
    * - N04 = 4,  4-voisinage, voisins qui partagent une arete en 2D
    * - N06 = 6,  6-voisinage, voisins qui partagent une face en 3D
    * - N08 = 8,  8-voisinage, voisins qui partagent une arete ou un sommet en 2D
    * - N10 = 10,  10-voisinage = union du 6-voisinage et ou 8-voisinage
    * - N18 = 18,  18-voisinage, voisins qui partagent une face ou une arete en 3D
    * - N26 = 26  26-voisinage, voisins qui partagent une face, une arete ou un sommet en 3D
    """
    C_04 = 4
    C_08 = 8
    C_06 = 6
    C_10 = 10
    C_18 = 18
    C_26 = 26
    N04 = 4    # 4-voisinage, voisins qui partagent une arete en 2D
    N06 = 6    # 6-voisinage, voisins qui partagent une face en 3D
    N08 = 8    # 8-voisinage, voisins qui partagent une arete ou un sommet en 2D
    N10 = 10   # 10-voisinage = union du 6-voisinage et ou 8-voisinage
    N18 = 18   # 18-voisinage, voisins qui partagent une face ou une arete en 3D
    N26 = 26    # 26-voisinage, voisins qui partagent une face, une arete ou un sommet en 3D

