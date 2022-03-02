from random import random
from physics.shapes import grid_graph2D
from physics.chemistry import Reaction
import profile
from time import time

g,pos=grid_graph2D( (100,100) )
creation=dict( (vid,0.01) for vid in g.vertices() )
decay=dict( (vid,0.01+random()/10.) for vid in g.vertices() )

dt=1.

substance=dict( (vid,0.) for vid in g.vertices() )
algo=Reaction(creation,decay)

def go () :
	algo.react(substance,dt)

print "initialised"
tinit=time()
profile.run("go()")
print time()-tinit

