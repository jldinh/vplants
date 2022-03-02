#-*- python -*-
#
#       vplants.mars_alt.alt.mapping
#
#       Copyright 2006-2011 INRIA - CIRAD - INRA
#
#       File author(s): Daniel BARBEAU <daniel.barbeau@inria.fr>
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#       http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
#
#       OpenAlea WebSite : http://openalea.gforge.inria.fr
#
################################################################################


__license__ = "CeCILL v2"
__revision__ = " $Id: alt.py 12060 2012-05-15 13:33:09Z chakkrit $ "

from vplants.mars_alt.alt.alt_preparation import alt_preparation
from vplants.mars_alt.alt.alt_disk_memoize import alt_intermediate
from vplants.mars_alt.alt.alt_loop import alt_loop


def alt( imgSeg0, imgSeg1, expert_map,
         imgFus0=None, imgFus1=None, max_iter = 20,
         field_sigma = 5.0, non_linear_registration_params = None,
         mapping_dist=8.0, mapping_ndiv=8,
         mapping_candidate_method="cell_shape", mapping_flow_method="rf_flow",
         filter_params=[],
         strict_candidate_test = False,
         intermediate_data = None,
         ):

    mat_init = __alt_preparation(expert_map=expert_map, imgSeg0=imgSeg0, imgSeg1=imgSeg1, intermediate_data=intermediate_data)
    return alt_loop( imgSeg0 = imgSeg0,
                     imgSeg1 = imgSeg1,
                     expert_map = expert_map,
                     tissue0 = None,
                     tissue1 = None,
                     imgFus0 = imgFus0,
                     imgFus1 = imgFus1,
                     mat_init = mat_init,
                     max_iter = max_iter,
                     field_sigma = field_sigma,
                     non_linear_registration_params = non_linear_registration_params,
                     mapping_dist=mapping_dist,
                     mapping_ndiv=mapping_ndiv,
                     mapping_candidate_method=mapping_candidate_method,
                     mapping_flow_method=mapping_flow_method,
                     filter_params=filter_params,
                     intermediate_data = None
                     )



@alt_intermediate("alt_preparation", ("tissue_0", "picklable"), ("tissue_1", "picklable"), ("mat_init","small_matrix") )
def __alt_preparation(**kw):
    mat_init = alt_preparation(kw["expert_map"], kw["imgSeg0"], kw["imgSeg1"])
    return mat_init
