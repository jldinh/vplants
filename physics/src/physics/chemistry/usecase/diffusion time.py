from openalea.physics.shapes import grid_graph2D
from openalea.physics import GraphDiffusion,PropertyMap
import profile
from time import time

g,pos=grid_graph2D( (100,100) )
print "generated"
vV=PropertyMap()
for vid in g.vertices() :
	vV[vid]=0.01
eD=PropertyMap()
for eid in g.edges() :
	eD[eid]=0.1

fc=PropertyMap()
fc[0]=0.98
fc[g.nb_vertices()-1]=0.
ff=PropertyMap()
dt=1.

substance=PropertyMap()
for vid in g.vertices() :
	substance[vid]=0.

algo=GraphDiffusion(g,vV,eD,fc,ff)

def go () :
	for i in xrange(10) :
		algo.react(substance,dt)

print "initialised"
tinit=time()
profile.run("go()")
print time()-tinit

