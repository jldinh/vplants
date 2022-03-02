from pickle import load
from openalea.vmanalysis import delaunay3D

cell_cent = load(open("cell centers.pkl",'rb') )

cell_centers = []
cell_seg_id = {} #used later to retrieve
                 #the original id of cells
for cid,vec in cell_cent.iteritems() :
	cell_seg_id[len(cell_centers)] = cid
	cell_centers.append(vec)

mesh,pos = delaunay3D(cell_centers)
