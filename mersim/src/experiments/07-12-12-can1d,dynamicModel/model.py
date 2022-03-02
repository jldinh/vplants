#!/usr/bin/env python
"""model.py
Canalisation model in 1D.

:version: 2006-05-15 15:21:06CEST
:author:  szymon stoma
"""

import visual
import math
import pylab
import scipy
import scipy.integrate.odepack
import copy
import random
import povexport

class LinearTransportModel:
    """Linear transport model of IAA using PIN transporters. 
    
    This is not optimal version (neighborhood defined by relation, not explicitly by cell number).
    """

    def __init__( self, nbr=100 ):
        """Initiation.
        
        The creation of the system. Contains constants with description.
        
        :parameters:
            nbr : `int`
                Number of cells in the system.
    """
        ########################################################
        #### equation constants
        self.c_sigma_a = 0.1 #creation of IAA
        self.c_theta_a = 0.01 #destruction of IAA
        self.c_gamma_act = 0.1 #active flux coef.
        self.c_gamma_diff = 0.1 # diffusion coef.
        self.c_sigma_p = 0.01 # creation of PIN
        self.c_theta_p = 0.1 # destruciton of PIN
        self.c_iaa_init_val= 0. # iaa initial value for *normal* cell is computed: v = c_iaa_init_val*(1+random()*c_iaa_init_rand_fact)
        self.c_iaa_init_rand_fact= 0. # look above
        self.c_prim_iaa_conc = 0. # the concentration of IAA in the primordium (kept fixed)
        self.c_pin_init = self.c_sigma_p/self.c_theta_p # pin initial value
        #### meristem geometry constants
        self.c_prim_trs = 7.0
        self.c_com_zone = 10        
        #### computation constants
        self.t = 0
        self.h = 1
        self.c_break_step_nbr=100 # if stable step is not found we break after this number of steps
        self.c_stable_tolerance=0.2 # the change of auxin in each cell must be below this value to call a step stable
        self.c_rtol = 0.1 # relative tolerance accepted by ODE solver
        self.c_atol = 0.1 # absolute tolerance accepted by ODE solver
        #### display constants
        self.c_disp_aux_max = 10
        ########################################################
        
        
        self.cells={}
        self.walls={}
        self.prims = []
        self.neigh = {}
        self.visualisation=[]
        self.center= -1#no center! nbr/2
        self.create( nbr )
        self.prepare_f( )
        #self.scene = visual.display(title='Canalisation model',width=600, height=200)
        self.frame=0
        self.history = {}
        
    def create( self, nbr):
        """Creates the cells and sets initial values for IAA and PIN.
        
        <Long description of the function functionality.>
        
        :parameters:
            nbr : `int`
                Number of cells.
        """
        for i in range( nbr ):
            self.cells[ i ] =  self.c_iaa_init_val+self.c_iaa_init_rand_fact*self.c_iaa_init_val*random.random()
        for i in range( nbr-1 ):
            #for PIN conc
            self.walls[ (i, i+1) ] = self.c_pin_init
            self.walls[ (i+1, i) ] = self.c_pin_init
        for i in range(1,nbr-1):
            self.neigh[ i ] = [i-1,i+1]
        self.neigh[ 0 ] = [1]
        self.neigh[ nbr-1 ] = [nbr-2]
        self.set_prims( prims=self.prims )
    
    def set_prims( self, prims=None ):
        """Sets primordias.
        
        The primordium has fixed IAA concentration.        
        :parameters:
            prims : `list(int)`
                Cells to became primordias.
        """
        self.prims=prims
        for i in prims:
            self.cells[ i ] = self.c_prim_iaa_conc
    
    def prepare_f( self ):
        """Creates the translation from dicts to list required by integrator.
        
        <Long description of the function functionality.>
        
        """
        self.cell2sys = {}
        self.wall2sys = {}
        ind = 0
        for i in self.cells.keys():
            self.cell2sys[ i ] = ind
            ind += 1
        for i in self.walls.keys():
            self.wall2sys[ i ] = ind
            ind += 1
        
    def prepare_x0( self ):
        """Creates the translation from dicts to list required by integrator.
        
        <Long description of the function functionality.>
        
        """
        x0 = []
        for x in range( len(self.cells) + len( self.walls ) ):
            x0.append(0)
        for i in self.cells.keys():
            x0[ self.cell2sys[ i ] ] = self.cells[ i ]
        for i in self.walls.keys():
            x0[ self.wall2sys[ i ] ] = self.walls[ i ]
        return x0
     
    def f( self, x, t ):
        """Funtion computing  derivatives.
        
        <Long description of the function functionality.>
        
        :parameters:
            x : `list(float)`
                contains the system of equation
            t : `float`
                current time
        """
        def Fi( x ):
            if x < 0:
                return 0
            return (x*x)
        
        def P( wid, t, x):    
            return x[ self.wall2sys[ wid ] ] 
        
        def J( (i, j), t, x):
            return self.c_gamma_act*(-A(j,t,x)*P((j,i),t,x)+A(i,t,x)*P((i,j),t,x))+self.c_gamma_diff*(A(i,t,x)-A(j,t,x)) #diff+act

        def A( cid, t, x ):
            return x[ self.cell2sys[ cid ] ]
        
        x2 = copy.copy( x ) 
        for i in self.cells.keys():
            x2[ self.cell2sys[ i ] ] = 0
            if not self.i_local_evacuate( i ) and not self.i_center_evacuate( i ):
                x2[ self.cell2sys[ i ] ] = self.c_sigma_a - self.c_theta_a*A(i,t,x) #- self.c_delta*self.i_local_evacuate( i ) - self.c_tau*self.i_center_evacuate( i ) #OK
                for n in self.neigh[ i ]:
                    x2[ self.cell2sys[ i ] ] += J((n,i),t,x) - J((i,n),t,x)
        for i in self.walls.keys():
            x2[ self.wall2sys[i] ] = Fi(J(i,t,x))+self.c_sigma_p-self.c_theta_p*P(i,t,x)
        return x2
    
    def i_local_evacuate( self, i ):
        if i in self.prims:
            return 1
        else:
            return 0

    def i_center_evacuate( self, i ):
        #if i in range( self.center-self.c_com_zone, self.center+self.c_com_zone):
        if i == self.center:
            return 1
        else:
            return 0
            
    def run( self ):
        stable = False
        i = 0
        while not stable and i < self.c_break_step_nbr:
            print i, self.t
            i+=1
            (res,self.info)= scipy.integrate.odepack.odeint( self.f, self.prepare_x0(), [self.t, self.t+self.h], rtol=self.c_rtol, atol=self.c_atol,  full_output=1 )
            self.t += self.h                
            stable = self.rate_error( self.cells, res[1])
            self.update( res[1] )
            x=[]
            y=[]
            y2=[]
            z = 0
            for i in self.cells.keys():
                x.append(i)
                y.append(self.cells[ i ] )
                z += self.cells[ i ]
            print " #: aux sum: ", z, "aux min:", min(y), "aux max:", max(y)
            print " #: aux min:", min(self.walls.values()), "aux max:", max(self.walls.values())
            print self.info
            #self.plot_pin_con()
            self.history[ self.frame ] = {"cells":self.cells.copy(),"walls":self.walls.copy(),"prims":self.prims}
        
            #self.create_prims()
            #self.move()
        #import pickle
        #pickle.dump( self.history, file("history.pickle", "w") )

    def stable_step( self, nbr=1 ):
        for i in range(nbr):
            self.run()
        self.plot()
        
 
    def update( self, x2 ):        
        for i in self.cells.keys():
            t = x2[ self.cell2sys[ i ] ]
            self.cells[ i ] = t
        for i in self.walls.keys():
            t = x2[ self.wall2sys[ i ] ]
            self.walls[ i ] = t 
        
    def rate_error( self, xn, xnprim ):
        tem = {}
        for i in self.cells.keys():
            tem[ i ] = xnprim[ i ]
        xnprim = tem
        t = True
        for i in self.cells.keys():
            if self.c_stable_tolerance < abs( xn[i] - xnprim[i] ):
                t=False
                break
        print " #: errror =  ", abs( xn[i] - xnprim[i] )
        #raw_input()
        return t

    #def create_prims( self ):
    #    created = False
    #    if self.cells[ self.center+self.c_com_zone ] > self.c_prim_trs:
    #        self.prims.append( self.center+self.c_com_zone )
    #        created = True
    #    if not created:    
    #        if self.cells[ self.center-self.c_com_zone ] > self.c_prim_trs:
    #            self.prims.append( self.center-self.c_com_zone )
    #
    #def move( self ):
    #    t = {}
    #    for i in range( self.center-1 ):
    #        self.cells[ i ] = self.cells[ i+1 ]
    #        t[ (i,i+1) ] = self.walls[ (i+1,i+2) ]
    #        if i != 0:
    #            t[ (i-1,i) ] =  self.walls[ (i,i+1) ]
    #    for i in range(self.center+2, self.center*2):
    #        self.cells[ i ] = self.cells[ i-1 ]
    #        if i != 2*self.center:
    #            t[ (i,i+1) ] = self.walls[ (i-1,i) ]
    #        t[ (i-1,i) ] =  self.walls[ (i-2,i-1) ]
    #    p = []
    #    for i in self.prims :
    #        if i in range(0, self.center*2-1):
    #            if i < self.center and i != 0:
    #                    p.append(i-1)
    #            if i > self.center and i!=99:
    #                p.append(i+1)
    #    self.prims = p+[self.center]
                
            
    #def visualise( self ):
    #    #visual.display.autoscale=0
    #    #visual.display.autocenter=0
    #    for i in self.visualisation:
    #        i.visible=False
    #    d = len( self.cells)
    #    for i in range( d ):
    #        a = (float(i)/(2*d))*2*math.pi
    #        x = 10*math.cos(a)
    #        y = 10*math.sin(a)
    #        p =  visual.vector(x,y,0)
    #        c = interpolate_color( color1=(0.,0.1,0), color2=(0,1,0), range=[5,7],value=self.cells[ i ] )
    #        radius= 0.2
    #        #self.visualisation.append( visual.sphere(pos=0.85*p, radius=radius*0.93,color=c ) )
    #        if i in [40,60]:
    #            #radius =0.4
    #            c=(1,1,0)
    #        self.visualisation.append( visual.sphere(pos=p, radius=radius,color=c ) )
    #        if i not in [0,99]:
    #            sn = visual.norm( visual.rotate(p,angle=math.pi/2,axis=visual.vector(0,0,1) ))
    #            c2=(1,0,0)#interpolate_color( color1=(0,0,0), color2=(1,0,0), range=[0,0.1],value=(self.walls[ (i,i-1) ] -self.walls[ (i,i+1) ] ) )
    #            self.visualisation.append( visual.arrow( pos=0.97*p, axis= -5*(self.walls[ (i,i-1) ] -self.walls[ (i,i+1) ] )*sn,color=c2 ) )
    #        #if i not in self.prims:
    #        #self.visualisation.append(visual.arrow(pos=p,axis=self.cells[ i ]* visual.norm(p),radius=0.1,color=(1,1,1),shaftwidth=0.1,fixedwidth=1))
    #    #self.visualisation.append(visual.sphere(pos=visual.vector(), radius=0.3,color=(0,1,0)))
    #    for i in self.prims:
    #        if i != self.center:
    #            a = (float(i)/(2*d))*2*math.pi
    #            x = 9.7*math.cos(a)
    #            y = 9.7*math.sin(a)
    #            p =  visual.vector(x,y,0)
    #            c = interpolate_color( color1=(1,0,0), color2=(0,1,0), range=[7,10],value=self.cells[ i ] )
    #            self.visualisation.append(visual.arrow(pos=p,axis=visual.norm(-abs(self.cells[ i ])/10.1*p),radius=0.1,color=(1,0,0)))
    #    #for i in [40,60]:
    #    #    a = (float(i)/(2*d))*2*math.pi
    #    #    x = 9.5*math.cos(a)
    #    #    y = 9.5*math.sin(a)
    #    #    p =  visual.vector(x,y,0)
    #    #    c = interpolate_color( color1=(0,1,0), color2=(1,0,0), range=[6,10],value=self.fields[ i ] )
    #    #    self.visualisation.append(visual.cylinder(pos=p,axis=self.fields[ i ]/10.1*p,color=c,shaftwidth=0.1,fixedwidth=1))
    #    #visual.display.autoscale=1
    #    #visual.display.autocenter=1

   #def visual_display( self ):
   #     self.visualise()
   #     visual.display.title=str(self.frame)+".pov"
   #     self.frame+=1
   #     povexport.export()

    def plot( self ):
        x = []
        y=[]
        y2=[]
        iaa=[]
        for i in self.cells.keys():
            x.append(i)
            iaa.append( 0 )
            y.append(0 )
            y2.append(0 )
        
            
        pylab.subplot( 211 )
        for i in range( len( self.cells ) ):
            iaa[ i ] =self.cells[ i ]
        pylab.plot(x, iaa, ".r")
        pylab.axis( [0,len(self.cells)-1,0,self.c_disp_aux_max] )
        pylab.xlabel( "Cells" )
        pylab.ylabel( "IAA  quantities" )
        pylab.title( "IAA/PIN concentration" )

        for (i,j) in self.walls.keys():
            if i > j:
                y[ i ]+=self.walls[ (i,j) ] 
            else:
                y2[ i ]+=self.walls[ (i,j) ] 
        
        pylab.subplot( 212 )        
        pylab.plot(x, y, "r",x, y2, "b")
        pylab.xlabel( "Cells" )
        pylab.ylabel( "PIN  quantities" )
        
        
        pylab.show()

    def play( self ):
        """To generate nice display (for animations).
        
        <Long description of the function functionality.>
        """
        visual.cylinder(radius=10, pos=visual.vector(0,0,-5),axis=(0,0,0.1),color=(0,0,0))
        import pickle
        self.history = pickle.load( open( "history.pickle" ) )
        frames = self.history.keys()
        frames.sort()
        self.visualise()
        for i in frames:
            self.cells = self.history[ i ]["cells"]
            self.walls = self.history[ i ]["walls"]
            self.prims = self.history[ i ]["prims"]
            self.visualise()
            #raw_input()
            visual.display.title=str(self.frame)
            self.frame+=1
            povexport.export()

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

if __name__ == "__main__":
    cells = 40
    m=LinearTransportModel(cells)
    m.set_prims([0, cells1-])
    m.stable_step()
    #m.play()
