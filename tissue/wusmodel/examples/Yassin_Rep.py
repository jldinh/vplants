import numpy as np
import cPickle
from math import sqrt
from scipy.integrate import ode
import numpy.matlib


#===============================================================================
# 
print "open tissue"
#
#===============================================================================
from openalea.celltissue import topen
from openalea.tissueshape import tovec,centroid,edge_length,face_surface_3D,cell_volume
from vplants.plantgl.math import norm

tissueName = "yassin_grid.zip"
f = topen(tissueName,'r')
t,d = f.read()
cfg = f.read_config("config")
pos,d = f.read("position")
L1,d = f.read("pattern_L1")
#L2,d = f.read("pattern_L2")
STEM,d = f.read("pattern_STEM")
#WUS,d = f.read("pattern_WUS")
f.close()
pos = tovec(pos)
g = t.relation(cfg.cc_graph)
mesh = t.relation(cfg.mesh_id)

#===============================================================================
# print finished
#===============================================================================


class Parameters:
    """
    Parameters class is just a data structure for parameters.
    """
    k_y2 = 0.1
    d_y2 = 0.002
    D_y2 = 0.052
    k_y1 = 0.1
    d_y1 = 0.008
    D_y1 = 0.009
    T_w = 10.0
    d_w = 0.1
    h_w = 2.0
    T_wy = -10.0
    

def initialize(graph, mesh):
    
    CellNumber = graph.nb_vertices() # Number of cells in the tissue
    CellCenter = dict( (cid,centroid(mesh,pos,3,cid)) for cid in graph.vertices() ) 
    # CellCenter is a dictionary whose keys are cids, cell ids, and corresponding values are cell centers.  
    CellVolume = dict((cid,float(cell_volume(mesh,pos,cid))) for cid in graph.vertices() )
    # CellCenter is a dictionary whose keys are cids, cell ids, and corresponding values are cell cell volumes.
    FaceSurface = dict(( eid, face_surface_3D(mesh,pos,eid)) for eid in graph.edges() ) #A_ij
    # FaceSurface is a dictionary whose keys are edge ids, eid, and values are corresponding surfaces
    CenterDistanceEdge = dict((eid, norm(CellCenter[graph.source(eid)] - CellCenter[graph.target(eid)])) for eid in graph.edges())  # d_ij
    A_over_d = dict( (eid, float(FaceSurface[eid])/float(CenterDistanceEdge[eid])) for eid in graph.edges())
    
    NodeEdgeDict = dict() #a dictionary of cids as keys. The corresponding value for each key, is a dictionary of its corresponding eids. 
    for cid in graph.vertices():
        SmallDict = dict()
        for eid in graph.edges(cid):
            SmallDict.setdefault(eid)        
        NodeEdgeDict.setdefault(cid, SmallDict)
    
    ind = 0    
    Ind2ID = dict() # a dictionary whose keys are numbers from 0 to CellNumber and the corresponding value is a cell id.
    for cid in g.vertices():
        Ind2ID.setdefault(ind, cid)
        ind += 1    

    counter = 0
    ID2IndDict = dict() # a dictionary whose keys are cell ids and the corresponding values are numbers from 0 to CellNumber.
    Len = len(Ind2ID)
    while counter < Len:
        ID2IndDict.setdefault(Ind2ID[counter], counter)
        counter += 1

    EdgeSourceDict = dict((eid, ID2IndDict[g.source(eid)]) for eid in g.edges())

    EdgeTargetDict = dict((eid, ID2IndDict[g.target(eid)]) for eid in g.edges())  
    
    return CellNumber, CellCenter, CellVolume, FaceSurface, CenterDistanceEdge, A_over_d, NodeEdgeDict, Ind2ID, ID2IndDict, EdgeSourceDict, EdgeTargetDict 

    
def G(x):
    return (1.0 + (x / ( sqrt( 1.0 + x * x ) ) ) ) / 2.0

def RepModel(dt, dtInternal, graph, mesh, L1, Stem):
    
    def Xdot(t, X):
        print t
        dX = np.zeros(LenX)
        dY1 = dX[:CellNumber]    
        Y1 = X[:CellNumber]        
        dY2 = dX[CellNumber: 2*CellNumber]    
        Y2 = X[CellNumber: 2*CellNumber]
        W = X[2*CellNumber:]
        dW = dX[2*CellNumber:]
        
        for IndexCounter in xrange(CellNumber): 
            cid = Ind2ID[IndexCounter]        
#            CellType = CellTypeDict[cid]
            DeltaY1 = 0.0
            DeltaY2 = 0.0
            if cid in L1: #CellType == "L1":
                DeltaY1 = k_y1
            elif cid in Stem: #CellType == "T" or CellType == "Tt": #Atteion: first it was if
                DeltaY2 = k_y2
            DiffusionY1 = 0
            DiffusionY2 = 0
            Volume = CellVolume[cid]
            Y_1 = Y1[IndexCounter]
            Y_2 = Y2[IndexCounter]
            for eid in NodeEdgeDict[cid]:
                if EdgeSourceDict[eid] == IndexCounter:
                    nInd = EdgeTargetDict[eid]                
                else:
                    nInd = EdgeSourceDict[eid]
                A_sur_d = A_over_d[eid]
                DiffusionY1 +=  ( A_sur_d / Volume ) * ( Y1[nInd] - Y_1)
                DiffusionY2 +=  ( A_sur_d / Volume ) * ( Y2[nInd] - Y_2)
                           
            dY1[IndexCounter] = DeltaY1 + D_y1 * DiffusionY1 - Y_1 * d_y1
            dY2[IndexCounter] = DeltaY2 + D_y2 * DiffusionY2 - Y_2 * d_y2
            dW[IndexCounter] = (1.0/T_w)*G(h_w+T_wy*(Y_1 + Y_2))-d_w*W[IndexCounter]
              
        return dX
    
    CellNumber, CellCenter, CellVolume, FaceSurface, CenterDistanceEdge, A_over_d, NodeEdgeDict, Ind2ID, ID2IndDict, EdgeSourceDict, EdgeTargetDict = initialize(graph, mesh)
    
    k_y2, d_y2, D_y2, k_y1, d_y1, D_y1, T_w, d_w, h_w, T_wy = Parameters.k_y2, Parameters.d_y2, Parameters.D_y2, Parameters.k_y1, Parameters.d_y1, Parameters.D_y1,    Parameters.T_w, Parameters.d_w, Parameters.h_w, Parameters.T_wy 
    

    VarNumber = 3
    LenX = VarNumber * CellNumber

    Y0 = np.zeros(LenX)
    t0 = 0
    dtInternal = .1
    r = ode(Xdot)
    r.set_initial_value(Y0, t0)

    while r.successful() and r.t < dt:
        r.integrate(r.t + dtInternal)
    Result = r.y
    
    return Result # in fact we have to update the tissue


if __name__ == "__main__":
    import time
    t1 = time.time()
    RepModel(1000, 0.1, g, mesh,  L1, STEM)
    print "Elapsed time is: ", time.time() - t1
    
    

    
    