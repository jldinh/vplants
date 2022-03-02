from openalea.image.all import imread, display
from vplants.mars_alt.all import original_fusion

import numpy as np

im1 = imread("../share/plantB-data/temp/imgReech1.inr.gz")
im2 = imread("../share/plantB-data/temp/imgReech2.inr.gz")
im3 = imread("../share/plantB-data/temp/imgReech3.inr.gz")

mat2=np.loadtxt("../share/plantB-data/temp/mat2.txt")
mat3=np.loadtxt("../share/plantB-data/temp/mat3.txt")

def1 = imread("../share/plantB-data/temp/champ_1.inr.gz")
def2 = imread("../share/plantB-data/temp/champ_2.inr.gz")
def3 = imread("../share/plantB-data/temp/champ_3.inr.gz")


from PyQt4 import QtGui
app = QtGui.QApplication([])

def test_fusion():
    fused_im = original_fusion(im1,def1,[im2,im3],[mat2,mat3],[def2,def3])
    assert fused_im.shape == (460, 460, 320)
    assert fused_im.max() == 255
    assert fused_im.min() == 0
