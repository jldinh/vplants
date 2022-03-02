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

cell_ptx = [0 for i in xrange(im.max() + 1)]
cell_pty = [0 for i in xrange(im.max() + 1)]
cell_ptz = [0 for i in xrange(im.max() + 1)]
cell_ptnb = [0 for i in xrange(im.max() + 1)]

imax,jmax,kmax = im.shape

print im.shape

for k in xrange(kmax) :
	print k,
	sys.stdout.flush()
	for i in xrange(imax) :
		for j in xrange(jmax) :
			cid = im[i,j,k]
			if cid > 1 :
				cell_ptx[cid] += i
				cell_pty[cid] += j
				cell_ptz[cid] += k
				cell_ptnb[cid] += 1

print ""
######################################
#
print "find cell centers"
#
######################################
cell_cent = dict( (i,(float(cell_ptx[i]) / nb,
                      float(cell_pty[i]) / nb,
                      float(cell_ptz[i]) / nb) ) \
                  for i,nb in enumerate(cell_ptnb) \
                  if nb > 2000)

cell_cent = dict( (cid,(v[0],jmax - v[1],kmax - v[2]) ) \
                  for cid,v in cell_cent.iteritems() )

cell_size = dict(enumerate(cell_ptnb) )
######################################
#
print "write cell centers"
#
######################################
from pickle import dump

dump(cell_cent,open("cell centers.all.pkl",'w') )
dump(cell_size,open("../cell size.all.pkl",'w') )

