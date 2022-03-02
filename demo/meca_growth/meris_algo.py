from physics.math import zeros,X,Y
from celltissue.data.wisp_triangulation import WispTriangulation2D,FaceMap
from meca import MecaGrowth

class WispTriangulationNode(object):
    def __call__(self, *inputs) :
        return WispTriangulation2D(*inputs)

class Strain0Node(object):
    def __call__(self, *inputs) :
        wt,=inputs
        strain0=FaceMap(wt)
        for fid in wt.faces() :
            strain0[fid]=zeros( (2,2) )
        return (strain0,)

class FixedCellNode(object):
    def __call__(self, *inputs) :
        t,cid=inputs
        fixed=[]
        for pid in t.geometry(0,cid) :
            fixed.extend([(pid,X),(pid,Y)])
        return (fixed,)

class MecaGrowthNode(object):
    def __call__(self, *inputs):
        return MecaGrowth(*inputs)


