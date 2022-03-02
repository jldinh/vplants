"""
This module develops the organization of the WUS expression zone according the 
repressor model proposed by Jonsson et al.   
"""

#===============================================================================
# 
print "open tissue"
#
#===============================================================================
from openalea.celltissue import topen
from openalea.tissueshape import tovec,centroid,edge_length,face_surface_3D,cell_volume
from vplants.plantgl.math import norm

tissuename = "tissue_grid.zip"
f = topen(tissuename,'r')
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
# 
print "Tissue, %s, opened, initializations..."%tissuename
#
#===============================================================================
import numpy as np

CellNumber = g.nb_vertices() # Number of cells in the tissue
CellCenter = dict( (cid,centroid(mesh,pos,3,cid)) for cid in g.vertices() ) 
# CellCenter is a dictionary whose keys are cids, cell ids, and corresponding values are cell centers.  
CellVolume = dict((cid,float(cell_volume(mesh,pos,cid))) for cid in g.vertices() )
# CellCenter is a dictionary whose keys are cids, cell ids, and corresponding values are cell cell volumes.
FaceSurface = dict(( eid, face_surface_3D(mesh,pos,eid)) for eid in g.edges() ) #A_ij
# FaceSurface is a dictionary whose keys are edge ids, eid, and values are corresponding surfaces
CenterDistanceEdge = dict((eid, norm(CellCenter[g.source(eid)] - CellCenter[g.target(eid)])) for eid in g.edges())  # d_ij
A_over_d = dict( (eid, float(FaceSurface[eid])/float(CenterDistanceEdge[eid])) for eid in g.edges())


def make_dict_node_edge():
    """
    Returns a dictionary of cids as keys. The corresponding value for each key, is a dictionary of its corresponding eids. 
    """
    NodeEdgeDict = dict()
    for cid in g.vertices():
        SmallDict = dict()
        for eid in g.edges(cid):
            SmallDict.setdefault(eid)        
        NodeEdgeDict.setdefault(cid, SmallDict)
    return NodeEdgeDict

NodeEdgeDict = make_dict_node_edge()

def index_2_ID():
    """
    Returns a numpy array of cids. 
    """
    ind = 0    
    Ind2ID = np.zeros(CellNumber, dtype=int)
    for cid in g.vertices():
        Ind2ID[ind] = cid
        ind += 1    
    return Ind2ID

def index2ID_dict():
    """
    Returns a dictionary whose keys are numbers from 0 to CellNumber and the corresponding value is a cell id.  
    """
    ind = 0    
    Ind2ID = dict()
    for cid in g.vertices():
        Ind2ID.setdefault(ind, cid)
        ind += 1    
    return Ind2ID

Ind2ID = index2ID_dict()

def ID_2_index_dict(Dict):
    """
    Returns a dictionary whose keys are cell ids and the corresponding values are numbers from 0 to CellNumber.
    """
    counter = 0
    D = dict()
    Len = len(Dict)
    while counter < Len:
        D.setdefault(Dict[counter],counter)
        counter += 1
    return D        

ID2IndDict = ID_2_index_dict(Ind2ID)

def BottomCids():
    """
    returns a set of cids situated in the border of meristem and the stem.
    """    
    bottom_cids = set()
    external_fids = [fid for fid in mesh.wisps(2) if mesh.nb_regions(2,fid) == 1]
    external_cids = set()
    for fid in external_fids :
        external_cids.update( mesh.regions(2,fid) )
    #mesh.wisp(2): les surfaces     mesh.wisp(3): les cellules
    bottom_cids = external_cids - set(L1)
    return bottom_cids

bottom_cids = BottomCids()


pruned_bottom_cids = []
for cid in bottom_cids:    
    if (CellCenter[cid][1]>-22 and CellCenter[cid][0]<27 ) or (0 <CellCenter[cid][0] < 27 and CellCenter[cid][1] < -22):
        pruned_bottom_cids.append(cid)

pruned_bottom_cids_2 = dict()
for cid in bottom_cids:
    if cid not in pruned_bottom_cids:
        pruned_bottom_cids_2.setdefault(cid)

TestCells=dict()
for cid in NodeEdgeDict:
    if (CellCenter[cid][2]<-39):
        TestCells.setdefault(cid)

def List_2_dict_test():
    CidDict=dict()
    for cid in g.vertices():
        if cid in L1:
            CidDict.setdefault(cid,"L1")
        elif cid in TestCells:
            CidDict.setdefault(cid,"T")
        elif cid in bottom_cids:
            CidDict.setdefault(cid,"Tt")
        else:
            CidDict.setdefault(cid,None)        
    return CidDict

CellTypeDict = List_2_dict_test()
        
EdgeSourceDict = dict((eid, ID2IndDict[g.source(eid)]) for eid in g.edges())
EdgeTargetDict = dict((eid, ID2IndDict[g.target(eid)]) for eid in g.edges())

#===============================================================================
#
print "initialized"
#
#===============================================================================


#===============================================================================
#
print "Modeling"
#
#===============================================================================
import cPickle
from math import sqrt

VarNumber = 3

def G(x):
    return (1.0 + (x / ( sqrt( 1.0+x*x ) ) ) ) / 2.0

k_y2, d_y2, D_y2 = .1, 0.0008, 0.31
k_y1, d_y1, D_y1 = 0.1, 0.0038, 0.025
T_w, d_w, h_w, T_wy = 10.0, 0.1, 2.0 ,-10.0

k_y2, d_y2, D_y2 = .1, 0.002, 0.052
#k_y1, d_y1, D_y1 = 0.14, 0.0077, 0.01
k_y1, d_y1, D_y1 = 0.1, 0.008, 0.009
T_w, d_w, h_w, T_wy = 10.0, 0.1, 2.0 ,-10.0

#check_cell = ID2IndDict[63402] + CellNumber
LenX = VarNumber * CellNumber

def Xdot(t, X):
       
    dX = np.zeros(LenX)
    dY1 = dX[:CellNumber]    
    Y1 = X[:CellNumber]        
    dY2 = dX[CellNumber: 2*CellNumber]    
    Y2 = X[CellNumber: 2*CellNumber]
    W = X[2*CellNumber:]
    dW = dX[2*CellNumber:]
    
#    print t, X[check_cell]
    print t
   
    for IndexCounter in xrange(CellNumber): 
        cid = Ind2ID[IndexCounter]        
        CellType = CellTypeDict[cid]
        DeltaY1 = 0.0
        DeltaY2 = 0.0
        if CellType == "L1":
            DeltaY1 = k_y1
        elif CellType == "T" or CellType == "Tt": #Atteion: first it was if
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
                       
#        DeltaY1 += DiffusionY1 - Y_1 * d_y1
#        DeltaY2 += DiffusionY2 - Y_2 * d_y2
        
        dY1[IndexCounter] = DeltaY1 + D_y1 * DiffusionY1 - Y_1 * d_y1
        dY2[IndexCounter] = DeltaY2 + D_y2 * DiffusionY2 - Y_2 * d_y2
        
        #dW[IndexCounter]=(1.0/T_w)*G(h_w+T_wy*(Y1[IndexCounter]+ Y2[IndexCounter]))-d_w*W[IndexCounter]       
        dW[IndexCounter] = (1.0/T_w)*G(h_w+T_wy*(Y_1 + Y_2))-d_w*W[IndexCounter]
          
    return dX

#===============================================================================
# Scipy ODE Solver
#===============================================================================
import time
import numpy.matlib
from scipy.integrate import ode

t1 = time.time()

IntermedaiteSolutionNumber = 100
TimeLimit = 1000.
Y0 = np.zeros(LenX)
t0 = 0
dt = .1
WhenSave = ((TimeLimit - t0)/dt)/IntermedaiteSolutionNumber

r = ode(Xdot)
ResultFile = numpy.matlib.zeros((IntermedaiteSolutionNumber+2, LenX), float)
ResultFile[0:] = Y0

r.set_initial_value(Y0, t0)
counter1 = 1
counter2 = 1 
while r.successful() and r.t < TimeLimit:
    r.integrate(r.t+dt)
    counter1 += 1
    if counter1 % WhenSave == 0:
#        rx = r.y
#        for i in xrange(LenX):
#            ResultFile[counter2, i] = r.y[i]
        ResultFile[counter2, :] = r.y[:]
        counter2 += 1
    
Result = r.y
ResultFile[-1:] = Result


t2 = time.time()
print "elapsed time for resolving the odes:", t2-t1



#===============================================================================
# 
print "Modeling finished."
#
#===============================================================================

def cell_vector():
    CellVector=dict((cid,0) for cid in g.vertices())
    return CellVector

factY = cell_vector()

for cid in g.vertices():
#        factY[cid]=Result[-1, ID2IndDict[cid] + 2*CellNumber]
        factY[cid]=ResultFile[-1,ID2IndDict[cid] + 2*CellNumber]
        #print factY[cid]


def write_2_file():
    f=open("WUSallnov.txt","w")
#    for i in xrange(len(Result)):
    for i in xrange(IntermedaiteSolutionNumber + 2):
#        if i%10==0:
        cPickle.dump(ResultFile[i,:],f)
    f.close()
            
#write_2_file()


#===============================================================================
# 
print "draw"
#
#===============================================================================
from vplants.plantgl.scenegraph import Shape,Material,Translated,Scaled
from vplants.plantgl.ext.color import JetMap
from openalea.pglviewer import SceneView
from openalea.tissueshape import centroid
from openalea.tissueview import cell_geom,ScalarPropView

cmap = JetMap(0.,1.,outside_values = True)
sc = ScalarPropView(mesh,pos,3,factY,10,cmap)
sc.redraw()

#===============================================================================
# sc = SceneView()
# 
# baryDict= dict((cid,centroid(mesh,pos,3,cid)) for cid in g.vertices())
# geomDict = dict((cid, cell_geom(mesh,pos,cid)) for cid in g.vertices())
# 
# for cid in mesh.wisps(3) :
#    geom = geomDict[cid]
#    geom.indexList = [(tup[0],tup[2],tup[1]) for tup in geom.indexList]
#    #bary = centroid(mesh,pos,3,cid)
#    sgeom = Translated(baryDict[cid], Scaled( (0.9,0.9,0.9),Translated(-baryDict[cid],geom) ) )
#    col = cmap(factY[cid])
#    mat = Material(col.i3tuple())
#    shp = Shape(sgeom,mat)
#    sc.add(shp)
#===============================================================================

###################################
#
print "display"
#
####################################
from openalea.pglviewer import QApplication,Viewer,Vec,Quaternion
from openalea.pglviewer import ClippingProbeView,ClippingProbeGUI

bb = sc.bounding_box()

pb = ClippingProbeView(sc,size = max(bb.getSize()) )
pb.set_visible(False)

qapp = QApplication([])
v = Viewer()
cam=v.view().camera()
cam.setPosition(Vec(102.063,-43.2236,41.9204))
cam.setOrientation(Quaternion(0.448465,0.349287,0.400549,0.718637))
pb.setPosition(Vec(1.10563,2.11675,-2.0438))
pb.setOrientation(Quaternion(-0.0259682,0.658813,-0.00453761,0.751845))
v.set_world(pb)
pb.activate(v.view(),True)

v.add_gui(ClippingProbeGUI(pb) )

v.show()
v.view().show_entire_world()
qapp.exec_()
