from openalea.image.all import *
from openalea.tissueshape import *
from vplants.mars_alt.all import alt_preparation, mapping2barycenter
from mapping_init_01 import mapping_init
import numpy as np

# Use to test if the two matrices are equal
epsilon=1e-5


if True:
    ######################################################
    # this cannot work, the file for im0 does not exist! #
    ######################################################
    im0 = imread("data/seg_1_ok.inr.gz")
    im1 = imread("data/seg_2_ok.inr.gz")
    # imgFus0 = imread("data/imgFus_0.inr.gz")
    # imgFus1 = imread("data/imgFus_1.inr.gz")


    # Use to test if the two transform matrix are equal
    def test_mapping2transfo():
        tissue0 = create_graph_tissue(im0)
        tissue1 = create_graph_tissue(im1)

        (points1,points0)= mapping2barycenter(tissue0,tissue1,mapping_init)
        T=pts2transfo(points1,points0)
        TTest=np.loadtxt("data/matTestTransfo.txt")
        assert (np.abs(TTest-T) < epsilon).all()

    # Use to test if the two segmented and fusion images are not very different after the transformation
    def test_alt_preparation():
        #Fusion image
        img1,img2, tis0, tis1, t=alt_preparation (imgFus0, imgFus1, im0, im1, mapping_init)
        t1 = imread("data/draft0Sur1_1.inr.gz")
        diff = len(img1[np.abs(t1 - img1)!= 0])
        assert float(diff)/(reduce(lambda x,y:x*y,img1.shape)) < 0.01
        #Segmented image
        t2 =imread("data/draftSeg0Sur1_1.inr.gz")
        diff2 = len(img2[np.abs(t2 - img2)!= 0])
        assert float(diff2)/(reduce(lambda x,y:x*y,img2.shape)) < 0.01
