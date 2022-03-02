#!/usr/bin/env python
"""model.py
Desc.

:version: 2006-05-15 15:21:06CEST
:author:  szymon stoma
"""

import visual
import math
import pylab
import scipy
import scipy.integrate.odepack
import copy

class SinkModel:
    def __init__( self, nbr=100 ):
        self.c_diff_coef = 5.5 #3.5
        self.c_dest_coef = 0.1
        self.c_creation_coef = 1
        self.c_local_evacuate_coef= 0.6
        self.c_act_tra_coef = 0.1
        self.c_prim_trs = 9.9
        self.c_com_zone = 10
        self.c_error1 = 0.01
        
        self.t = 0
        self.h_for_automate_step = 30#0.15
        self.h = 0.15
        self.fields=[]
        self.flux=[]
        self.prims = []
        self.visualisation=[]
        self.center= nbr/2
        self.create( nbr )
        
        self.integrator = RungeKutta()
        self.f = self.prepare_f()
        self.f2 = self.prepare_f2()
        

    def create( self, nbr):
        for i in range( nbr ):
            self.fields.append(  0 )
            self.flux.append(  0 )

    def run( self ):
        while True:
            stable = False
            i = 0
            while not stable:
                print i, self.t
                i+=1
                res= scipy.integrate.odepack.odeint( self.fun, copy.copy(self.fields), [self.t, self.t+self.h_for_automate_step], rtol=0.009, atol=0.9)
                res=res[1]
                #raw_input()
                #res = self.integrator.step(self.f, self.fields, self.t, self.h )
                self.t += self.h_for_automate_step                
                stable = self.rate_error( self.fields, res)
                self.fields = res
            pylab.plot(range(100), self.fields)
            pylab.show()
            #self.visualise()
                
            self.create_prims()
            self.move()

    def rate_error( self, xn, xnprim ):
        t = True

        for i in range( len(xn) ):
            if self.c_error1 < abs( xn[i] - xnprim[i] ):
                t=False
                break
        #raw_input()
        return t

    def create_prims( self ):
        created = False
        if self.fields[ self.center+self.c_com_zone ] > self.c_prim_trs:
            self.prims.append( self.center+self.c_com_zone )
            created = True
        if not created:    
            if self.fields[ self.center-self.c_com_zone ] > self.c_prim_trs:
                self.prims.append( self.center-self.c_com_zone )

    def move( self ):
        for i in range( self.center-1 ):
            self.fields[ i ] = self.fields[ i+1 ]
        for i in range(self.center+2, self.center*2):
            self.fields[ i ] = self.fields[ i-1 ]
        p = []
        for i in self.prims :
            if i in range(0, self.center*2-1):
                if i < self.center:
                    p.append(i-1)
                if i > self.center:
                    p.append(i+1)
        self.prims = p#+[self.center]
                
            
    def visualise( self ):
        for i in self.visualisation:
            i.visible=False
        d = len( self.fields)
        for i in range( d ):
            a = (float(i)/(2*d))*2*math.pi
            x = 10*math.cos(a)
            y = 10*math.sin(a)
            p =  visual.vector(x,y,0)
            c = interpolate_color( color1=(1,0,0), color2=(0,1,0), range=[7,10],value=self.fields[ i ] )
            radius= 0.2
            if i in [40,60]:
                radius =0.4
            self.visualisation.append( visual.sphere(pos=p, radius=radius,color=c ) )
        self.visualisation.append(visual.sphere(pos=visual.vector(), radius=0.3,color=(0,1,0)))
        for i in self.prims:
            a = (float(i)/(2*d))*2*math.pi
            x = 9.7*math.cos(a)
            y = 9.7*math.sin(a)
            p =  visual.vector(x,y,0)
            c = interpolate_color( color1=(1,0,0), color2=(0,1,0), range=[7,10],value=self.fields[ i ] )
            self.visualisation.append(visual.arrow(pos=p,axis=-self.fields[ i ]/10.1*p,radius=0.1,color=c,shaftwidth=0.1,fixedwidth=1))
        #for i in [40,60]:
        #    a = (float(i)/(2*d))*2*math.pi
        #    x = 9.5*math.cos(a)
        #    y = 9.5*math.sin(a)
        #    p =  visual.vector(x,y,0)
        #    c = interpolate_color( color1=(0,1,0), color2=(1,0,0), range=[6,10],value=self.fields[ i ] )
        #    self.visualisation.append(visual.cylinder(pos=p,axis=self.fields[ i ]/10.1*p,color=c,shaftwidth=0.1,fixedwidth=1))

    def i_local_evacuate( self, i ):
        if i in self.prims:
            return 1
        else:
            return 0
        

    def prepare_f( self ):
        f = []
        for i in range( len( self.fields ) ):
            f.append(
                self.gen_f( i )
            )
        return f

    def gen_f( self, i ):
        a = self.c_creation_coef
        b = self.c_dest_coef
        c = self.c_diff_coef
        d = self.c_local_evacuate_coef
        if i == 0:
            return lambda t, x: a - b*x[ i ]+c*(x[i+1]- x[ i ]) - d*self.i_local_evacuate( i )*x[i]
        if i == len(self.fields)-1:
            return lambda t, x: a - b*x[ i ] +c*(x[i-1] - x[ i ]) - d*self.i_local_evacuate( i )*x[i]
        return lambda t, x: a - b*x[ i ] +c*(x[i-1]+x[i+1]-2*x[ i ]) - d*self.i_local_evacuate( i )*x[i]

    def prepare_f2( self ):
        f = []
        for i in range( len( self.fields ) ):
            f.append(
                self.gen_f( i )
            )
        return f

    def fun( self, a, t ):
        res = range( len( a ) )
        for i in range( len( a ) ):
            res[ i ] = self.f2[i]( t, a )
        return res
    
    def gen_f2( self, i ):
        a = self.c_creation_coef
        b = self.c_dest_coef
        c = self.c_diff_coef
        d = self.c_local_evacuate_coef
        if i == 0:
            return lambda x, t: a - b*x[ i ]+x[i+1]- x[ i ] - d*self.i_local_evacuate( i )*x[i]
        if i == len(self.fields)-1:
            return lambda x, t: a - b*x[ i ] +c*(x[i-1] - x[ i ]) - d*self.i_local_evacuate( i )*x[i]
        return lambda x, t: a - b*x[ i ] +c*(x[i-1]+x[i+1]-2*x[ i ] - d*self.i_local_evacuate( i )*x[i])

    
class RungeKutta:
    """
    Runge-Kutta 4th order solver
    """
    def __init__(self):
        pass
        
    def step(self, f, x, t,delta_t):
        # create lists for the constants and new values for the variables
        k1 = []; k2 = []; k3 = []; k4 = []; tmpx = []; newx = []
        for index in range(0,len(x)):
            k1.append(0); k2.append(0); k3.append(0); k4.append(0)
            tmpx.append(0); newx.append(0);
        # compute the k1's
        for index in range(0,len(x)):
            k1[index] = delta_t*f[index](t,x)
        # compute the k2's
        for index in range(0,len(x)):
            tmpx[index] = x[index] + k1[index]/2
        for index in range(0,len(x)):
            k2[index] = delta_t*f[index](t+delta_t/2, tmpx)
        # compute the k3's
        for index in range(0,len(x)):
            tmpx[index] = x[index] + k2[index]/2 
        for index in range(0,len(x)):
            k3[index] = delta_t*f[index](t+delta_t/2, tmpx)
        # compute the k4's
        for index in range(0,len(x)):
            tmpx[index] = x[index] + k3[index]
        for index in range(0,len(x)):
            k4[index] = delta_t*f[index](t+delta_t, tmpx)
        # compute the new variables
        for index in range(0,len(x)):
            newx[index] = x[index] + ( k1[index]+2*k2[index]+2*k3[index]+k4[index] )/6
        return newx

def interpolate_color( color1=None, color2=None, range=None, value=None):
    """Returns the interpolated RGB value between color1 and color2.
    assumptions:
    * color?= (r,g, b)
    * range = (x1, x2)
    * x1 < x2
    * value is in range
    """
    try:
        r,b,g = color1
        r2,b2,g2 = color2
        s0, s1 = range
        p = (value-s0) / (s1-s0) 
        dr = float( r2 - r )
        dg = float( g2 - g )
        db = float( b2 - b )
        c = (r+p*dr, b+p*db , g+p*dg)
    except ZeroDivisionError:
        return color1
    return c 


if __name__ == "__main__":
    m=SinkModel()
    m.run()
