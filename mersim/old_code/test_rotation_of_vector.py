#!/usr/bin/env python
import visual
import math



axisn = visual.norm( visual.vector( 1,0.2,0) )
curent_axisn = visual.norm( visual.vector( 0,1,0.5) )
steps = 180
mindist = 1000000000000
minteta = 0
for z in range( steps ):
    teta=float(z)/steps*2*math.pi
    dist = visual.mag(visual.rotate( curent_axisn, teta, visual.cross( axisn, curent_axisn) ) - axisn)
    if dist < mindist:
        minteta = teta

print minteta
visual.arrow(axis=axisn)
visual.arrow(axis=curent_axisn)
visual.arrow(axis=visual.rotate( curent_axisn, minteta, visual.cross( axisn, curent_axisn)), color=(1,0,0) )