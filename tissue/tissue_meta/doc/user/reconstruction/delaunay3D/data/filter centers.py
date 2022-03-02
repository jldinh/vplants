from pickle import load,dump
from openalea.vmanalysis import is_inside_mesh
from vplants.plantgl.scenegraph import TriangleSet

#read cell centers
cell_cent = load(open("cell centers.all.pkl",'rb') )

#read outer boundary mesh
pts,trs = load(open("../surface mesh.pkl",'rb') )
outer_boundary = TriangleSet(pts,trs)

cell_cent = dict( (cid,cell_cent[cid]) \
            for cid in is_inside_mesh(outer_boundary,cell_cent) )

dump(cell_cent,open("../cell centers.pkl",'w') )
