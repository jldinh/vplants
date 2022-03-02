import numpy as np

from openalea.image.all import imread, SpatialImage
from vplants.mars_alt.mars.segmentation import filtering


def test_gaussian():
    im          = imread('data/imgFus_0.inr.gz')
    im_ref      = imread('data/imgFus_0_filtered_gauss_sigma_3.inr.gz')
    im_half_ref = imread('data/imgFus_0_half_filtered_gauss_sigma_3.inr.gz')

    filtered = filtering(im, "gaussian", 3.0)
    np.testing.assert_array_equal(filtered, im_ref)

    half = im[:,:im.shape[1]/2,:]    
    filtered = filtering(half, "gaussian", 3.0)
    np.testing.assert_array_equal(filtered, im_half_ref)
