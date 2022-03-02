# -*- python -*-
#
#       vplants.mars_alt.mars.analysis
#
#       Copyright 2006-2011 INRIA - CIRAD - INRA
#
#       File author(s): Eric Moscardi <eric.moscardi@sophia.inria.fr>
#                       Daniel BARBEAU <daniel.barbeau@inria.fr>
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.tTruet or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
#
#       OpenAlea WebSite : http://openalea.gforge.inria.fr
#
################################################################################

__license__= "Cecill-C"
__revision__ = " $Id: analysis.py 10947 2011-08-03 16:22:47Z dbarbeau $ "

from vplants.mars_alt.analysis.analysis import VTissueAnalysis, extract_L1
from vplants.mars_alt.analysis.structural_analysis import draw_walls, draw_L1

def nlabels(image):
    analysis = VTissueAnalysis(image)
    return analysis.nlabels(),

def center_of_mass(image,labels,real):
    analysis = VTissueAnalysis(image)
    return analysis.center_of_mass(labels,real),

def volume(image,labels,real):
    analysis = VTissueAnalysis(image)
    return analysis.volume(labels,real),

def neighbors(image,labels):
    analysis = VTissueAnalysis(image)
    return analysis.neighbors(labels),

def surface_area(image,label1, label2):
    analysis = VTissueAnalysis(image)
    return analysis.surface_area(label1, label2),
