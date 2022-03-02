# -*- python -*-
#
#       vplants.mars_alt.alt.candidate_lineaging
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
__revision__ = " $Id: candidate_lineaging.py 11309 2011-10-26 12:06:20Z dbarbeau $ "

import numpy as np
import scipy as sp
from scipy.spatial import KDTree
from scipy.spatial import distance as sc_dist
from scipy import ndimage as nd



from openalea.core.logger import get_logger
myLogger = get_logger(__name__)



def candidate_lineaging(im_0, im_1,
                        dist=3, ndiv=8,
                        bkgdLabel=1,
                        rfernandezCompatible=True,
                        candidate_method="cell_shape",
                        ):
    """ Given two images of an organ at t0 and t1, tries to find cell lineages.

    :Parameters:
      - `im_0` :  segmented image of organ a t0
      - `im_1` :  segmented image of organ a t1
      - `dist` :  distance between mother boundary and child barycenter beyond which child is disregarded.
      - `ndiv` :  a limit to the number of divisions a cell can have between two images.
      - `bkgdLabel` : value of the background label of the input images.
      - `candidate_method` : name of the method to use. "cell_shape" means that the distance `dist` is computed
                           starting from the mother cell's boundary. "cell_as_box" considers cells as boxes and the distance
                           is computed from the mother cell's barycenter corrected by the mean radius of cells. The mean radius of cell
                           is the mean diagonal of all cells' bouding boxes.

    :Returns:
	Mapping of mother to candidate children with a score (or a distance) for each child.

    :Returns Type:
	dict
      """
    if candidate_method=="cell_shape":
        cfunc = rfernandez_get_candidate_successors
    elif candidate_method=="cell_as_box":
        cfunc = py_get_candidate_successors
    else:
        myLogger.error("unknown candidates method: " + candidate_method)
        return

    return cfunc(im_0, im_1, dist, ndiv, bkgdLabel=bkgdLabel, as_scores=True)















#######################################################
# Methods to get the candidates using numpy and scipy #
#######################################################
def py_get_candidate_successors(imgSeg0, imgSeg1, distance, ndiv, bkgdLabel, as_scores=True, rfernandezLabelSpace=False):
    """Estimates candidate lineages between cells in imgSeg0 and cells in imgSeg1.

    This method approximates the cells as boxes. Images must be 3D (even if only one pixel wide in Z).

       :Parameters:
	- `imgSeg0` (|SpatialImage|) - segmented image representing the parent cells
	- `imgSeg1` (|SpatialImage|) - segmented image representing the daugther cells
	- `distance` (float) - distance between mother boundary and child barycenter beyond which child is disregarded.
	- `ndiv` (int) - number of divisions between two images.
        - `bkgdLabel` (int) - label to consider as the background.
        - `as_scores` (bool, optional) - if True, the returned mapping contains scores (highest confidence is 1.0,
           lowest confidence is 0.0) else the mapping contains relative distances (highest confidence is 0.0,
           lowest condidence is one).
        - `rfernandezLabelSpace` (bool, optional) - Returned labels are compatible with the rest of the tools (background label is 1).

    :Returns:
	Mapping of mother to candidate children with a score (or a distance) for each child.

    :Returns Type:
	dict
    """
    # -- for each label in each image create the bounding box --
    # -- then for each bounding box of cell in imgSeg0 get the ndiv in the
    # -- cells from imgSeg1, based on some distance

    # If we want results to be compatible with rfernandez' tools
    # we must offset the final labels so that 1 is the background.
    labelOffset = 1-bkgdLabel

    # step 1 : build the bboxes:
    im0Boxes = get_bounding_boxes(imgSeg0, bkgdLabel)
    im1Boxes = get_bounding_boxes(imgSeg1, bkgdLabel)

    # print im0Boxes
    # print im1Boxes

    candidate_map = get_closest_per_label(im0Boxes, im1Boxes,
                                          distance, ndiv, bkgdLabel, as_scores,
                                          labelOffset=0 if not rfernandezLabelSpace else labelOffset)

    if not rfernandezLabelSpace:
        candidate_map[bkgdLabel] = [(bkgdLabel, 1.0)]
    else:
        candidate_map[bkgdLabel+labelOffset] = [(bkgdLabel+labelOffset, 1.0)]
    return candidate_map


def get_bounding_boxes(image, bkgdLabel):
    """Gets the bounding box in real coordinates for each label in image.

    :Parameters:
	- `imgSeg` (|SpatialImage|) - segmented image representing the cells
	- `bkgdLabel` (int) - value of the background label

    :Returns:
        A dictionnary mapping cell labels to bounding boxes in real coordinates.
    """
    # the max bound of a box is an index, but we are
    # using volumes so it's the index of the voxel
    # at the corner of the one found that should be used.
    # find_object returns slices so this is taken into account
    # however, it expects labels to start at 1, 0 being the background:
    image_bis = image-bkgdLabel
    # step 1 : build the bboxes:
    objs = nd.find_objects(image_bis)
    # step 1.1 : get label indices
    # l+bkgdLabel+1 : l ranges from 0 to len(objs). Our real labels start at bkgdLabel+1
    rez = image_bis.resolution # we correct the indices by the voxel sizes.
    imBoxes = dict( (l+bkgdLabel+1, np.array([np.array([x.start, y.start, z.start]), np.array([x.stop, y.stop, z.stop])])*rez)
                   for l, (x, y, z) in enumerate(objs))
    return imBoxes


def get_closest_per_label(boxDict0, boxDict1, distance, ndiv, bkgdLabel, as_scores=True, labelOffset=0):
    """Return a candidate mapping given two sets of cell bounding boxes.

    :Parameters:
	- `boxDict0`   (dict)  - dictionnary mapping mother cells to their bounding boxes.
	- `boxDict1`   (dict)  - dictionnary mapping child cells to their bounding boxes.
	- `distance`   (float) - distance to mother's bounding box beyond which child cells are disregarded.
                               Child cells that have their barycenters within the mother BB have a distance of 0.0.
	- `ndiv` (int)       - number of possible divisions between two images
        - `bkgdLabel`   (int)  - value of the background label.
        - `as_scores`   (bool) - return scores instead of relative distances.
        - `labelOffset` (bool) - offset to make returned labels start at a given value.

    :Returns:
	vector field

    :Returns Type:
	|SpatialImage|


    """
    # build kdtree for children based on bbox centroids.
    def centroid_radius(l,v):
        cent = (v[0]+v[1])/2.0
        radius = sc_dist.euclidean(cent, v[0])
        return cent, radius

    # correct the distance by the mean radius of cells
    centAndRad = [centroid_radius(l,v) for l,v in boxDict0.iteritems()]
    centroids0, radii = zip(*centAndRad)
    centroids0 = np.array(centroids0)
    centroids1 = np.array([(v[0]+v[1])/2.0 for l,v in boxDict1.iteritems()])
    radius     = np.max(radii)
    correctedDistance = distance+radius

    # now build the kdtree and do the query
    maxKids = ndiv
    tree      = KDTree(centroids1)
    closests  = tree.query(centroids0,
                           k=maxKids,
                           p=2.0,
                           distance_upper_bound=correctedDistance)

    # -- great, that was easy, now rebuild a dictionnary
    # mapping mommy labels to (child_label, distance) tuples. --
    d = {}
    inf = float("inf")

    for momIndex in xrange(len(centroids0)):
        childTupleList = zip(closests[1][momIndex], closests[0][momIndex])
        for childTreeIndex, dist in childTupleList:
            if dist < inf:
                realChildLabel = childTreeIndex+bkgdLabel+1
                realMomLabel   = momIndex+bkgdLabel+1
                mommyBB = boxDict0[realMomLabel]
                chPt    = tree.data[childTreeIndex]

                # per mother, let's restrict the kids to those
                # that fall into the mommy's bounding box (adjusted with distance)
                ptInBox = point_in_box(chPt, mommyBB, margin=distance)
                if ptInBox < 0: # out of the box!
                    continue
                elif ptInBox == 0: # strictly in mommy's BB
                    reldist = 0.0
                else: # in the mommy's adjusted bb
                    if distance == 0.0:
                        reldist = 0.0
                    else:
                        reldist = (dist-radius)/float(distance)

                if not as_scores:
                    d.setdefault(realMomLabel+labelOffset, []).append( (realChildLabel+labelOffset, reldist) )
                else:
                    d.setdefault(realMomLabel+labelOffset, []).append( (realChildLabel+labelOffset, 1-reldist) )
    return d

def point_in_box(pt, box, margin=0.0):
    """Test if 3D pt is is box.

    :Parameters:
        - `pt` (3-uple) - the point to test
        - `box` (3-uple-of-2-uples) - the box ((minX, maxX), (minY, maxY), (minZ, maxZ))
        - `margin` (float) - a distance to consider for non-strict matching.


    :Returns:
        If it's beyond the box (adjusted by the margin) : returns -1
        If it is strictly inside (or on the border) of the box : return 0
        If it is in the margin, return 1.
    """

    loose = box[0][0]-margin <= pt[0] <= box[1][0]+margin and \
            box[0][1]-margin <= pt[1] <= box[1][1]+margin and \
            box[0][2]-margin <= pt[2] <= box[1][2]+margin

    if not loose:
        return -1

    strict = box[0][0] <= pt[0] <= box[1][0] and \
             box[0][1] <= pt[1] <= box[1][1] and \
             box[0][2] <= pt[2] <= box[1][2]

    return 0 if strict else 1









##############################################################
# Methods to get the candidates using romain's code          #
# You should worship me for ages for doing this! (or not).   #
##############################################################
import os
import ctypes
import struct
from openalea.core.ctypes_ext import find_library
if os.name != "posix":
    from ctypes.util import find_msvcrt

def rfernandez_get_candidate_successors(imgSeg0, imgSeg1, distance, ndiv,
                                        bkgdLabel, as_scores=True, rfernandezLabelSpace=False):
    """Estimates candidate lineages between cells in imgSeg0 and cells in imgSeg1.

    This method uses the original implementation from Romain Fernandez.

    .. note:: Images must be 3D (even if only one pixel wide in Z) and in ushort.

    :Parameters:
     - `imgSeg0` (|SpatialImage|) - segmented image representing the parent cells (encoded in ushorts).
     - `imgSeg1` (|SpatialImage|) - segmented image representing the daugther cells (encoded in ushorts).
     - `distance` (float) - distance between mother boundary and child barycenter beyond which child is discarded.
     - `ndiv` (int) - number of divisions between two images.
     - `bkgdLabel` (int) - label to consider as the background.
     - `as_scores` (bool, optional) - if True, the returned mapping contains scores (highest confidence is 1.0,
        lowest confidence is 0.0) else the mapping contains relative distances (highest confidence is 0.0,
       lowest condidence is one).
     - `rfernandezLabelSpace` (bool, optional) - Returned labels are compatible with the rest of the tools (background label is 1).

    :Returns:
	Mapping of mother to candidate children with a score (or a distance) for each child.

    :Returns Type:
	dict
    """
    # Cast to UINT16 if possible or raise exception. This is
    # required because the C function takes 16 bit images only.
    imgSeg0 = __cast_or_die(imgSeg0, "imgSeg0")
    imgSeg1 = __cast_or_die(imgSeg1, "imgSeg1")

    assert imgSeg0.resolution == imgSeg1.resolution
    assert imgSeg0.shape == imgSeg1.shape

    # For images that have a background different than 1
    # we must offset the labels so that 1 is the background
    # because that is what Romain's C++ implementation expects.
    labelOffset = 1-bkgdLabel
    if bkgdLabel!=1:
        imgSeg0 = imgSeg0 + labelOffset
        imgSeg1 = imgSeg1 + labelOffset

    # -- lets configure the ctypes accesses --
    CT_USHORT_P = ctypes.POINTER(ctypes.c_ushort)
    CT_UINT_P   = ctypes.POINTER(ctypes.c_uint)
    CT_DOUBLE_P = ctypes.POINTER(ctypes.c_double)

    candyLib = ctypes.CDLL(find_library("lineage"))
    candyLib.compute_candidates.argtypes = [ctypes.c_double, #distance
                                            ctypes.c_uint, #nbCells1
                                            ctypes.c_uint, #nbCells2
                                            ctypes.c_uint, #sx_im1
                                            ctypes.c_uint, #sy_im1
                                            ctypes.c_uint, #sz_im1
                                            CT_USHORT_P,   #data_im1
                                            ctypes.c_uint, #sx_im2
                                            ctypes.c_uint, #sy_im2
                                            ctypes.c_uint, #sz_im2
                                            CT_USHORT_P,   #data_im2
                                            ctypes.c_double, #vx
                                            ctypes.c_double, #vy
                                            ctypes.c_double, #vz
                                            ctypes.POINTER(CT_UINT_P),
                                            ctypes.POINTER(CT_UINT_P),
                                            ctypes.POINTER(CT_DOUBLE_P),
                                            CT_UINT_P
                                            ]

    # -- we also need access to cstdlib::free(void*) --
    libcName = find_library("c") if os.name == "posix" else find_msvcrt()
    libc = ctypes.CDLL(libcName)

    # -- max i0 and i1 labels: corrected by one for
    # bkgd that is reserved for watershed --
    max0 = imgSeg0.max()+1
    max1 = imgSeg1.max()+1

    shape0 = imgSeg0.shape
    shape1 = imgSeg1.shape

    rez0 = imgSeg0.resolution
    rez0 = rez0 if len(shape0)==3 else (rez0[0], rez0[1], 1.0)

    sx0, sy0, sz0 = shape0 if len(shape0)==3 else (shape0[0], shape0[0], 1)
    sx1, sy1, sz1 = shape1 if len(shape1)==3 else (shape1[0], shape1[0], 1)

    # -- the compute_candidates function returns the mapping of mother to
    # child and score in the shape of three arrays where mom[i] -> (kids[i], score[i]
    # we don't know the size, it is returned by reference in nPairs.
    moms   = CT_UINT_P()
    kids   = CT_UINT_P()
    scores = CT_DOUBLE_P()
    nPairs = ctypes.c_uint(0)

    candyLib.compute_candidates(distance,
                                max0,
                                max1,
                                sx0,
                                sy0,
                                sz0,
                                imgSeg0.ctypes.data_as(CT_USHORT_P),
                                sx1,
                                sy1,
                                sz1,
                                imgSeg1.ctypes.data_as(CT_USHORT_P),
                                rez0[0],
                                rez0[1],
                                rez0[2],
                                ctypes.byref(moms),
                                ctypes.byref(kids),
                                ctypes.byref(scores),
                                ctypes.byref(nPairs)
                                )

    if not rfernandezLabelSpace:
        retDict = {bkgdLabel:[(bkgdLabel, 1.0)]}
    else:
        retDict = {bkgdLabel+labelOffset:[(bkgdLabel+labelOffset, 1.0)]}
    nPairs = nPairs.value #get the python equivalent
    for i in range(nPairs):
        sc = scores[i]
        sc = sc if as_scores else 1-sc
        if not rfernandezLabelSpace:
            # we must substract labelOffset as we incremented the labels
            # previously, to be compatible with the C++ implementation.
            retDict.setdefault(moms[i]-labelOffset, []).append( (kids[i]-labelOffset, sc) )
        else:
            retDict.setdefault(moms[i], []).append( (kids[i], sc) )

    libc.free(moms)
    libc.free(kids)
    libc.free(scores)

    return retDict


def __cast_or_die(image, imname):
    uint16_max = np.iinfo(np.ushort).max
    if image.dtype != np.ushort:
        m = image.max()
        if uint16_max >= m:
            return np.ushort(image)
        else:
            raise Exception("rfernandez_get_candidate_successors: %s is %s "
                            "and cannot be safely cast to uint16, "
                            "maximum in image is %d"%(imname, str(imgSeg0.dtype), m))
    return image







###################
# Utility Methods #
###################
def equal_lineages(d1, d2, epsilon=1e-10):
    """Compare two mappings and return True.
    If the mappings are candidate mappings then the values
    are list of (child, score) tuples. In that case the epsilon
    is used to compare the scores (if difference of scores < epsilon, then
    they are the same).

    :Parameters:
        - `d1` (dict) - a mapping from mother label to child labels. Child labels can be (label, score(float)) tuples.
        - `d2` (dict) - a mapping from mother label to child labels. Child labels can be (label, score(float)) tuples.
        - `epsilon` (float) - In case child list contains scores, scores between d1 and d2 childs are the same if
                              their difference is below epsilon.

    :Returns:
        True if keys are the same in d1 and d2, if m1 has the same child labels as m2 and if child score differences are below
        epsilon. Else False.

    :Return Type:
        bool
    """
    #if dictionnary values are list of tuples
    #then it is a candidate mapping
    areCandidates = isinstance(d1[ list(d1.iterkeys())[0] ][0], tuple)

    eq = set(d1) == set(d2)
    if not eq:
        return False

    for parent0, kids1 in d1.iteritems():
        if not areCandidates:
            kids2 = d2[parent0]
            eq = set(kids1)==set(kids2)
        else:
            kids1 = dict(kids1)
            kids2 = dict(d2[parent0])
            eq = set(kids1) == set(kids2)
            if not eq:
                return False
            for v in kids1:
                eq = abs(kids1[v]-kids2[v]) <= epsilon
                if not eq:
                    return False
        if not eq:
            return False

    return True


def compare_lineages(reference, lineage):
    """ gives a score regarding the quality of ``lineage`` compared to an expert ``reference`` mapping. """

    ref_moms = set(reference.iterkeys())
    lin_moms = set(lineage.iterkeys())

    # ugh -- this logic can be off as I'm tired right now --
    good_moms   = ref_moms & lin_moms
    wrong_moms  = lin_moms - good_moms
    missed_moms = ref_moms - good_moms

    good_moms_scores = {}

    for good_lin_mom in good_moms:
        ref_kids  = set(reference[good_lin_mom])
        lin_kids  = set(lineage[good_lin_mom])

        # -- same here --
        good_kids   = ref_kids & lin_kids
        wrong_kids  = lin_kids - good_kids
        missed_kids = ref_kids - good_kids

        assert len(good_kids) <= len(ref_kids)
        good_moms_scores[good_lin_mom] = ( float(len(good_kids)) / len(ref_kids), good_kids, wrong_kids, missed_kids)

    assert len(good_moms_scores) == len(good_moms)

    # The final score is (n_good_moms/n_reference_moms) * ( sum(good_mom_scores)/n_good_moms)
    n_good_moms      = len(good_moms)
    n_reference_moms = float(len(reference))

    if n_good_moms:
        cum_score = __sum_scores(good_moms_scores)
        assert cum_score <= n_good_moms
        score = (n_good_moms/n_reference_moms) * (cum_score/n_good_moms)
    else:
        score = 0

    return score, good_moms, wrong_moms, missed_moms, good_moms_scores


def __sum_scores(d):
    sum = 0
    for k in d.itervalues():
        sum += k[0]
    return sum

def candidate_contains_expert(reference, candidate):
    """ Tells if the candidate space contains the expert space."""
    ref_moms = set(reference.iterkeys())
    can_moms = set(candidate.iterkeys())

    moms_contained = ref_moms.issubset(can_moms)
    if not moms_contained:
        return False, ref_moms-can_moms, None

    missing_candidates = {}

    for ref_mom, ref_kids in reference.iteritems():
        ref_kids = set(ref_kids)
        # -- candidate kids are tuples of (label, score), we want the label --
        can_kids = set( k[0] for k in candidate[ref_mom] )
        if not can_kids.issuperset(ref_kids):
            missing_candidates[ref_mom] = ref_kids - can_kids

    return len(missing_candidates) == 0, None, missing_candidates
