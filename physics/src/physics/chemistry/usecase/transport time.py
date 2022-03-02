from random import random
from physics.shapes import grid_graph2D
from physics.chemistry import Transport
import profile
from time import time

g,pos=grid_graph2D( (100,100) )
vV=dict( (vid,0.1) for vid in g.vertices() )
eP=dict( (eid,random()*0.01) for eid in g.edges() )
dt=1.

substance={}
algo=Transport(g,vV,eP,{0:0.9,99:0.},{})

def go () :
	algo.react(substance,dt)

print "initialised"
tinit=time()
profile.run("go()")
print time()-tinit

