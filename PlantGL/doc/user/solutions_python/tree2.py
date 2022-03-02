from openalea.plantgl.all import *
from math import cos
from math import sin
from math import pi
from math import sqrt

# a function to make a  textured cylinder 
# with quads as primitives
def quad_cyl(radius, height, slices = 12):
    """ quad_cyl(radius, height) makes a textured cylinder with quads as primitives """
    points = []
    indices = []
    texCoords = []
    for i in range(slices):
        points += [(radius*cos(2*i*pi/slices),radius*sin(2*i*pi/slices), 0),
                   (radius*cos(2*i*pi/slices),radius*sin(2*i*pi/slices), height)]
        texCoords += [(i*1./slices,0),(i*1./slices,1)]
        if i is not (slices -1):
           indices += [(2*i,2*i+1,2*i+3,2*i+2)]
        else:
           #texCoordsIndices = indices + [(2*i,2*i+1,2*i+3,2*i+2)]
           indices += [(2*i,2*i+1,1,0)]
    texCoords += [(1,0),(0,0)]
    cyl = QuadSet(points,indices)
    cyl.texCoordList = texCoords
    cyl.texCoordIndexList = indices #texCoordsIndices
    return cyl

def tree2():
    
    # We compute the trunk of the tree with an extruded circle
    cyl = quad_cyl(1.0,6,50)
    tex = ImageTexture("./textures/wood_texture.png")
    trunk = Shape(cyl,tex)
    
    # Now we compute a leaf. We will use a transparent texture over a square
    points = [(0,-0.6,-0.6),
              (0,0.6,-0.6),
              (0,0.6,0.6),
              (0,-0.6,0.6)]
    indices = [(0, 1, 2, 3)]
    square = QuadSet(points,indices)
    tex = ImageTexture("./textures/palm_leaf.png")
    texCoord = [(0,0),(0,1),(1,1),(1,0)]
    texCoordIndices = [(0,1,2,3)]
    square.texCoordList = texCoord
    square.texCoordIndexList = texCoordIndices
    square = EulerRotated(0,pi/2.,0,square)
    square = AxisRotated((1,0,0),pi/4., square)
    square = Translated(0,1.6,0.9,square)
    
    # scale factor
    sf = 0.9

    leaves = [Shape(Translated(0,1.-(sf*(4-i)),1.6*i,Scaled((sf*(4-i),sf*(4-i),sf*(4-i)),square)),tex) for i in range(4)]
    square = AxisRotated((0,0,1),pi,square)
    leaves += [Shape(Translated(0,-(1.-(sf*(4-i))),1.6*i,Scaled((sf*(4-i),sf*(4-i),sf*(4-i)),square)),tex) for i in range(4)]

    return leaves+[trunk]

scene = Scene(tree2())
Viewer.display(scene)
