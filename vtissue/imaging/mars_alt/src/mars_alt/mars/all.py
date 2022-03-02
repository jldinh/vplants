# -*- python -*-
# -*- coding: latin-1 -*-
#
#       vplants.mars_alt.mars.all
#
#       Copyright 2006 - 2011 INRIA - CIRAD - INRA
#
#       File author(s): Daniel BARBEAU <daniel.barbeau@inria.fr>
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#       http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
#
#       OpenAlea WebSite : http://openalea.gforge.inria.fr
################################################################################

__license__= "Cecill-C"
__revision__ = " $Id: all.py 11302 2011-10-22 22:30:55Z dbarbeau $ "

# -- to work with landmarks --
from reconstruction import im2surface, surface2im, spatialise_matrix_points, surface_landmark_matching
# -- automatic registrations --
from reconstruction import automatic_linear_registration, automatic_non_linear_registration
# -- task based API --
from reconstruction import reconstruction_task, surface_landmark_matching_parameters, automatic_linear_parameters, \
     automatic_non_linear_parameters, reconstruct, fuse_reconstruction

# -- to fuse images together: task based API --
from fusion import fusion, fusion_task, attenuation
from fusion import original_fusion

# -- segmentation tools --
from segmentation import filtering, seed_extraction, watershed, remove_small_cells, \
     euclidean_sphere, mostRepresentative_filter, cell_segmentation
