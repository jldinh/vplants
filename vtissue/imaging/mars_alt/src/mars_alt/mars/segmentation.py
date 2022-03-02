# -*- python -*-
#
#       vplants.mars_alt.mars.segmentation
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
__revision__ = " $Id$ "

import numpy as np
from scipy import ndimage

from openalea.image.spatial_image          import SpatialImage
from openalea.image.algo.basic             import logicalnot
from vplants.asclepios.vt_exec.morpho      import dilation, erosion
from vplants.asclepios.vt_exec.recfilters  import recfilters
from vplants.asclepios.vt_exec.regionalmax import regionalmax
from vplants.asclepios.vt_exec.connexe     import hysteresis, connected_components
from vplants.asclepios.vt_exec.watershed   import watershed
#from openalea.tissueshape                  import create_graph_tissue
from openalea.image.algo.analysis          import SpatialImageAnalysis

from openalea.core.logger import get_logger
mylogger = get_logger(__name__)

from scipy import ndimage as nd
from scipy.ndimage.morphology import grey_erosion, grey_dilation


def filtering (img, filter_type="gaussian", filter_value=0.5):
    """
    Applies a smoothing filter to the image.
    :Parameters:
    - `image` (|SpatialImage|) - image

    - `filter_type`(str) - denoising method used for filtering ("gaussian" or "asf" for alternate sequential filter,
                           or "mr" for most representative).
                           default is "gaussian".

    - `filter_value` (float for "gaussian" filter or int for alternate sequential filter) - value used for the filtering :
                                            * for a Gaussian filtering, the "filter_value" corresponds to the standard deviation.
                                            * for a Alternate Sequential Filter, the "filter_value" corresponds to the number of
                                              succession of morphological opening and closing operations.
                                              
    :See:
     - :mod:`~vplants.asclepios.vt_exec.morpho`
     - :mod:`~vplants.asclepios.vt_exec.recfilters`
     - :mod:`~vplants.asclepios.vt_exec.regionalmax`
     - :mod:`~vplants.asclepios.vt_exec.connexe`
     - :mod:`~vplants.asclepios.vt_exec.watershed`
    """
    if not isinstance(img,SpatialImage) or not img.flags.f_contiguous:
        img = SpatialImage(img)

    if filter_type == 'gaussian':
        filter_value = float(filter_value)
        img = recfilters(img,filter_type="sigma",filter_value=filter_value,xyz=(0,0,0))
    elif filter_type == 'asf':
        filter_value = int(round(filter_value))
        img = alternate_sequential_filter(img, filter_value)
    elif filter_type == "mr":
        filter_value = int(round(filter_value))
        img = mostRepresentative_filter(img, filter_value)
    else:
        raise RuntimeError, 'filter type not supported'

    return img


def seed_extraction (img,h_minima):
    """
    :Parameters:
    - `image` () - image
    - `h_minima` (int) - The parameter "h_minima" allows controlling the pertinence of extracted minima:
                         two neighboring basins will be merged if they are separated by a "mountain" whose minimal height
                         (with respect to the higher basin) is less than "h_minima".

    :See:
     - :func:`~vplants.asclepios.vt_exec.regionalmax.regionalmax`
     - :func:`~vplants.asclepios.vt_exec.connexe.hysteresis`
     - :func:`~vplants.asclepios.vt_exec.connexe.connected_components`

    """
    if not isinstance(img,SpatialImage):
        img = SpatialImage(img)

    inv = logicalnot(img)
    regmax = regionalmax(inv,h_minima) # This didn't return a binary image
    thres = hysteresis(regmax,1,h_minima,connectivity=6) # this make the image binary (with some other stuffs to determine ...
    seeds = connected_components(thres,1) # this find connected components and give them an ID 
    return seeds


def remove_anormal_sized_cells (segmented_image,image_markers, volume_max,volume_min=None,real=False) :
    """
    Cell with too small volume are removed. The other are set by a threshold value.

    :Parameters:
      - `segmented_image` (|SpatialImage|) - segmented image
      - `image_markers` (|SpatialImage|) - labeled markers image
      - `volume` (int) - minima volume
      - `real` (bool, optional) - If real = True, volume is in real-world units else in voTrueels.

    :See:
     - :func:`~openalea.tissueshape.create_graph_tissue`
     - :func:`~vplants.asclepios.vt_exec.connexe.connected_components`

    """
    # create a graph
    #db = create_graph_tissue(segmented_image)
    #nb = db.get_property('nb')
    analysis=SpatialImageAnalysis(segmented_image)
    volumes=analysis.volume()
    labels=analysis.labels()
    nb = dict(zip(labels, np.uint(volumes)))
    threshold = 255
    seeds = image_markers.copy()
    nb.pop(1)
    if volume_min==None:
        volume_min=np.uint(np.mean(nb.values())-0.25*np.std(nb.values()))
    for c, v in nb.items():
        if not (volume_min<v<volume_max):
            print "remove cell number %s,volume %s" %(c,v)
            seeds[seeds==c]=0

    img = np.where(seeds != 0 , threshold, 0)
    image = SpatialImage(np.uint8(img), segmented_image.resolution)
    new_seeds = connected_components( image, 1)
    return new_seeds


def remove_small_cells (segmented_image,image_markers,volume_min=None,real=False) :
    """
    Cell with too small volume are removed. The other are set by a threshold value.

    :Parameters:
      - `segmented_image` (|SpatialImage|) - segmented image
      - `image_markers` (|SpatialImage|) - labeled markers image
      - `volume` (int) - minima volume
      - `real` (bool, optional) - If real = True, volume is in real-world units else in voTrueels.

    :See:
     - :func:`~openalea.tissueshape.create_graph_tissue`
     - :func:`~vplants.asclepios.vt_exec.connexe.connected_components`

    """
    analysis=SpatialImageAnalysis(segmented_image)
    volumes=analysis.volume()
    labels=analysis.labels()
    nb = dict(zip(labels, np.uint(volumes)))
    threshold = 255
    seeds = image_markers.copy()
    nb.pop(1)
    if volume_min==None:
        volume_min=np.uint(np.mean(volumes)-0.5*np.std(volumes))
    
    for c, v in nb.items():
        if v < volume_min:
            print "remove cell number %s,volume %s" %(c,nb[c])
            seeds[seeds==c]=0
    
    img = np.where(seeds != 0 , threshold, 0)
    image = SpatialImage(np.uint8(img), segmented_image.resolution)
    new_seeds = connected_components( image, 1)
    return new_seeds


def remove_big_cells (segmented_image,image_markers,volume,real=False) :
    """
    Cell with too big volume are removed. The other are set by a threshold value.

    :Parameters:
      - `segmented_image` (|SpatialImage|) - segmented image
      - `image_markers` (|SpatialImage|) - labeled markers image
      - `volume` (int) - minima volume
      - `real` (bool, optional) - If real = True, volume is in real-world units else in voTrueels.

    :See:
     - :func:`~openalea.tissueshape.create_graph_tissue`
     - :func:`~vplants.asclepios.vt_exec.connexe.connected_components`

    """
    # create a graph
    #db = create_graph_tissue(segmented_image)
    #nb = db.get_property('nb')
    analysis=SpatialImageAnalysis(segmented_image)
    volumes=analysis.volume()
    labels=analysis.labels()
    nb = dict(zip(labels, volumes))
    threshold = 255
    seeds = image_markers

    for c in xrange(2,segmented_image.max()+1):
        if nb[c] > volume:
            print "remove cell number %s,volume %s" %(c,nb[c])
            seeds = np.where(seeds == c, 0, seeds)

    img = np.where(seeds != 0, threshold, 0)
    image = SpatialImage(np.uint8(img), segmented_image.resolution)
    new_seeds = connected_components( image, 1)
    return new_seeds


def euclidean_sphere(size):
    """
    Generate a euclidean sphere for binary morphological operations

    :Parameters:
        - `size` (int) - the shape of the euclidean sphere = 2*size + 1.

    :Returns:
        - Euclidean sphere which may be used for binary morphological operations, with shape equal to 2*size + 1.
    """
    n = int(2*size + 1)
    sphere = np.zeros((n,n,n),np.bool)
    for x in range(n):
        for y in range(n):
            for z in range(n):
                if abs(x-size)+abs(y-size)+abs(z-size)<=2*size:
                    sphere[x,y,z]=True
    return sphere


def mostRepresentative_filter(img,size=1):
    """
    The most representated value in a neighborhood is calculated with a multi-dimensional median filter
    and a Euclidean sphere as structuring element.

    :Parameters:
        - `image` (SpatialImage) - image to filter.
        - `size` (int, optional) - the shape of the euclidean sphere = 2*size + 1. Default: size = 1

    :Returns:
        - Denoising image.

    :See:
     - :func:`~scipy.ndimage.median_filter`

    """
    sphere = euclidean_sphere(size)
    return ndimage.median_filter(img,footprint=sphere)


def alternate_sequential_filter(img, size):
    """ Applies a sequence of dilation/erosions "size" times. """
    resolution = img.resolution
    for rad in xrange(1,((size+1)/2)+1) :
        print "closing operations with structuring elements of size %s" %rad
        struct=euclidean_sphere(rad)
        #~ s=(rad,rad,rad)
        img = grey_dilation(img,footprint=struct)
        img = grey_erosion(img,footprint=struct)

        if size >= rad*2 :
            print "opening operations with structuring elements of size %s" %rad
            img = grey_erosion(img,footprint=struct)
            img = grey_dilation(img,footprint=struct)
    return SpatialImage(img, resolution=resolution)

def cell_segmentation(image,h_minima,volume,real=False,prefilter=True,filter_type="gaussian",filter_value=0.5):
    """
    This function does a complete cell segmentation loop as described in R. Fernandez et al. 2010 (Nature Methods).

    That is to say: a first filtering step (if prefilter is True), then the seeds are extracted,
    a first watershed is done, the result is filtered and seeds of small cells are removed, and
    finally a new watershed is done.

    :Parameters:

    - `image` (|SpatialImage|) - image

    - `h_minima` (int) -    The parameter "h_minima" allows controlling the pertinence of eTruetracted minima:
                            two neighboring basins will be merged if they are separated by a "mountain" whose minimal height
                            (with respect to the higher basin) is less than "h_minima".

    - `volume` (int) -      Cell with too small "volume" are removed.

    - `real` (bool) -       If real = True, volume is in real-world units else in voTrueels.

    - `prefilter` (bool) -  The parameter "prefilter" determines if the input is pre-filtered before seed eTruetraction
                            (necessary for enhance the signal/noise ratio and eliminate high frequency noise).
                            If False, it is assumed that the input is already filtered.
                            Default : Gaussian filtering with a standard deviation of 0.5.

    - `filter_type` (str) - Either "gaussian" or "asf" or "mr"


    :See:
     - :func:`~vplants.mars_alt.mars.segmentation.filtering`
     - :func:`~vplants.mars_alt.mars.segmentation.seed_extraction`
     - :func:`~vplants.asclepios.vt_exec.watershed.watershed`
     - :func:`~vplants.mars_alt.mars.segmentation.remove_small_cells`
    """

    if not isinstance(image,SpatialImage):
        image = SpatialImage(image)

    mylogger.info("denoising")
    if prefilter :
        img = filtering(image,filter_type,filter_value)

    mylogger.info("seed extraction")
    seeds = seed_extraction(img,h_minima)
    

    mylogger.info("watershed transformation")
    wat = watershed(seeds,img)

    mylogger.info("over-segmentation correction")
    new_seeds = remove_small_cells (wat,seeds,volume,real=real)

    return watershed (new_seeds,img), img, wat, seeds, new_seeds

