from random import random,sample
from time import time
from openalea.physics.chemistry import Reaction

volume=dict( (pid,1.) for pid in xrange(1000) )
substance=dict( (pid,random()) for pid in volume )
actor=Reaction(dict( (pid,random()) for pid in sample(volume.keys(),900) ),
				dict( (pid,random()) for pid in sample(volume.keys(),950) ))

def bound () :
	substance[0]=0.

tinit=time()
for i in xrange(10) :
	for i in xrange(100) :
		actor.react(substance,0.1)
		bound()
	print substance[0],substance[1]
print "time",time()-tinit

print actor._creation[1]/actor._decay[1]
