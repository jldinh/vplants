# -*- python -*-
#
#       CandidateLineaging test module
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


__license__ = "CeCILL v2"
__revision__ = " $Id: test_candidate_lineaging.py 11152 2011-09-15 17:43:43Z dbarbeau $ "

import numpy as np
import scipy as sci
from openalea.image.spatial_image import SpatialImage

from vplants.mars_alt.alt import candidate_lineaging
from vplants.mars_alt.alt.candidate_lineaging import equal_lineages, compare_lineages


def test_compare_lineages():
    ref = {2:[4,5],3:[8,6,7]}
    lin = {5:[4]}
    assert compare_lineages(ref, lin) == (0, set(), set([5]), set([2, 3]), {})

    ref = {2:[4,5],3:[8,6,7]}
    lin = {5:[4], 3:[8,6]}
    assert compare_lineages(ref, lin) == (2/6., set([3]), set([5]), set([2]),
                                         {3: (2/3., set([6, 8]), set(), set([7]))})

    

def test_lineage_equality_test():
    # test equality of mapping from mother to children
    d1 = {1:[1], 2:[2,3], 3:[4,5]}
    d2 = d1.copy()
    assert equal_lineages(d1, d2)

    d1 = {1:[1], 2:[2], 3:[4,5]}
    d2 = {1:[1], 2:[2,3], 3:[4,5]}
    assert not equal_lineages(d1, d2)

    d1 = {1:[1], 2:[2], 3:[4,5]}
    d2 = {1:[1], 3:[4,5]}
    assert not equal_lineages(d1, d2)

    # test equality of mapping from mother to **candidate** children
    d1 = {1:[(1,1.0)], 2:[(2,1.1),(3,1.0)], 3:[(4,0.1),(5,0.79)]}
    d2 = d1.copy()
    assert equal_lineages(d1, d2)

    d1 = {1:[(1,1.0)], 2:[(2,1.1),(3,1.0)], 3:[(4,0.1),(5,0.79)]}
    d2 = {1:[(1,1.0)], 2:[(2,1.1)], 3:[(4,0.1),(5,0.79)]}
    assert not equal_lineages(d1, d2)

    d1 = {1:[(1,1.0)], 2:[(2,1.1),(3,1.0)], 3:[(4,0.1),(5,0.79)]}
    d2 = {1:[(1,1.0)], 3:[(4,0.1),(5,0.79)]}
    assert not equal_lineages(d1, d2)

    d1 = {1:[(1,1.0)], 2:[(2,1.1),(3,1.0)], 3:[(4,0.1),(5,0.79)]}
    d2 = {1:[(1,1.0)], 2:[(2,1.2),(3,1.0)], 3:[(4,0.1),(5,0.79)]}
    assert equal_lineages(d1, d2, epsilon=1e-1)

    d1 = {1:[(1,1.0)], 2:[(2,1.1),(3,1.0)], 3:[(4,0.1),(5,0.79)]}
    d2 = {1:[(1,1.0)], 2:[(2,1.2),(3,1.0)], 3:[(4,0.1),(5,0.79)]}
    assert not equal_lineages(d1, d2)

    d1 = {1:[(1,1.0)], 2:[(2,1.1),(3,1.0)], 3:[(4,0.1),(5,0.79)]}
    d2 = {1:[(1,1.0)], 2:[(2,1.1)], 3:[(4,0.1),(5,0.79)]}
    assert not equal_lineages(d1, d2)


def test_identity():
    im0 = SpatialImage(np.ones((11,7,1), dtype=np.ushort))
    im1 = SpatialImage(np.ones((11,7,1), dtype=np.ushort))

    im0[1:-1,1:-1,:] = 2
    im1[1:-1,1:-1,:] = 2

    d1 = candidate_lineaging.rfernandez_get_candidate_successors (im0, im1, 3, 8, 1)
    d2 = candidate_lineaging.py_get_candidate_successors         (im0, im1, 3, 8, 1)
    print d1
    print d2
    assert equal_lineages(d1,d2)

    d1 = candidate_lineaging.rfernandez_get_candidate_successors (im0, im1, 0, 8, 1)
    d2 = candidate_lineaging.py_get_candidate_successors         (im0, im1, 0, 8, 1)
    print d1
    print d2
    assert equal_lineages(d1,d2)


def test_one_div():
    im0 = SpatialImage(np.ones((11,7,1), dtype=np.ushort))
    im1 = SpatialImage(np.ones((11,7,1), dtype=np.ushort))

    im0[1:-1,1:-1,:] = 2
    im1[1:4,1:-1,:] = 2
    im1[6:-1,1:-1,:] = 3

    d1 = candidate_lineaging.rfernandez_get_candidate_successors (im0, im1, 3, 8, 1)
    d2 = candidate_lineaging.py_get_candidate_successors (im0, im1, 3, 8, 1)
    print d1
    print d2
    assert equal_lineages(d1, d2)

    d1 = candidate_lineaging.rfernandez_get_candidate_successors (im0, im1, 0, 8, 1)
    d2 = candidate_lineaging.py_get_candidate_successors (im0, im1, 0, 8, 1)
    assert equal_lineages(d1, d2)


def test_one_div_shift():
    im0 = SpatialImage(np.ones((11,7,1), dtype=np.ushort))
    im1 = SpatialImage(np.ones((11,7,1), dtype=np.ushort))

    im0[1:-1,1:-1,:] = 2
    im1[1:4,1:-1,:] = 2
    im1[6:-1,1:-1,:] = 3

    #shifting creates a numpy array, let's recreate a SpatialImage out of it.
    im1 = SpatialImage( sci.ndimage.shift(im1, (2,2,0), cval=1) )

    # let's test with a distance larger than the offset
    d1 = candidate_lineaging.rfernandez_get_candidate_successors (im0, im1, 3, 8, 1)
    d2 = candidate_lineaging.py_get_candidate_successors (im0, im1, 3, 8, 1)
    print "====================================================================================="
    print d1
    print d2
    # let's test that we have the same lineages, disregarding score
    assert equal_lineages(d1,d2, epsilon=float("inf"))

    # now change the distance limit to be equal to the offset
    d1 = candidate_lineaging.rfernandez_get_candidate_successors (im0, im1, 2, 8, 1)
    d2 = candidate_lineaging.py_get_candidate_successors (im0, im1, 2, 8, 1)
    print "====================================================================================="
    print d1
    print d2
    # let's test that we have the same lineages, disregarding score
    assert equal_lineages(d1,d2, epsilon=float("inf"))

    # now change the distance limit to something smaller than the offset
    d1 = candidate_lineaging.rfernandez_get_candidate_successors (im0, im1, 1, 8, 1)
    d2 = candidate_lineaging.py_get_candidate_successors (im0, im1, 1, 8, 1)
    print "====================================================================================="
    print d1
    print d2
    # let's test that we have the same lineages, disregarding score (shift isn't enough to place
    # the barycenter of cell labeled "3" out of mother cell "2"
    assert equal_lineages(d1,d2, epsilon=float("inf"))


def test_zero_background():
    im0 = SpatialImage(np.zeros((11,7,1), dtype=np.ushort))
    im1 = SpatialImage(np.zeros((11,7,1), dtype=np.ushort))

    im0[1:-1,1:-1,:] = 1
    im1[1:4,1:-1,:] = 1
    im1[6:-1,1:-1,:] = 2

    im0_bg1 = SpatialImage(np.ones((11,7,1), dtype=np.ushort))
    im1_bg1 = SpatialImage(np.ones((11,7,1), dtype=np.ushort))

    im0_bg1[1:-1,1:-1,:] = 2
    im1_bg1[1:4,1:-1,:] = 2
    im1_bg1[6:-1,1:-1,:] = 3

    d1 = candidate_lineaging.rfernandez_get_candidate_successors (im0, im1, 3, 8, bkgdLabel=0, rfernandezLabelSpace=True)
    d2 = candidate_lineaging.rfernandez_get_candidate_successors (im0_bg1, im1_bg1, 3, 8, bkgdLabel=1)
    print d1
    print d2
    assert equal_lineages(d1,d2, epsilon=float("inf"))

    d1 = candidate_lineaging.py_get_candidate_successors (im0, im1, 3, 8, bkgdLabel=0, rfernandezLabelSpace=True)
    d2 = candidate_lineaging.py_get_candidate_successors (im0_bg1, im1_bg1, 3, 8, bkgdLabel=1)
    print d1
    print d2
    assert equal_lineages(d1,d2, epsilon=float("inf"))

