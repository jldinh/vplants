#!/usr/bin/python
# -*- python -*-
#
#       VPlants.MarsAlt
#
#       Copyright 2006-2011 INRIA - CIRAD - INRA
#
#       File author(s): Daniel Barbeau <daniel.barbeau@sophia.inria.fr>
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
#
#       OpenAlea WebSite : http://openalea.gforge.inria.fr
#
###############################################################################

from vplants.mars_alt.alt.mapping import LineageTracking
from vplants.mars_alt.alt.mapping import RomainLineageTrackingDummyWrapper
from vplants.mars_alt.alt.mapping import PyLineageTracking
from vplants.mars_alt.alt.mapping import lineage_from_file

from vplants.mars_alt.alt.candidate_lineaging import candidate_lineaging
from vplants.mars_alt.alt.candidate_lineaging import py_get_candidate_successors
from vplants.mars_alt.alt.candidate_lineaging import rfernandez_get_candidate_successors
from vplants.mars_alt.alt.flow_graph import flow_graph
from vplants.mars_alt.alt.flow_graph import rfernandez_flow_solving
from vplants.mars_alt.alt.flow_graph import nx_flow_solving
from vplants.mars_alt.alt.flow_graph import merge_expert_and_candidates

from openalea.core.logger import get_logger

myLogger = get_logger(__name__)

def mapping(im_0,
            im_1,
            dist=3,
            expert_lineage=None,
            ndiv=8,
            use_binary=False,
            candidate_method="cell_shape",
            flow_method="rf_flow"):
    """ Given two images of an organ at t0 and t1, tries to find cell lineages.

    Careful: Image labels are expected to start from 2 (1 being the background)

    :Parameters:
      - `im_0` (openalea.image.SpatialImage) -  segmented image of meristem a t0
      - `im_1` (openalea.image.SpatialImage) -  segmented image of meristem a t1
      - `expert_lineage` (dict) - a dictionnary mapping mother labels to a list of child labels.
      - `ndiv` (int) -  an limit to the number of children a mother can have.  (used by graph flow)
      - `use_binary` (bool) - if True, will attempt to call directly the MAPPING binary if available instead of
         using the CTypes wrapping. This is the ground truth to assert that other implmentations
         yield similar results. If this is used, "candidate_method" and "flow_method" are not used.
      - `candidate_method` (str) - name of the method to use. "cell_shape" means that the distance `dist` is computed
         starting from the mother cell's boundary. "cell_as_sphere" considers cells as spheres and the distance
         is computed from the mother cell's barycenter corrected by the mean radius of cells. The mean radius of cell
         is the mean diagonal of all cells' bouding boxes.
      - `flow_method` (str) - name of the flow graph solving. "rf_flow" is the original published implementation by Romain Fernandez.

    """


    # don't put default container arguments as they are shared between instances
    # and bring in MANY side effects:
    if expert_lineage is None:
        expert_lineage = {}

    if None in [im_0, im_1]:
        myLogger.error("Lineaging got null input image")
        return (None,)

    # If use_binary is True, candidate_method and flow_method are discarded and we attempt
    # to use Romain Fernandez' MAPPING binary.
    if use_binary:
        solver = RomainLineageTrackingDummyWrapper(im_0, im_1, dist, expert_lineage, ndiv)
    else:
        cfunc = rfernandez_get_candidate_successors if candidate_method=="cell_shape" else py_get_candidate_successors
        ffunc = rfernandez_flow_solving if flow_method=="rf_flow" else nx_flow_solving

        solver = PyLineageTracking( cfunc, ffunc,
                                    im_0, im_1, dist, expert_lineage, ndiv)

    solver.run()

    # return outputs
    return solver.get_lineages(), solver.get_candidates()


