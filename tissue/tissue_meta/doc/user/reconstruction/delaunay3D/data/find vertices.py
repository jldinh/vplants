######################################
#
print "read segmented image"
#
######################################
from openalea.vmanalysis import read_inrimage

im,info = read_inrimage("segmentation_partial_p60D2.inr.gz")

######################################
#
print "find cell pts"
#
######################################
import sys

vtx = []

imax,jmax,kmax = im.shape

print im.shape

for k in xrange(kmax - 1) :
	print k,
	sys.stdout.flush()
	for i in xrange(imax - 1) :
		for j in xrange(jmax - 1) :
			cols = set(im[i + di,j + dj,k + dk] \
			           for di,dj,dk in [(0,0,0),
			                            (1,0,0),
			                            (-1,0,0),
			                            (0,1,0),
			                            (0,-1,0),
			                            (0,0,1),
			                            ] )
			if 1 in cols and len(cols) > 3 :
				vtx.append( (i,jmax - j,kmax - k) )

print ""
######################################
#
print "write vertices"
#
######################################
from pickle import dump

dump(vtx,open("vertices.pkl",'w') )


