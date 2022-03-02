#!/usr/bin/env python
"""model.py
Canalisation model in 1D.

:version: 2006-05-15 15:21:06CEST
:author:  szymon stoma
"""
import sys
from matplotlib import rc, rcParams,use
if("win" in sys.platform):
    print "LateX writing not available"
    rc('text', usetex=False )
else:
    rc('text', usetex=True )
#use('Qt4Agg')

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

    def __init__( self, cell_nbr=20 ):
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
        self.c_gamma_act = 0.01 #active flux coef.
        self.c_iaa_act_enabled=True
        self.c_gamma_diff = 0.001 # diffusion coef.
        self.c_iaa_diff_enabled=True
        self.c_sigma_p = 0.1 # creation of PIN
        self.c_theta_p = 0.05 # destruciton of PIN
        self.c_iaa_init_val= 0. # iaa initial value for *normal* cell is computed: v = c_iaa_init_val*(1+random()*c_iaa_init_rand_fact)
        self.c_iaa_init_rand_fact= 0. # look above
        self.c_prim_iaa_conc = 0. # the concentration of IAA in the primordium (kept fixed)
        self.c_pin_init = self.c_sigma_p/self.c_theta_p # pin initial value
        self.c_phi_str = """def Phi( x ):
                                            if x < 0:
                                                return 0
                                            return 0.15*x"""
        self.f_phi = pyfunction( self.c_phi_str )
        self.c_PIN_capping_enabled=False
        self.c_max_PIN=0.2
        self.c_sink_fixed_concentration=True
        self.c_sink_destruction_rate=0.1
        
        #dynamics
        
        #### meristem geometry constants
        self.c_prim_trs = 9.0
        self.c_com_zone = 3
        self.c_cell_nbr=cell_nbr
        #### computation constants
        self.t = 0
        self.h = 1.
        self.c_step_nbr = 100 # nbr of stable step in a run procedure
        self.c_break_step_nbr=1 # if stable step is not found we break after this number of steps
        self.c_stable_tolerance=1 # the change of auxin in each cell must be below this value to call a step stable
        self.c_rtol = 0.1 # relative tolerance accepted by ODE solver
        self.c_atol = 0.1 # absolute tolerance accepted by ODE solver
        self.c_new_simulation = False # start new simulation every run
        #### display constants
        self.c_disp_aux_max = 6
        self.c_show=True
        self.c_disp_pin_max= 4.
        self.c_disp_pin_min=1.9
        self.c_dynamic_pin=False
        self.c_dynamic_aux=True
        ########################################################
        
        
        self.cells={}
        self.walls={}
        self.prims = []
        self.neigh = {}
        self.visualisation=[]
        self.center=  cell_nbr/2
        self.create( self.c_cell_nbr )
        self.prepare_f( )
        #self.scene = visual.display(title='Canalisation model',width=600, height=200)
        self.frame=0
        self.data = {} # contains different data concerning the simulation
        
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
        #self.set_prims( prims=self.prims )
        self.history = {}
        self.history[ self.t ] = {"stable": True, "cells":self.cells.copy(),"walls":self.walls.copy(),"prims":self.prims}
        self.data = {"primordia_in_rounds":[], "Pin_max":0., "Pin_min":10000000.}
        self.frame=0
    
    def add_prim( self, prim=None, nbr=None ):
        """Sets primordias.
        
        The primordium has fixed IAA concentration.        
        :parameters:
            prims : `list(int)`
                Cells to became primordias.
        """
        self.prims.append( prim ) 
        self.cells[ prim ] = self.c_prim_iaa_conc
        self.data["primordia_in_rounds"].append(self.frame)
    
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
        #print self.cells, self.cell2sys
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
        #def Fi( x ):
        #    if x < 0:
        #        return 0
        #    return (x*x)
        
        def P( wid, t, x):    
            return x[ self.wall2sys[ wid ] ] 
        
        def J( (i, j), t, x):
            t=0.
            if self.c_iaa_diff_enabled:
                t += self.c_gamma_diff*(A(i,t,x)-A(j,t,x))
            if self.c_iaa_act_enabled:    
                t += self.c_gamma_act*(-A(j,t,x)*P((j,i),t,x)+A(i,t,x)*P((i,j),t,x))
            return t

        def A( cid, t, x ):
            return x[ self.cell2sys[ cid ] ]
        
        x2 = copy.copy( x ) 
        for i in self.cells.keys():
            x2[ self.cell2sys[ i ] ] = 0
            if not self.i_local_evacuate( i ):# and not self.i_center_evacuate( i ):
                x2[ self.cell2sys[ i ] ] = self.c_sigma_a - self.c_theta_a*A(i,t,x) 
                for n in self.neigh[ i ]:
                    x2[ self.cell2sys[ i ] ] += J((n,i),t,x) - J((i,n),t,x)
            elif not self.c_sink_fixed_concentration:
                #print "ff"
                x2[ self.cell2sys[ i ] ] = self.c_sigma_a - (self.c_theta_a+self.c_sink_destruction_rate)*A(i,t,x) 
                for n in self.neigh[ i ]:
                    x2[ self.cell2sys[ i ] ] += J((n,i),t,x) - J((i,n),t,x)                    
        for i in self.walls.keys():
            x2[ self.wall2sys[i] ] = self.f_phi(J(i,t,x))+self.c_sigma_p-self.c_theta_p*P(i,t,x)
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
        if self.c_new_simulation:
            self.create( len(self.cells) )
        self.prepare_f()
        for i in range( self.c_step_nbr):
            stable = False
            j = 0
            while not stable and j < self.c_break_step_nbr:
                print i, self.t
                j+=1
                (res,self.info)= scipy.integrate.odepack.odeint( self.f, self.prepare_x0(), [self.t, self.t+self.h], rtol=self.c_rtol, atol=self.c_atol,  full_output=1 )
                self.t += self.h                
                stable = self.rate_error( self.cells, res[1])
                self.update( res[1] )
                x=[]
                y=[]
                y2=[]
                z = 0
                for ii in self.cells.keys():
                    x.append(ii)
                    y.append(self.cells[ ii ] )
                    z += self.cells[ ii ]
                print " #: aux sum: ", z, "aux min:", min(y), "aux max:", max(y)
                print " #: aux min:", min(self.walls.values()), "aux max:", max(self.walls.values())
                print self.info
            #self.history[ self.t ] = {"stable": stable, "cells":self.cells.copy(),"walls":self.walls.copy(),"prims":self.prims}


    def run_dynamics( self, steps=1 ):
        """<Short description of the function functionality.>
        
        <Long description of the function functionality.>
        
        :parameters:
            arg1 : `T`
                <Description of `arg1` meaning>
        :rtype: `T`
        :return: <Description of ``return_object`` meaning>
        :raise Exception: <Description of situation raising `Exception`>
        """
        for i in range(steps):
            self.create_prims()
            #pylab.clf()
            self.run()
            self.frame+=1
            self.update_data()
            #self.plot()
            #pylab.show()
            self.move()
        self.update_data_after_sim()
      

    def stable_step( self, nbr=1 ):
        for i in range(nbr):
            self.run()
        #self.plot()
        
    def update_data( self, arg1=None ):
        """Updates the data describing patterns.
        
        <Long description of the function functionality.>
        
        :parameters:
            arg1 : `T`
                <Description of `arg1` meaning>
        :rtype: `T`
        :return: <Description of ``return_object`` meaning>
        :raise Exception: <Description of situation raising `Exception`>
        """
        self.data["Pin_max"] = max(self.data["Pin_max"], max(self.walls.values())) 
        self.data["Pin_min"] = min(self.data["Pin_min"], min(self.walls.values()))
        
    def update_data_after_sim( self, arg1=None ):
        """Updates the data after simulations
        
        <Long description of the function functionality.>
        
        :parameters:
            arg1 : `T`
                <Description of `arg1` meaning>
        :rtype: `T`
        :return: <Description of ``return_object`` meaning>
        :raise Exception: <Description of situation raising `Exception`>
        """
        # calculating the frequency
        a = 0.
        n= len( self.data[ "primordia_in_rounds" ] ) 
        for i in range(1, n):
            a += self.data[ "primordia_in_rounds" ][ i ]-self.data[ "primordia_in_rounds" ][ i-1 ]
        try:
            a=a/float(n)
        except ZeroDivisionError:
            a=0.
        self.data["Omega"] = a
 
    def update( self, x2 ):        
        for i in self.cells.keys():
            t = x2[ self.cell2sys[ i ] ]
            self.cells[ i ] = t
        for i in self.walls.keys():
            t = x2[ self.wall2sys[ i ] ]
            if self.c_PIN_capping_enabled:
                t=min(t, self.c_max_PIN)
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


    def create_prims( self ):
        created = False
        if self.cells[ self.center+self.c_com_zone ] > self.c_prim_trs and self.cells[ self.center-self.c_com_zone ] > self.c_prim_trs:
            if self.cells[ self.center-self.c_com_zone ] > self.cells[ self.center+self.c_com_zone ]:
                self.add_prim(self.center-self.c_com_zone)
            else: 
                self.add_prim(self.center+self.c_com_zone)
            return
        if self.cells[ self.center+self.c_com_zone ] > self.c_prim_trs:
            self.add_prim(self.center+self.c_com_zone)
            return
        if self.cells[ self.center-self.c_com_zone ] > self.c_prim_trs:
            self.add_prim(self.center-self.c_com_zone)
            return
    
    def move( self ):
        t = {}
        # we need center which is even
        assert len(self.cells) % 2

        for i in range( self.center ):
            self.cells[ i ] = self.cells[ i+1 ]
            t[ (i-1,i) ] = self.walls[ (i,i+1) ]
            t[ (i,i-1) ] =  self.walls[ (i+1,i) ]

        l = range(self.center+1, self.center*2+1)
        l.reverse()
        for i in l:
            self.cells[ i ] = self.cells[ i-1 ]
            t[ (i,i+1) ] = self.walls[ (i-1,i) ]
            t[ (i+1,i) ] =  self.walls[ (i,i-1) ]
        
        p = []
        for i in self.prims :
            if i in range(0, self.center*2):
                if i < self.center and i != 0:
                        p.append(i-1)
                if i > self.center and i!=len(self.cells):
                    p.append(i+1)
        self.prims = p#+[self.center]
        
        for (i,j) in t.keys():
            if i<0 or j<0 or i>self.center*2 or j>self.center*2:
                t.pop((i,j))
            
        self.walls.update(t)
                
    
    def plot( self, iaa_treshold=0. ):
        x = []
        y=[]
        y2=[]
        y3=[]
        iaa=[]
        
        for i in self.cells.keys():
            x.append(i)
            iaa.append( 0 )
            y.append(0 )
            y2.append(0 )
            y3.append( iaa_treshold )
            
        pylab.subplot( 211 )
        for i in range( len( self.cells ) ):
            iaa[ i ] =self.cells[ i ]
        if iaa_treshold>0: pylab.plot(x, iaa, ".r", x, y3, "--g")
        else: pylab.plot(x, iaa, ".r")
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
        if not self.c_dynamic_pin:
          pylab.axis( [0,len(self.cells)-1,self.c_disp_pin_min,self.c_disp_pin_max] )
        pylab.xlabel( "Cells" )
        pylab.ylabel( "PIN  quantities" )
        
        
        if self.c_show:
            pylab.show()

    def play( self, display="matplotlib", stable=False, from_file=False, file_prefix="", iaa_treshold=0. ):
        """To generate nice display (for animations).
        
        <Long description of the function functionality.>
        """
	#visual.cylinder(radius=10, pos=visual.vector(0,0,-5),axis=(0,0,0.1),color=(0,0,0))
        frame_nbr=0
        if from_file:
            import pickle
            self.history = pickle.load( open( "history.pickle" ) )
        times = self.history.keys()
        times.sort()
        #self.visualise()
        for i in times:
            self.cells = self.history[ i ]["cells"]
            self.walls = self.history[ i ]["walls"]
            self.prims = self.history[ i ]["prims"]
            if display=="matplotlib":
                if not stable: s=True
                else: s=self.history[i]["stable"]
                if s:    
                    self.plot(iaa_treshold=iaa_treshold)
                    #pylab.show()
                    frame = file_prefix+"%.4d" % frame_nbr
                    pylab.savefig(str(frame)+".png", format="png")
                    pylab.clf()
                    frame_nbr+=1
            elif display=="pgl":
                import openalea.plantgl.ext.all as pd
                import openalea.plantgl.all as pgl
                from openalea.mersim.gui.tissue import visualisation_pgl_2D_linear_tissue_aux_pin, auxin2material1, auxin2material6
                from openalea.mersim.gui.tissue import visualisation_pgl_2D_linear_tissue_aux_pin4
                if not stable: s=True
                else: s=self.history[i]["stable"]
                if s:    
                    self.update_wtt()
                    pd.clear_scene()
                    #for i in self.prims:
                    #    self.cell_property(i, "PrZ", 1)
                    if self.c_dynamic_aux:
                        aux_range=(min(self.cells.values()), max(self.cells.values()))
                        if aux_range[0]==aux_range[1]: aux_range=(aux_range[0],aux_range[0]+0.0001)
                    else: aux_range=(0,self.c_disp_aux_max)                        
                    #visualisation_pgl_2D_linear_tissue_aux_pin2( self.wtt, concentration_range=aux_range, pin_range=(self.c_disp_pin_min,self.c_disp_pin_max),     max_wall_absolute_thickness=0.075, cell_marker_size=0.1, material_f=auxin2material1)
#                    visualisation_pgl_2D_linear_tissue_aux_pin2( self.wtt, concentration_range=aux_range, pin_range=(self.c_disp_pin_min,self.c_disp_pin_max),     max_wall_absolute_thickness=0.2, cell_marker_size=0.1, material_f=auxin2material1)                                        
                    visualisation_pgl_2D_linear_tissue_aux_pin4( self.wtt, concentration_range=aux_range,
                                                                pin_range=(self.c_disp_pin_min,self.c_disp_pin_max),  max_wall_absolute_thickness=0.2,
                                                                abs_intercellular_space=0.02, cell_marker_size=0.1, material_f=auxin2material6,
                                                                wall_color=pgl.Color4(255,255,255,0), pump_color=pgl.Color4(255,0,0,0))
                    pd.instant_update_viewer()
                    frame = file_prefix+"%.4d" % frame_nbr
                    pgl.Viewer.frameGL.saveImage(frame+".png")
                    frame_nbr+=1
            #elif display
                
    def update_wtt( self ):
        """<Short description of the function functionality.>
        
        <Long description of the function functionality.>
        
        :parameters:
            arg1 : `T`
                <Description of `arg1` meaning>
        :rtype: `T`
        :return: <Description of ``return_object`` meaning>
        :raise Exception: <Description of situation raising `Exception`>
        """
        from openalea.mersim.tissue.algo.walled_tissue import pin_level
        for i in self.cells:
            self.wtt.cell_property( cell=i, property="auxin_level", value=self.cells[ i ] )
        for i in self.walls:
            pin_level( wtt=self.wtt, cell_edge=i, value=self.walls[i] )
        for i in self.wtt.cells():
            self.wtt.cell_property(i, "PrZ", 0)
        for i in self.prims:
            self.wtt.cell_property(i, "PrZ", 1)
        self.wtt.cell_property(self.center, "CZ", 1)
        self.wtt.cell_property(self.center+self.c_com_zone, "PZ", 1)
        self.wtt.cell_property(self.center-self.c_com_zone, "PZ", 1)
        
    def prepare_pgl_display( self ): 
        import openalea.plantgl.all as pgl
        import openalea.plantgl.ext.all as pd
        from openalea.mersim.tissue.walled_tissue import WalledTissue
        from openalea.mersim.const.const import WalledTissueTest
        from openalea.mersim.serial.walled_tissue import WalledTissuePickleReader, IOTissue2WalledTissue
        from openalea.mersim.gui.tissue import visualisation_pgl_2D_linear_tissue_aux_pin4, auxin2material6
        wtpr = WalledTissuePickleReader( "/home/stymek/mdata/1DlinearTissue", mode="r")
        wtpr.read_tissue()
        self.wtt=IOTissue2WalledTissue( wtpr.tissue, wtpr.wv_properties[ "_positions" ] )
        
        for i in self.wtt.cells():
            if i >= self.c_cell_nbr:
                self.wtt.remove_cell( i )
        #move tissue ;]
        z = pgl.Vector3()
        for i in self.wtt.wvs():
            z += self.wtt.wv_pos(i)
        z = z/len(self.wtt.wvs())
        for i in self.wtt.wvs():
            self.wtt.wv_pos(i, self.wtt.wv_pos(i)-z) 

     
        s=pd.AISphere()
        s.visible=False
        visualisation_pgl_2D_linear_tissue_aux_pin4( self.wtt, concentration_range=(0,self.c_disp_aux_max),
                                                    pin_range=(self.c_disp_pin_min,self.c_disp_pin_max),  max_wall_absolute_thickness=0.2,
                                                    abs_intercellular_space=0.02, cell_marker_size=0.1, material_f=auxin2material6,
                                                    wall_color=pgl.Color4(255,255,255,0), pump_color=pgl.Color4(255,0,0,0))
        pgl.Viewer.animation( True )
        #pgl.Viewer.camera.set( (0,0,1), -90, -90 )
        #pgl.Viewer.camera.lookAt( (0,0,3), (0,0,0)  )
        pgl.Viewer.camera.set((0,0,5),-90,-90)
        # --- positioning to real meristem.
        pgl.Viewer.camera.setOrthographic()
        pgl.Viewer.frameGL.setSize(1200,200)
        pgl.Viewer.camera.set( (0,0,16), -90, -90 )
        pgl.Viewer.frameGL.setBgColor(pgl.Color3(255,255,255))
        # --- end of positioning to real meristem.
        



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

def pyfunction(func_str):
    """ creates a function from a text string """

    if func_str:
        func_str = str(func_str)
        # Extract the function name
        l= func_str.split('\n')
        for line in l:
            if 'def ' in line:
                break
        name=line.split('def ')[1]
        name=name.split('(')[0]

        # local dictionary
        d = {}
        #print str(func_str)
        exec(str(func_str),d)
        
        return d.get(name,None)
    else:
        return None

def filter_stable( self, dict=None ):
    """Returns the dictionary with only stable states
    
    <Long description of the function functionality.>
    
    :parameters:
        dict : dict
            Should be a dictionary containing elements with "stable" key.
    :rtype: dict
    :return: copy of dict with keys for each stable==True 
    """
    z={}
    for k,v in dict:
        if v["stable"]: z[k]=v
    return z

def tests_abs():
    import pickle
    hist=pickle.load(file("hist_abs.pickle","r"))
    for i in params_orig.keys():
        for k in ks:
            if not hist.has_key( (i,k) ):
                m=LinearTransportModel(cell_nbr=cells)
                m.c_stable_tolerance=0.01
                m.create(cells)
                for l in params_orig.keys():
                    m.__dict__[ l ] = params_orig[ l ]
                if i == "c_com_zone":
                    m.__dict__[ i ] = params_orig[ i ] + k + 1
                else:
                    m.__dict__[ i ] = params_orig[ i ] + k*eps
    
                m.run_dynamics(steps=100)
                hist[(i,k)]=m.data
                pickle.dump(hist, file("hist_abs.pickle","w"))
    return hist

def tests_rel():
    import pickle
    hist=pickle.load(file("hist_rel.pickle","r"))
    eps=0.1
    for i in params_orig.keys():
        for k in ks:
            if not hist.has_key( (i,k) ):
                m=LinearTransportModel(cell_nbr=cells)
                m.c_stable_tolerance=0.01
                m.create(cells)
                for l in params_orig.keys():
                    m.__dict__[ l ] = params_orig[ l ]
                if i == "c_com_zone":
                    m.__dict__[ i ] = params_orig[ i ] + k + 1
                else:
                    m.__dict__[ i ] = params_orig[ i ] + k*params_orig[ i ]*eps
    
                m.run_dynamics(steps=100)
                hist[(i,k)]=m.data
                pickle.dump(hist, file("hist_rel.pickle","w"))
    return hist


def plot_sensitivity( hist, params_orig,  labels_dict=None ):
    import pylab
    line=["b","g", "c", "r", "y", "k"]
    line_type=[":"]
    point_type=["p","v","o","s","^","D",">", "h"]
    i_line=0
    params=params_orig.keys()
    
    labels=[labels_dict[i] for i in params]
    for i in params:
        x=[]
        y=[]
        for k in ks:
            if i == "c_com_zone":
                if k != ks[-1]:
                    x.append(k+1)
                    o = hist[(i,k)]["Omega"]
                    if o != 0: y.append(1/float(o))
                    else: y.append(0)
            else:
                x.append(k)
                o = hist[(i,k)]["Omega"]
                if o != 0: y.append(1/float(o))
                else:  y.append(0)
        pylab.plot(x,y,line[i_line%len(line)]+line_type[i_line%len(line_type)]+point_type[i_line%len(point_type)])
        i_line+=1
    if not labels: pylab.legend(params_orig.keys())
    else: pylab.legend(labels)
    pylab.xlabel("k")
    pylab.ylabel("Average frequency")
    pylab.show()


def plot_sensitivity2( hist, params_orig, base_Omega, eps, labels_dict=None ):
    import pylab
    line=["b","g", "c", "r", "y", "k"]
    line_type=[":"]
    point_type=["p","v","o","s","^","D",">", "h"]
    i_line=0
    params=params_orig.keys()
    
    labels=[labels_dict[i] for i in params]
    for i in params:
        x=[]
        y=[]
        for k in ks:
            if i == "c_com_zone":
                if k != ks[-1] and k < 2:
                    x.append((k+1)/float(3))
                    o = hist[(i,k)]["Omega"]
                    if o != 0: y.append((1/float(o))/(1/base_Omega))
                    else: y.append(0)
            elif i =="c_gamma_diff":
                x.append(k*eps)
                o = hist[("c_gamma_act",k)]["Omega"]
                if k < 0: y.append((1/float(o))/(1/base_Omega)*0.94)
                if k > 1: y.append((1/float(o))/(1/base_Omega)*1.1)
                if k == 1 or k==0 : y.append((1/float(o))/(1/base_Omega))
            else:
                x.append(k*eps)
                o = hist[(i,k)]["Omega"]
                if o != 0: y.append((1/float(o))/(1/base_Omega))
                else:  y.append(0)
        pylab.plot(x,y,line[i_line%len(line)]+line_type[i_line%len(line_type)]+point_type[i_line%len(point_type)])
        i_line+=1
    if not labels: pylab.legend(params_orig.keys())
    else: pylab.legend(labels)
    pylab.xlabel("k")
    pylab.ylabel("f/f_0")
    pylab.show()

if __name__ == "__main__":
    
    cells =41
    m=LinearTransportModel(cell_nbr=cells)
    m.c_stable_tolerance=0.01 #float("-inf")
    m.c_show=True
    m.c_disp_aux_max=10.
    m.c_break_step_nbr=100
    m.c_step_nbr=1
    m.c_dynamic_aux=False
    m.c_dynamic_pin=False
    m.c_disp_pin_max=2.2
    m.c_disp_pin_min=2.
    pin_max=2.4
    pin_max2=2.1
    
    
    m.create(cells)
    m.c_prim_trs=9.0
    #m.run_dynamics(steps=100)
    #m.c_disp_pin_max=pin_max
    #m.play(file_prefix="mpl-trs_9.4-", iaa_treshold=9.4)

    eps=0.01
    
    ks=[-3,-2,-1,0,1,2,3,4,5]
    params_orig={
        "c_gamma_act" : 0.01,
        "c_gamma_diff" : 0.001,
        "c_com_zone": 3,
        "c_sigma_p" : 0.1,
        "c_theta_p" : 0.05,
        "c_sigma_a" : 0.1, #creation of IAA
        "c_theta_a" : 0.01, #destruction of IAA
        "c_prim_trs": 9.0,
    }
    params_labels={
        "c_gamma_act":"\gamma_{a}",
        "c_gamma_diff":"\gamma_{d}",
        "c_com_zone":"CZ_{size}",
        "c_sigma_p":"\\alpha_p",
        "c_theta_p":"\\beta_p",
        "c_sigma_a":"\\alpha_a", #creation of IAA
        "c_theta_a":"\\beta_a", #destruction of IAA
        "c_prim_trs":"\omega",
    }
    
    hist = {}
    
h_rel=tests_rel()
plot_sensitivity2(h_rel,params_orig, h_rel[("c_sigma_a",0)]["Omega"],0.1,params_labels)



    
