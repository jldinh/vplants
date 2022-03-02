import numpy as np
from openalea.image.serial.basics import imread
from vplants.mars_alt.all import filtering, seed_extraction, euclidean_sphere, mostRepresentative_filter, remove_small_cells

b1 = np.array([[[False,  True, False],
              [ True,  True,  True],
              [False,  True, False]],
              [[ True,  True,  True],
              [ True,  True,  True],
              [ True,  True,  True]],
              [[False,  True, False],
              [ True,  True,  True],
              [False,  True, False]]], dtype=bool)

b2 = np.array([[[False, False,  True, False, False],
              [False,  True,  True,  True, False],
              [ True,  True,  True,  True,  True],
              [False,  True,  True,  True, False],
              [False, False,  True, False, False]],
              [[False,  True,  True,  True, False],
              [ True,  True,  True,  True,  True],
              [ True,  True,  True,  True,  True],
              [ True,  True,  True,  True,  True],
              [False,  True,  True,  True, False]],
              [[ True,  True,  True,  True,  True],
              [ True,  True,  True,  True,  True],
              [ True,  True,  True,  True,  True],
              [ True,  True,  True,  True,  True],
              [ True,  True,  True,  True,  True]],
              [[False,  True,  True,  True, False],
              [ True,  True,  True,  True,  True],
              [ True,  True,  True,  True,  True],
              [ True,  True,  True,  True,  True],
              [False,  True,  True,  True, False]],
              [[False, False,  True, False, False],
              [False,  True,  True,  True, False],
              [ True,  True,  True,  True,  True],
              [False,  True,  True,  True, False],
              [False, False,  True, False, False]]], dtype=bool)

def test_euclidean_sphere_b1():
    ''' Test of the euclidean sphere with size = 1. '''
    assert (euclidean_sphere(1) == b1).all()

def test_euclidean_sphere_b2():
    ''' Test of the euclidean sphere with size = 2. '''
    assert (euclidean_sphere(2) == b2).all()

def test_mostRepresentative_filter():
    ''' Test of the mostRepresentative filter with a sphere of size = 2. '''
    image = imread('data/segmentation/imgDebug.13_wat.inr.gz')
    image_res = imread('data/segmentation/imgDebug.14_corr.inr.gz')
    res = mostRepresentative_filter(image,size=2)
    diff = len( res[np.abs(image_res - res)!= 0])
    assert float(diff)/(reduce(lambda x,y:x*y,res.shape)) < 0.01

    return res


def test_remove_small_cells():
    ''' Test of mips and vtissue remove_small_cells function
     for minimal cell volumes=1000 voxels '''
    #original image and mips filtered image
    seeds_mips = imread('data/segmentation/imgDebug.07_cc.inr.gz')
    wat1_mips = imread('data/segmentation/imgDebug.08_wat.inr.gz')
    newseeds_mips=imread('data/segmentation/imgDebug.12_cc.inr.gz')

    newseeds_vt=remove_small_cells(wat1_mips,seeds_mips,volume=1000,real=False)
    assert (newseeds_vt == newseeds_mips).all()

    return newseeds_vt

def test_filtering():
    ''' Test of mips and vtissue filtering for filtervalue=3 '''
    #original image and mips filtered image
    image = imread('data/segmentation/imgFus.inr.gz')
    filtered_mips = imread('data/segmentation/imgDebruitee.inr.gz')

    filtered_vt=filtering(image,filter_type="asf",filter_value=3)

    diff = len( filtered_vt[np.abs(filtered_mips - filtered_vt)!= 0])
    print "diff=",diff
    size=(reduce(lambda x,y:x*y,filtered_vt.shape))
    print "size=",size
    print "percentage=",float(diff)/size
    #assert float(diff)/size < 0.01
    return filtered_vt

def test_seed_extraction():
    ''' Test of mips and vtissue seed_extraction function
     with h_minima=3 '''
    seeds_mips = imread('data/segmentation/imgDebug.07_cc.inr.gz')
    filtered_mips = imread('data/segmentation/imgDebug.01_gauss.inr.gz')

    seeds_vt=seed_extraction(filtered_mips,h_minima=3)

    assert (seeds_vt == seeds_mips).all()
    return seeds_vt

