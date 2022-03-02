# -*- coding: latin-1 -*-
#
#       analysis : mars_alt package
#
#       Copyright 2006 - 2010 INRIA - CIRAD - INRA
#
#       File author(s): Eric MOSCARDI <eric.moscardi@gmail.com>
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#       http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
#
#       OpenAlea WebSite : http://openalea.gforge.inria.fr
################################################################################

__license__ = "Cecill-C"
__revision__ = " $Id: $ "

from vplants.mars_alt.analysis.structural_analysis import draw_walls, draw_L1

def wra_draw_walls(image, dilation):
    return draw_walls(image, dilation)

def wra_draw_L1(image):
    return draw_L1(image)
