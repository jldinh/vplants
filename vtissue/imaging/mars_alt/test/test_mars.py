from vtissuedata import get_shared_data
from openalea.image.all import imread, display, point_selection, pts2transfo

# Use to test if the two matrices are equals
epsilon=1e-10

im1 = imread(get_shared_data("plantB-1.lsm"))
im2 = imread(get_shared_data("plantB-2.lsm"))
im3 = imread(get_shared_data("plantB-3.lsm"))

from PyQt4 import QtGui
app = QtGui.QApplication([])

from vplants.mars_alt.mars.reconstruction import im2surface, surface2im

surf1,alt1 = im2surface(im1)
surf2,alt2 = im2surface(im2)

import numpy as np

pts1=np.loadtxt(get_shared_data("pts12-1.txt"))
pts2=np.loadtxt(get_shared_data("pts12-2.txt"))

pts1_3D = np.loadtxt(get_shared_data("pts1_3D.txt"))
pts2_3D = np.loadtxt(get_shared_data("pts2_3D.txt"))

def test_read_images():
    w1 = display(im1)
    w2 = display(im2)
    w3 = display(im3)

def test_im2surface():
    assert surf1.shape == (460, 460, 1)
    assert alt1.shape == (460, 460, 1)
    assert surf1.max() == 255
    assert surf1.min() == 0
    assert alt1.max() == 48
    assert alt1.min() == 0

def test_surface2im():
    points1 = surface2im(pts1,alt1)
    points1 = np.array(points1)
    vx1,vy1,vz1 = im1.resolution
    points1[:,0] /= vx1
    points1[:,1] /= vy1
    points1[:,2] /= vz1
    assert (np.round(points1) == np.round(pts1_3D)).all()

    points2 = surface2im(pts2,alt2)
    points2 = np.array(points2)
    vx2,vy2,vz2 = im2.resolution
    points2[:,0] /= vx2
    points2[:,1] /= vy2
    points2[:,2] /= vz2
    assert (np.round(points2) == np.round(pts2_3D)).all()

def test_open_point_selection():
    ps1 = point_selection(im1)
    ps2 = point_selection(im2)

def test_point_selection_with_surface():
    ps1 = point_selection(surf1)
    ps2 = point_selection(surf2)

    ps1.set_points(pts1)
    ps2.set_points(pts2)

def test_user_registration():
    pts1_3D = surface2im(pts1,alt1)
    pts2_3D = surface2im(pts2,alt2)
    Tr12 = pts2transfo(pts1_3D,pts2_3D)
    T = np.loadtxt(get_shared_data("Tr12.txt"))
    assert (np.abs(Tr12-T)<epsilon).all()
