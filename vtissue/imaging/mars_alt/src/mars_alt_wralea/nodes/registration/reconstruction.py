# -*- python -*-
# -*- coding: latin-1 -*-
#
#       mars_alt wralea
#
#       Copyright 2006 - 2011 INRIA - CIRAD - INRA
#
#       File author(s): Daniel BARBEAU <daniel.barbeau@inria.fr>
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#        http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
#
#       OpenAlea WebSite : http://openalea.gforge.inria.fr
################################################################################


__license__ = "Cecill-C"
__revision__ = " $Id: reconstruction.py 11022 2011-08-26 16:08:21Z dbarbeau $ "

from vplants.mars_alt.mars.reconstruction import reconstruction_task, reconstruct, fuse_reconstruction, \
     surface_landmark_matching_parameters, automatic_linear_parameters, automatic_non_linear_parameters
from vplants.mars_alt.mars.fusion import original_fusion, fusion, fusion_task


