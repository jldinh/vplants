#!/usr/bin/env python
"""tutorialDiscPhyllotaxisModel.py

Desc.

:version: 2006-12-19 15:21:06CEST
:author:  szymon stoma
"""

from visual import *
import math
import pylab as pl
import random

C_CENTER = vector(0,0,0)
C_CZONE=1#10
C_SPEED=0.1
C_PRIM_SIZE=3#13.16518#12.259#4.31358#math.sqrt(151)
C_DISCRETIZATION =200#500
C_SIZE_X = 20
C_SIZE_Y = 20
C_DZONE  = 6
C_VISUAL_ZONE_SIZE=0.1
C_PLANE_NORMAL=vector(0,0,1)
C_PRIM_TRASH=0

def p( p1, p2, r):
    d = r - mag(p1 - p2)
    if d < 0:
        return 0
    else:
        return 1

def pc( p1, p2, r):
    #print p1,p2,r
    d = r - mag(p1 - p2)
    if d < 0:
        return 0
    else:
        return 1 - mag(p1-p2)/r 
    
def m( p, c ):
    return norm( p-c )*speed( p )
    
def speed( p ):
    global C_CENTER
    return C_SPEED*mag(p-C_CENTER)*0.1
    #return C_SPEED*math.pow(mag(p-C_CENTER),2)*0.1
    #return C_SPEED

def prepare_scene():
    center = sphere(pos=vector(0,0,3), radius=0.1, color=(1,1,1))
    competence = ring( pos=vector(0,0,3), axis=vector(0,0,1), radius=C_CZONE, thickness=C_VISUAL_ZONE_SIZE)
    drop = ring( pos=vector(0,0,3), axis=vector(0,0,1), radius=C_DZONE, color=(1,0,0), thickness=C_VISUAL_ZONE_SIZE)

def competance_grid():
    l = []
    e = random.random()
    #e = 0
    for i in range(C_DISCRETIZATION):
        a = e+(float(i)/C_DISCRETIZATION)*2*math.pi
        x = C_CZONE*math.cos(a)
        y = C_CZONE*math.sin(a)
        l.append(vector(x,y,0))
    return l

    
def move_primodiums( prims ):
    for i in prims:
        prims[ i ] = prims[ i ] + m(prims[ i ], C_CENTER)
    return prims

def drop_primordiums( prims ):
    t = {}
    for i in prims:
        if p(prims[ i ], C_CENTER, C_DZONE) == 1:
            t[ i ] = prims[ i  ]
    return t

def search_new_primordiums( prims, cand ):
    appcand=[]
    for i in cand:
        in_range=False
        for j in prims:
            if p( i, prims[ j ], C_PRIM_SIZE) == 1:
                in_range=True
                break
        if not in_range:
            appcand.append( i )
    return appcand

def insert_new_primordiums( prims ):
    global current_prim
    global information
    cand = competance_grid()
    appcand = search_new_primordiums( prims, cand)
    while len(appcand):
        sort_prim_cand( prims=prims, prim_cand=appcand) 
        prims[ current_prim ] = appcand[ 0 ]
        information[ current_prim ] = appcand[ 0 ]
        current_prim=current_prim+1
        print_last_div()
        appcand = search_new_primordiums( prims=prims, cand=appcand)
    return prims

def print_last_div():
    global information
    global current_prim
    if current_prim > 1:
        zi = information[ current_prim-1 ]
        yi =information[ current_prim-2 ]
        yi.z = 0
        zi.z = 0
        print yi.diff_angle(zi)*360/(2*math.pi) 

def sort_prim_cand( prims=None, prim_cand=None):
    if len( prim_cand ) < 2:
        return prim_cand
    print "sorting..", len( prim_cand )
    pp = prims
    
    ds = {}        
    for i in prim_cand:
        z=0
        for j in pp:
            z += math.pow( mag( pp[ j ] - i ),2 )
        ds[ i ] = z
    prim_cand.sort( lambda x, y: cmp( ds[ y ],  ds[ x ] ))
    #for i in prim_cand:
    #    print  i ,ds[ i ]   
    #return prim_cand    

def visualise_prims( prims, vis ):
    nv=[]
    for i in vis:
        i.visible=False
    for i in prims:
        nv.append( cylinder(pos=prims[ i ], axis=vector(0,0,1),radius=C_PRIM_SIZE, length=0.001+0.01*(C_DZONE-mag(C_CENTER-prims[ i ])), color=(0.,0.5,0)))
        nv.append( ring(pos=prims[ i ], axis=vector(0,0,1),radius=C_PRIM_SIZE, thickness=0.01+0.04*(C_DZONE-mag(C_CENTER-prims[ i ])), color=(0.,0.8,0)))
        nv.append( cylinder(pos=prims[ i ], axis=vector(0,0,1),radius=float(C_PRIM_SIZE)/15, length=50, color=(0.5,0.0,0)))
        #nv.append(  )
    #raw_input()
    return nv

def visualise_primordium_information( ):
    global information
    p = information
    pln = len( p )
    x = range( 1, pln )
    y = []
    for i in range( 1, pln ):
        yi = p[ i ] 
        zi = p[ i-1 ]
        yi.z = 0
        zi.z = 0
        y.append( yi.diff_angle(zi)*360/(2*math.pi) )
    pl.plot( x, y )
    pl.show()

def visualise_primordium_abs_angle( ):
    global information
    p = information
    pln = len( p )
    x = range( 1, pln )
    y = []
    zi = vector(1,0,0)
    for i in range( 1, pln ):
        yi = p[ i ] 
        yi.z = 0
        y.append( yi.diff_angle(zi)*360/(2*math.pi) )
    pl.plot( x, y )
    pl.show()

def mainloop():
    global primordiums
    global vis
    while True:
        display.autocenter=0
        display.autoscale=0
        vis = visualise_prims( prims=primordiums, vis=vis )
        primordiums = move_primodiums(primordiums)
        primordiums = drop_primordiums(primordiums)
        primordiums = insert_new_primordiums( primordiums )
        
current_prim=2
primordiums={}
vis=[]
point2mesh_id={}
display.autocenter=0
display.autoscale=0
information={}
r = vector(random.random(), random.random(),0)
r=vector(-8, 0, 0)
primordiums[ 0 ] = r
information[ 0 ] = r
r = vector(-random.random(), -random.random(),0)
r = vector(math.cos(math.radians(42.49))*C_CZONE,C_CZONE*math.sin(math.radians(42.49)),0)
primordiums[ 1 ] = r
information[ 1 ] = r
prepare_scene()
mainloop()