from openalea.image.all import imread, display, write_inrimage
import numpy as np
from scipy.ndimage import morphology
from openalea.image.algo.morpho import skiz
from vplants.mars_alt.alt.deformation_field import deformation_field
from vplants.mars_alt.alt.mapping import lineage_from_file

def simple_image(shape=(100,100,100)):
    return np.ones(shape)

def simple_points(shape=(100,100,100)):
    ax, bx = int(24/100.*shape[0]), int(74/100.*shape[0])
    ay, by = int(24/100.*shape[1]), int(74/100.*shape[1])
    az, bz = int(24/100.*shape[2]), int(74/100.*shape[2])
    pts = [(x,y,z) for x in (ax,bx) for y in (ay,by) for z in (az,bz)]
    return pts

def random_points(size=20, shape=(100,100,100)):
    X,Y,Z = shape
    N = X*Y*Z
    pts = np.random.random_integers(0,N,size)

    ' i =x + y*X + z*X*Y'
    z = pts / (X*Y)
    y = (pts-(z*X*Y))/Y
    x = pts - z*X*Y - y*Y
    return zip(x,y,z)

def test_skiz1():
    ''' Simple test of the skiz algorithm . '''
    img = simple_image()
    pts = simple_points()

    mask = skiz(img, pts)
    assert mask.max() == len(pts)
    assert mask.min() == 1

def test_skiz2():
    ''' Simple test of the skiz algorithm . '''
    img = simple_image()
    pts = random_points()

    mask = skiz(img, pts)
    assert mask.max() == len(pts)
    assert mask.min() == 1

def test_skiz_final():

    pts1  = np.loadtxt('data/points1_skiz.set')
    pts2  = np.loadtxt('data/points2_skiz.set')
    image = imread('data/imgBeforeSkiz.inr.gz')

    pts1 /= image.resolution
    pts2 /= image.resolution

    img1 = skiz(image, pts2)

    image_res = imread('data/tabSkiz.inr.gz')

    assert len( np.abs(image_res - img1)!= 0) < 1200
    return img1

def test_skiz_final_vector():

    #return
    im0      = imread("data/seg_1_ok.inr.gz")
    im1      = imread("data/seg_2_ok.inr.gz")
    mapping  = lineage_from_file("data/map_dict.py")

    assert len(mapping) == 443
    assert im0.max() == 444
    vector_field = deformation_field(im0, im1, None, mapping, 5.)
    write_inrimage('test_field.inr.gz', vector_field)
    return vector_field

def view_vector_field(vectors, mask=30):
    from enthought.mayavi.mlab import quiver3d
    u = vectors[:,:,:,0]
    v = vectors[:,:,:,1]
    w = vectors[:,:,:,2]
    obj = quiver3d(u, v, w, mask_points=mask)

def init_vector():
    pts1 = np.loadtxt('data/points1_skiz.set')
    pts2 = np.loadtxt('data/points2_skiz.set')
    image = imread('data/imgBeforeSkiz.inr.gz')

    pts1 /= image.resolution
    pts2 /= image.resolution

    vector_img = np.zeros(shape=image.shape+(3,))
    vectors = pts1-pts2
    for i, (x,y,z) in enumerate(pts2):
        vector_img[x,y,z] = vectors[i]

    return vector_img
"""
def skiz(image, points):

    shape = image.shape
    img = np.ones(shape=shape)
    label = np.zeros(shape=shape, dtype=np.int)
    for i, (x,y,z) in enumerate(points):
        img[x,y,z] = 0
        label[x,y,z] = i+1

    ix, iy, iz=morphology.distance_transform_bf(img, metric='euclidean',
                    return_distances=False, return_indices=True)
    return label[ix, iy, iz]
"""
