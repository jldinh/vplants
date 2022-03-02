#!/usr/bin/env python
"""tutorialInhibitorFieldDiscModel.py

Desc.

:version: 2006-12-27 15:21:06CEST
:author:  szymon stoma
"""


from visual import *
import math
import pylab as pl
import random
import pickle
#import psyco

import copy_reg
def dump_visual_vector( v ):
    return (vector, ( v.x,v.y,v.z ) )
copy_reg.pickle(vector, dump_visual_vector)

#C_CENTER = vector(0,0,0)
#C_CZONE=1#10
#C_SPEED=0.1
#C_DISCRETIZATION =360#0
#C_SIZE_X = 20
#C_SIZE_Y = 20
#C_VISUAL_ZONE_SIZE=0.01
#C_PLANE_NORMAL=vector(0,0,1)
#
#C_PRIM_STIFFNESS=14
#C_PRIM_TRASH=5
#C_PRIM_SIZE=  2.1#19.99#przytymwzaleznosci od predkosci14.2#13.16518#12.259#4.31358#math.sqrt(151)
##: these values are used to determine the inhibition function 
#
#C_INITIALTIMESTEP = 0.01
#C_DZONE  = 20*C_CZONE
#C_V0 = 1.
#
#
#def p( p1, p2, r):
#    d = r - mag(p1 - p2)
#    if d < 0:
#        return 0
#    else:
#        return 1
#
#def pc( p1, p2, r):
#    #return p(p1,p2,r)
#    d = mag(p1 - p2)
#    try:
#        return (C_PRIM_SIZE/d)**C_PRIM_STIFFNESS
#    
#        if d < C_PRIM_SIZE:
#            return C_PRIM_TRASH/(d/C_PRIM_SIZE)**C_PRIM_STIFFNESS
#        else:
#            return 0
#    except ZeroDivisionError:
#        return 1000000
#    
#def m( p, c ):
#    return norm( p-c )*speed( p )
#    
#def speed( p ):
#    global current_timestep
#    #return current_timestep    
#    return current_timestep*C_V0*mag(p-C_CENTER)/C_CZONE
#    #return current_timestep*math.pow(mag(p-C_CENTER),2)*0.1
#    #return C_SPEED
#
#def prepare_scene():
#    background = cylinder(pos=vector(0,0,-1), axis=vector(0,0,1),radius=20*C_PRIM_SIZE, length=0.01, color=(0.,0.0,0))
#    center = sphere(pos=vector(0,0,1), radius=0.1, color=(1,1,1))
#    competence = ring( pos=vector(0,0,1), axis=vector(0,0,1), radius=C_CZONE, thickness=C_VISUAL_ZONE_SIZE)
#    drop = ring( pos=vector(0,0,1), axis=vector(0,0,1), radius=C_DZONE, color=(1,0,0), thickness=C_VISUAL_ZONE_SIZE)
#    #drop.thickness=0.01
#    #grid = faces()
#    #x = arange(-20,20,1)
#    #y = arange(-20,20,1)
#    #Z = 0
#    #l = []
#    #for i in range(len(x)-1):
#    #    for j in range(len(y)-1):
#    #        l.append(vector(x[i], y[j], Z))
#    #        l.append(vector(x[i+1], y[j], Z))
#    #        l.append(vector(x[i], y[j+1], Z))
#    #        l.append(vector(x[i+1], y[j], Z))
#    #        l.append(vector(x[i+1], y[j+1], Z))
#    #        l.append(vector(x[i], y[j+1], Z))
#    #    for v in l:
#    #        grid.append( pos=v, color=f_field( v ), normal=C_PLANE_NORMAL)
#    #        if not point2mesh_id.has_key( v ):
#    #            point2mesh_id[ v ] = [len(grid.pos)-1]
#    #        else:
#    #            point2mesh_id[ v ] = point2mesh_id[ v ].append(len(grid.pos)-1)
#
#def competance_grid():
#    l = []
#    e = random.random()
#    #e = 0
#    for i in range(C_DISCRETIZATION):
#        a = e+(float(i)/C_DISCRETIZATION)*2*math.pi
#        x = C_CZONE*math.cos(a)
#        y = C_CZONE*math.sin(a)
#        l.append(vector(x,y,0))
#    return l
#
#def move_primodiums( prims ):
#    for i in prims:
#        prims[ i ] = prims[ i ] + m(prims[ i ], C_CENTER)
#    return prims
#
#def drop_primordiums( prims ):
#    t = {}
#    for i in prims:
#        if p(prims[ i ], C_CENTER, C_DZONE) == 1:
#            t[ i ] = prims[ i  ]
#    return t
#
#def search_new_primordiums( prims, cand ):
#    appcand=[]
#    for i in cand:
#        if  f_field(i, prims) <= C_PRIM_TRASH:
#            appcand.append( i )
#    return appcand
#
#def insert_new_primordiums( prims ):
#    global current_prim
#    global information
#    global current_timestep
#    cand = competance_grid()
#    appcand = search_new_primordiums( prims, cand)
#    if len( appcand ) > 1:
#        if current_timestep > 0:
#            raise ExceptionTooManyCandidates()
#        else:
#            print " !: sorting.."
#            #raise Exception
#    while len(appcand):
#        sort_prim_cand( prims=prims, prim_cand=appcand) 
#        prims[ current_prim ] = appcand[ 0 ]
#        information[ current_prim ] = appcand[ 0 ]
#        current_prim=current_prim+1
#        appcand = search_new_primordiums( prims=prims, cand=appcand)
#    return prims
#
#def sort_prim_cand( prims=None, prim_cand=None):
#    if len( prim_cand ) < 2:
#        return prim_cand
#    #print "sorting..", len( prim_cand )
#    ds = {}        
#    for i in prim_cand:
#        ds[ i ] = f_field( i, prims )
#    prim_cand.sort( lambda x, y: cmp( ds[ y ],  ds[ x ] ))
#    return prim_cand    
#
#def visualise_prims( prims, vis ):
#    nv=[]
#    for i in vis:
#        i.visible=False
#    for i in prims:
#        nv.append( cylinder(pos=prims[ i ], axis=vector(0,0,1),radius=C_PRIM_SIZE, length=0.01*(C_DZONE-mag(C_CENTER-prims[ i ])), color=(0.,0.5,0)))
#        nv.append( ring(pos=prims[ i ], axis=vector(0,0,1),radius=C_PRIM_SIZE, thickness=0.008*(C_DZONE-mag(C_CENTER-prims[ i ])), color=(0.,0.8,0)))
#        nv.append( cylinder(pos=prims[ i ], axis=vector(0,0,1),radius=float(C_PRIM_SIZE)/25, length=50, color=(0.5,0.0,0)))
#    #raw_input()    
#    return nv
#
#def visualise_primordium_information( ):
#    global information
#    p = information
#    pln = len( p )
#    x = range( 1, pln )
#    y = []
#    for i in range( 1, pln ):
#        yi = p[ i ] 
#        zi = p[ i-1 ]
#        yi.z = 0
#        zi.z = 0
#        y.append( get_angle_between_primordias(i, i-1) )
#    pl.plot( x, y )
#    pl.show()
#
#def get_angle_between_primordias( i, j):
#    global information
#    p = information
#    yi = p[ i ]
#    yj = p[ j ]
#    yi.z = 0
#    yj.z = 0
#    d = yi.diff_angle(yj)
#    if mag( rotate( yi, axis=vector(0,0,-1), angle=d )- yj ) < 0.001:
#        return d*360/(2*math.pi)
#    else:
#        return (2*math.pi-d)*360/(2*math.pi)
#    
#    
#def f_field( v, prims ):
#    global C_PRIM_SIZE
#    r = 0
#    for i in prims:
#        r += pc( v, prims[ i ], C_PRIM_SIZE)
#    #return (r,0,0)
#    return r
#
#def mainloop():
#    global primordiums
#    global vis
#    global current_timestep
#    while True:
#        primordiumsT = primordiums.copy()
#        primordiumsT = move_primodiums( primordiumsT )
#        try:
#            primordiumsT = insert_new_primordiums( primordiumsT )
#        except ExceptionTooManyCandidates:
#            current_timestep = current_timestep/10
#            #print current_timestep
#            continue
#        primordiums = primordiumsT.copy()
#        current_timestep = C_INITIALTIMESTEP
#        vis = visualise_prims( prims=primordiums, vis=vis )            
#        primordiums = drop_primordiums(primordiums)
#        
#current_timestep=C_INITIALTIMESTEP        
#current_prim=2
#primordiums={}
#vis=[]
#point2mesh_id={}
#display.autocenter=0
#display.autoscale=0
#information={}
##r = vector(random.random(), random.random(),0)
##r=vector(-8, 0, 0)
#r = vector(-2.1,0,0)
#primordiums[ 0 ] = r
#information[ 0 ] = r
##r = vector(-random.random(), -random.random(),0)
##r = vector(math.cos(math.radians(42.49))*C_CZONE,C_CZONE*math.sin(math.radians(42.49)),0)
#r = vector(2.,0,0)
#primordiums[ 1 ] = r
#information[ 1 ] = r
#prepare_scene()
#mainloop()


class ExceptionTooManyCandidates(Exception):
    pass


class DiscInhibitorPhyllotaxisModel:
    
    def __init__( self, prims=None ):
        self.c_center = vector(0,0,0)
        self.c_czone=1

        self.c_discretization =720
        self.c_plane_normal=vector(0,0,1)
        
        self.c_prim_stiffness=14
        self.c_prim_trash=5
        self.c_prim_size=  4.1
        #: these values are used to determine the inhibition function 
        
        self.c_initial_timestep = 0.01
        self.c_dzone  = 20*self.c_czone
        self.c_v0 = 1.

        self.c_visual_zone_size=0.01       
        #params
        
        self.vis = []
        self.current_timestep = self.c_initial_timestep
        self.time = 0
        self.current_prim = 0
        self.prims = {}
        self.i_prim2time = {}
        self.i_prim2init_pos = {}
        
        self._check_convergance = 0
        
        self.init_prims(prims)
        self.prepare_scene()
   
    def converges( self ):
        y = []
        z = len(self.i_prim2init_pos)
        for j in range( z-10,z):
            y.append( standarize_angle( get_angle_between_primordias( self.i_prim2init_pos[ j], self.i_prim2init_pos[ j-1]) ) )
        for i in range( 2,len(y) ):
            if abs( y[ -1 ] - y[ i ] )  > 2.0:
                return False
        return True        
        
    def f_single_inihibition( self, p1, p2, r):
        d = mag(p1 - p2)
        try:
            return (self.c_prim_size/d)**self.c_prim_stiffness
        except ZeroDivisionError:
            return 1000000
    
    def displacement( self, p, c ):
        # scalar_speed * normalised radial vector    
        return norm( p-c )*self.scalar_speed( p )

    def scalar_speed( self, p ):
        return self.current_timestep*self.c_v0*mag(p-self.c_center)/self.c_czone

    def prepare_scene( self ):
        self.background = cylinder(pos=vector(0,0,-1), axis=vector(0,0,1),radius=1.5*self.c_dzone, length=0.01, color=(0.,0.0,0))
        self.center = sphere(pos=vector(0,0,1), radius=0.1, color=(1,1,1))
        self.competence = ring( pos=vector(0,0,1), axis=vector(0,0,1), radius=self.c_czone, thickness=self.c_visual_zone_size)
        self.drop = ring( pos=vector(0,0,1), axis=vector(0,0,1), radius=self.c_dzone, color=(1,0,0), thickness=self.c_visual_zone_size)

    def competance_grid( self ):
        l = []
        e = random.random()
        for i in range(self.c_discretization):
            a = e+(float(i)/self.c_discretization)*2*math.pi
            x = self.c_czone*math.cos(a)
            y = self.c_czone*math.sin(a)
            l.append(vector(x,y,0))
        return l

    def move_primodiums( self, prims ):
        for i in prims:
            prims[ i ] = prims[ i ] + self.displacement(prims[ i ], self.c_center)
        return prims

    def drop_primordiums( self, prims ):
        t = {}
        for i in prims:
            if mag(prims[ i ] - self.c_center) < self.c_dzone:
                t[ i ] = prims[ i  ]
        return t

    def search_new_primordiums( self, prims, cand ):
        appcand=[]
        for i in cand:
            if  self.f_inhibition(i, prims) <= self.c_prim_trash:
                appcand.append( i )
        return appcand

    def insert_new_primordiums( self, prims ):
        cand = self.competance_grid()
        appcand = self.search_new_primordiums( prims, cand)
        if len( appcand ) > 1:

            if self.current_timestep > 0:
                raise ExceptionTooManyCandidates()
            else:
                print " !: sorting.."
        self.prims = prims.copy()
        while len(appcand):
            appcand = self.sort_prim_cand( prims=self.prims, prim_cand=appcand) 
            self.add_prim( appcand[ 0 ] )
            appcand = self.search_new_primordiums( prims=self.prims, cand=appcand)

    def add_prim( self, prim ):
        self.prims[ self.current_prim ] = prim
        self.i_prim2init_pos[ self.current_prim ] = prim
        self.i_prim2time[ self.current_prim ] = self.time
        self.current_prim += 1
        print self.current_prim
    

    def sort_prim_cand( self, prims=None, prim_cand=None):
        if len( prim_cand ) < 2:
            return prim_cand
        ds = {}        
        for i in prim_cand:
            ds[ i ] = self.f_inhibition( i, prims )
        prim_cand.sort( lambda x, y: cmp( ds[ y ],  ds[ x ] ))
        return prim_cand    

    def visualise_prims( self, prims, vis ):
        nv=[]
        for i in vis:
            i.visible=False
        for i in prims:
            nv.append( cylinder(pos=prims[ i ], axis=vector(0,0,1),radius=self.c_prim_size, length=0.01*(self.c_dzone-mag(self.c_center-prims[ i ])), color=(0.,0.5,0)))
            nv.append( ring(pos=prims[ i ], axis=vector(0,0,1),radius=self.c_prim_size, thickness=0.008*(self.c_dzone-mag(self.c_center-prims[ i ])), color=(0.,0.8,0)))
            nv.append( cylinder(pos=prims[ i ], axis=vector(0,0,1),radius=float(self.c_prim_size)/25, length=50, color=(0.5,0.0,0)))
        #raw_input()    
        return nv

    def visualise_time_diff( self ):
        p = self.i_prim2time
        pln = len( p )
        x = range( 1, pln )
        y = []
        for i in range( 1, pln ):
            y.append( p[ i ] - p[ i-1 ] )
        pl.plot( x, y )
        pl.show()


    def visualise_div_ang( self ):
        p = self.i_prim2init_pos
        pln = len( p )
        x = range( 1, pln )
        y = []
        for i in range( 1, pln ):
            yi = p[ i ] 
            zi = p[ i-1 ]
            yi.z = 0
            zi.z = 0
            y.append( self.get_angle_between_primordias(i, i-1) )
        pl.plot( x, y )
        pl.show()

    def get_angle_between_primordias( self, i, j):
        p = self.i_prim2init_pos
        yi = p[ i ]
        yj = p[ j ]
        yi.z = 0
        yj.z = 0
        d = yi.diff_angle(yj)
        if mag( rotate( yi, axis=self.c_plane_normal, angle=d )- yj ) < 0.001:
            return d*360/(2*math.pi)
        else:
            return (2*math.pi-d)*360/(2*math.pi)
    
        
    def f_inhibition( self, v, prims ):
        r = 0
        for i in prims:
            r += self.f_single_inihibition( v, prims[ i ], self.c_prim_size)
        return r
    
    def run( self, nbr_prim=1000000000 ):
        while not len( self.i_prim2init_pos ) > nbr_prim:
            primordiumsT = self.prims.copy()
            primordiumsT = self.move_primodiums( primordiumsT )
            try:
                self.time += self.current_timestep
                self.insert_new_primordiums( primordiumsT )
            except ExceptionTooManyCandidates:
                self.time -= self.current_timestep
                self.current_timestep = self.current_timestep/10
                continue
            #self.prims = primordiumsT.copy() #TODO drop copy
            self.current_timestep = self.c_initial_timestep
            self.vis = self.visualise_prims( prims=self.prims, vis=self.vis )            
            self.prims = self.drop_primordiums(self.prims)
            if self.check_convergance():
                break
            
    def check_convergance( self ):
        if self._check_convergance < self.current_prim:
            self._check_convergance = self.current_prim
            if self.current_prim > 20:     
                return self.converges()
            else:
                return False

    def init_prims( self, prims=None ):         
        if not prims == None:
            for i in prims:
                self.add_prim( prims[ i ] )
        else:
            self.add_prim( vector(-self.c_czone,0,0) )
            self.add_prim( vector(self.c_czone+0.01,0,0) )


def get_angle_between_primordias( yi, yj):
    d = yi.diff_angle(yj)
    if mag( rotate( yi, axis=(0,0,1), angle=d )- yj ) < 0.001:
        return d*360/(2*math.pi)
    else:
        return (2*math.pi-d)*360/(2*math.pi)

def plot_time( timeD, min_gamma=None, max_gamma=None, how_many_last_values=10 ):
    y = []
    x = []
    for i in timeD:
        if i <= max_gamma and i >= min_gamma:
            k = len( timeD[ i ] )
            for j in range(k-how_many_last_values, k):
                x.append( i )
                #y.append(  get_angle_between_primordias( divD[ i ][ j], divD[ i ][ j-1])  )
                y.append( timeD[ i ][ j] - timeD[ i ][ j-1])
    pl.plot( x, y, "." )
    pl.show()    
    
def plot_time_change( timeD, gamma ):
    y = []
    x = []
    i = gamma
    for j in range( 1,len( timeD[ i ] ) ):
        x.append( j )
        y.append( timeD[ i ][ j] - timeD[ i ][ j-1])
    pl.plot( x, y, "." )
    pl.show()

def plot_divergance_angel_change( divD, gamma ):       
    y = []
    x = []
    i = gamma
    for j in range( 1,len( divD[ i ] ) ):
        x.append( j )
        #y.append(  get_angle_between_primordias( divD[ i ][ j], divD[ i ][ j-1])  )
        y.append( standarize_angle( get_angle_between_primordias( divD[ i ][ j], divD[ i ][ j-1]) ) )
    pl.plot( x, y, "." )
    pl.show()    

def plot_divergance_angle( divD, min_gamma=None, max_gamma=None, how_many_last_values=10 ):       
    y = []
    x = []
    for i in divD:
        if i <= max_gamma and i >= min_gamma:
            k = len( divD[ i ] )
            for j in range(k-how_many_last_values, k):
                x.append( i )
                #y.append(  get_angle_between_primordias( divD[ i ][ j], divD[ i ][ j-1])  )
                y.append( standarize_angle( get_angle_between_primordias( divD[ i ][ j], divD[ i ][ j-1]) ) )
    pl.plot( x, y, "." )
    pl.show()    
    
def standarize_angle( a ):
    if a > 180:
        return 360 - a 
    return a

m = DiscInhibitorPhyllotaxisModel()
m.c_prim_size = 1.8
raw_input()
m.run(nbr_prim=200)
m.visualise_div_ang()
m.visualise_time_diff()
import pickle
#prim_stable = pickle.load(open("prim1.4-3.5-0.2--2000.pickle"))
#
##psyco.full()            
#ang = {}
#tim = {}
#prim = {}
#a =prim_stable.keys()
#print a
#for i in a:
#    m = DiscInhibitorPhyllotaxisModel(prims=prim_stable[ i ])
#    print "calculating for: ", i
#    m.c_prim_size = i
#    m.run(nbr_prim=100)
#    ang[ i ]= m.i_prim2init_pos.copy()
#    tim[ i ]= m.i_prim2time.copy()
#    prim[ i ] =m.prims.copy()
#import pickle
#pickle.dump(ang, open("ang1.4-3.5-0.2-2000.pickle","w" ))
#pickle.dump(tim, open("tim1.4-3.5-0.2-2000.pickle","w" ))
#pickle.dump(prim, open("prim1.4-3.5-0.2--2000.pickle","w" ))
ang = pickle.load(open("ang1.4-3.5-0.2-2000.pickle"))
tim = pickle.load(open("tim1.4-3.5-0.2-2000.pickle"))
