from visual import *

from random import uniform
from math import *

#a = convex(color=(0.5,0,0))






z=[]
for i in range( 0, 5000, 6 ):
    v1 = vector( 0+i,2,0.1)
    v2 = vector( 2+i,4,0.2)
    v3 = vector( 4+i,4,0.4)
    v4 = vector( 6+i,2,0.2)
    v5 = vector( 4+i,0,0.1)
    v6 = vector( 2+i,0,0.5)
    l = [v1,v2,v3,v4,v5,v6]
    z.append( l )

#for i in l:
#    a.pos += i

#a= convex(pos=l, color=(0.5,1,0))
f = []
f2 = []
for l in z:
    for i in range( 1, len( l )-1 ):
        f.append( faces( pos=[l[ 0 ], l[i], l[ i+1 ] ] ) )
        f2.append( faces( pos=[l[ 0 ], l[ i+1 ], l[ i ] ] ) )
        #print 0, i, i+1, [l[ 0 ], l[ i+1 ], l[ i ] ]

x = 0
v = vector()
while True:
    x += 0.01
    v.y = 0.2*cos( x )
    for ff in f:
        ff.pos[ 0 ] += v 
