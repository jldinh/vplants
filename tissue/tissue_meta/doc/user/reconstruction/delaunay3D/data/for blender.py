######################################
#
print "read infos"
#
######################################
from pickle import load

vtx = load(open("vertices.pkl",'rb') )
vtx = dict(enumerate(vtx) )

cent = load(open("cell centers.all.pkl",'rb') )

######################################
#
print "transform"
#
######################################
from openalea.tissueshape import tovec

vtx = tovec(vtx)
cent = tovec(cent)

bary = reduce(lambda x,y : x + y,vtx.itervalues() ) / len(vtx)

scaling = 0.1

bldvtx = dict( (pid, (vec - bary) * scaling) for pid,vec in vtx.iteritems() )
bldcent = dict( (pid, (vec - bary) * scaling) for pid,vec in cent.iteritems() )
######################################
#
print "write infos"
#
######################################
from pickle import dump

dump(bldvtx,open("bldvtx.pkl",'w') )
dump(bldcent,open("bldcent.pkl",'w') )
dump( (tuple(bary),scaling),open("bldtransform.pkl",'w') )

