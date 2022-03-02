#############################
#
print "compute delaunay"
#
#############################
execfile("delaunay_simple.py")

#############################
#
print "constrain delaunay"
#
#############################
execfile("delaunay_constrained.py")

#############################
#
print "filter delaunay"
#
#############################
execfile("delaunay_filtered.py")

#############################
#
print "compute voronoi"
#
#############################
execfile("voronoi_simple.py")

#############################
#
print "compute voronoi"
#
#############################
execfile("voronoi_projected.py")

#############################
#
print "write result"
#
#############################
from openalea.container import Quantity,write_topomesh

X = Quantity(dict( (pid,float(vec[0]) ) for pid,vec in pos.iteritems() ),
             "pix",
             "float",
             "x coordinate of points")

Y = Quantity(dict( (pid,float(vec[1]) ) for pid,vec in pos.iteritems() ),
             "pix",
             "float",
             "y coordinate of points")

Z = Quantity(dict( (pid,float(vec[2]) ) for pid,vec in pos.iteritems() ),
             "pix",
             "float",
             "z coordinate of points")

seg_id = Quantity(cell_seg_id,
                  "cid",
                  "int",
                  "id of cell in segmented image")

props = [[("X",X),("Y",Y),("Z",Z)],
         [],
         [],
         [("SEGID",seg_id)]]

write_topomesh("tissue.msh",
               mesh,
               "voronoi reconstruction",
               props)


