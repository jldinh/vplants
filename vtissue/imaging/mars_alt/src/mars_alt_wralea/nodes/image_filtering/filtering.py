# -*- python -*-
#
#       vplants.mars_alt.mars.image_filtering
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
__revision__ = " $Id: filtering.py 10947 2011-08-03 16:22:47Z dbarbeau $ "


from vplants.mars_alt.mars.segmentation import filtering

def wra_filtering(im,filter_type,filter_value):
    if filter_type == "alternate sequential" :
        filter_type = "asf"
    elif filter_type == "most representative":
        filter_type = "mr"
    else :
        filter_type = "gaussian"
    return filtering (im,filter_type,filter_value)
wra_filtering.__doc__ = filtering.__doc__
