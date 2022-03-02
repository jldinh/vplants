# -*- python -*-
#
#       vplants.mars_alt.alt.deformation_field
#
#       Copyright 2010-2011 INRIA - CIRAD - INRA
#
#       File author(s): Christophe Pradal
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#       http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
#
#       OpenAlea WebSite : http://openalea.gforge.inria.fr
#
################################################################################

__license__= "Cecill-C"
__revision__ = " $Id$ "

import numpy as np
import scipy.ndimage as ndimage
from openalea.image.spatial_image import SpatialImage
from openalea.image.serial.basics import lazy_image_or_path
from openalea.tissueshape import create_graph_tissue
from alt_preparation import mapping2barycenter, alt_preparation


from openalea.image.interpolation.interpolation import deformation_field as pts_to_field


def deformation_field( imgSeg0, imgSeg1, imgFus0, mapping, sigma, T_vox=None,
                       res0=(1.,1.,1.), res1=(1.,1.,1.),
                       points0=None, points1=None, inv=False, dtype=np.float64):
    """

    :Principles:

    This module implements an interpolation of the vector field based on a set of
    high confidence lineages.


    :Algorithm:

    First the vector that links the centre of mass (point0) in each one of the parent
    cells and the center of mass (point1) of its descendants is computed.

    Then, the dense vector field is computed by interpolating between these vectors
    using an smoothed SKIZ.  The SKIZ is obtained and smoothed by using a Gaussian filter (:math:`\sigma`=5).


    :Parameters:
	- `imgSeg0` (|SpatialImage|) - segmented image representing the parent cells
	- `imgSeg1` (|SpatialImage|) - segmented image representing the daugther cells
	- `mapping' (dict) - expert mapping for initialisation
	- 'sigma' (float, optional) - standard deviation of the Gaussian function. Default Sigma = 5.

    :Returns:
	vector field

    :Returns Type:
	|SpatialImage|

    :Examples:
        ::

	from vplants.mars_alt import deformation_field



    """
    if points0 == None or points1 == None:
        points0,points1=mapping2barycenter( imgSeg0, imgSeg1, mapping )


    points0 /= np.array(res0)
    points1 /= np.array(res1)

    # -- try to save some memory... --
    del imgSeg0, imgSeg1, mapping

    # -- Put points0 (from tissue0) into tissue1 space --
    if T_vox is not None:
        # - T_vox is in homogeneous coordinates, we must convert points0 to homogeneous coords -
        points0 = np.concatenate( (points0, np.ones(shape=(points0.shape[0],1))),
                                  axis=1)
        # - now we can dot the matrix and each vector -
        points0 = np.transpose(np.dot(T_vox, np.transpose(points0)))[:,:3]


    image, was_path = lazy_image_or_path(imgFus0)
    if not inv:
        return pts_to_field(image, points0, points1, sigma, dtype=dtype)
    else:
        return pts_to_field(image, points1, points0, sigma, dtype=dtype)



if __name__ == "__main__":
    from openalea.image.serial.basics import imread
    from openalea.image.serial.inrimage import write_inrimage, read_inriheader
    from vplants.mars_alt.alt.mapping import lineage_from_file
    import sys
    import os.path
    import os
    import gc

    print "checking data..."
    assert len(sys.argv)==7

    for i in range(1,5):
        f = sys.argv[i]
        f = f if os.path.isabs(f) else os.path.join(os.getcwd(), f)
        print "Checking", f
        assert f.endswith("inr.gz") or f.endswith("inr")
        if i != 4: # outpuf file can not exist yet
            assert os.path.isfile(f)


    # -- obtain the paths --
    imgFus0_pth  = sys.argv[1]
    imgSeg0_pth  = sys.argv[2]
    imgSeg1_pth  = sys.argv[3]
    outputf_pth  = sys.argv[4]
    mapping_pth  = sys.argv[5]
    sigma_str    = sys.argv[6]

    sigma = int(sigma_str)

    # -- read data --
    print "reading data"
    #  - only read header of segmented images -
    imgSeg0_header = read_inriheader(imgSeg0_pth)
    imgSeg1_header = read_inriheader(imgSeg1_pth)
    res0 = tuple(float(imgSeg0_header.pop(k) ) for k in ("VX","VY","VZ") )
    res1 = tuple(float(imgSeg1_header.pop(k) ) for k in ("VX","VY","VZ") )
    del imgSeg0_header, imgSeg1_header

    mapping = lineage_from_file(mapping_pth)

    # -- compute the initial transform --
    print "initial rigid transform and morphometry"
    useless0, useless1, T_vox, tissue0, tissue1 = alt_preparation(mapping, None, None, imread(imgSeg0_pth), imread(imgSeg1_pth))

    print "deformation field computation"
    field = deformation_field(tissue0, tissue1, imread(imgSeg0_pth), mapping, sigma, T_vox=None, res0=res0, res1=res1)
    del tissue0, tissue1, mapping, T_vox, res0, res1
    gc.collect()
    write_inrimage(outputf_pth, field)

    sys.exit(0)

