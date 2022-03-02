#!/usr/bin/env python
"""Simulation of pumps reproduction using canalization,
with equations with dimensions and parameters accquired
from real mesurements.

<Long description of the module functionality.>

:todo:
    Nothing.

:bug:
    None known.
    
:organization:
    INRIA

"""
# Module documentation variables:
__authors__="""Szymon Stoma    
"""
__contact__=""
__license__="Cecill-C"
__date__="<Timestamp>"
__version__="0.1"
__docformat__= "restructuredtext en"
__revision__="$Id: 08-05-29-real,marianne01,can,simulation.py 7875 2010-02-08 18:24:36Z cokelaer $"

from openalea.mersim.physio.influence_zones import set_property_on_tissue_component
from openalea.mersim.tissue.algo.walled_tissue import pin_level, pyfunction, calculate_cell_surface, calculate_wall_length
from openalea.mersim.gui.tissue import f_property2material
from openalea.mersim.const.const import TissueConst
from openalea.mersim.serial.walled_tissue import  read_walled_tissue
import openalea.plantgl.all as pgl
import  openalea.plantgl.ext.all as pd
from openalea.mersim.gui.tissue import auxin2material5, auxin2material6, mark_regions5
from openalea.mersim.gui.tissue import  visualisation_pgl_2D_linear_tissue_aux_pin2
from openalea.mersim.physio.canalisation import PhysAuxinTransportModel
from openalea.mersim.tissue.algo.walled_tissue import cell_edge2wv_edge
import scipy

const=TissueConst()
const.cell_properties ={
        "PrC": 0,
        "auxin_level": 0,
        "PrZ": 0,
        "CZ":0,
        "PZ":0,
    }
const.wv_edge_properties={
        "pin_level":[0,0],
}
const.tissue_properties={}

visualisation_conf={"concentration_range":[0,8],
                    "pin_range":[0.1,0.12],
                    "max_wall_absolute_thickness":0.9,
                    "cell_marker_size":0.8,
                    "abs_intercellular_space":0.2,
                    "revers":False,
                    "material_f":auxin2material5,
                    "prefix":"",
                    "prim_cells_with_pin": True,
                    "f_mark_regions": mark_regions5
}

# reading tissue
path="/home/stymek/mdata/08-05-21-marianne01/"
wt_filename="/home/stymek/mdata/08-05-21-marianne01-mersim/"


class TissueSystem(object):
    def __init__(self, tissue):
        self.tissue = tissue

def visualisation( tissue, conf, **keys ):
    pd.SCENES[ 0 ].clear()
    visualisation_pgl_2D_linear_tissue_aux_pin2( tissue, concentration_range=conf["concentration_range"],
                                                pin_range=conf["pin_range"], max_wall_absolute_thickness=conf["max_wall_absolute_thickness"],
                                                cell_marker_size=conf["cell_marker_size"], abs_intercellular_space=conf["abs_intercellular_space"],
                                                material_f=conf["material_f"], revers=conf["revers"],
                                                prim_cells_with_pin=conf["prim_cells_with_pin"],
                                                f_mark_regions=conf["f_mark_regions"], **keys)


class Phys(PhysAuxinTransportModel):
    """Model with correct resolution using scipy.
    
    The target is to check pin realocation model and its influance on the overal behaviour.
    
    """

    def __init__(self, tissue_system = None):
        PhysAuxinTransportModel.__init__( self, tissue_system=tissue_system)
        self.system = tissue_system

        ########################################################
        #### equation constants
        self.c_sigma_a = 0.1 # mumol.mum-3.s-1 : creation of IAA
        self.c_theta_a = 0.01 # s-1 : destruction of IAA
        self.c_theta_a_prim=0.0
        self.c_gamma_act = 0.1  #mumol.mum-2.s-1 : active flux coef.
        self.c_iaa_act_enabled=True
        self.c_gamma_diff = 0.05 # mumol.mum-3.s-1 : diffusion coef.
        self.c_iaa_diff_enabled=True
        self.c_sigma_p = 0.01 # mumol.mum-2.s-1 : creation of PIN
        self.c_theta_p = 0.1 # s-1 : destruciton of PIN
        self.c_iaa_init_val= 0. # mumol.mum-3 : iaa initial value for *normal* cell is computed: v = c_iaa_init_val*(1+random()*c_iaa_init_rand_fact)
        self.c_iaa_init_rand_fact= 0. # look above
        self.c_prim_iaa_conc = 0. # mumol.mum-3 : the concentration of IAA in the primordium (kept fixed)
        self.c_pin_init = self.c_sigma_p/self.c_theta_p # mumol.mum-2 : pin initial value
        self.c_phi_str = """def Phi( x ):
                                            if x < 0:
                                                return 0
                                            return 0.11*x"""
        self.f_phi = pyfunction( self.c_phi_str )
        self.c_PIN_capping_enabled=True
        self.c_max_PIN=2.
        self.c_sink_fixed_concentration=True
        self.c_sink_destruction_rate=0.1
        #### meristem geometry constants
        self.c_prim_trs = 11.0
        self.c_com_zone = 10
        
        #### computation constants
        self.t = 0
        self.h = 1.
        self.c_step_nbr = 1 # nbr of stable step in a run procedure
        self.c_break_step_nbr=1 # if stable step is not found we break after this number of steps
        self.c_stable_tolerance=float("-inf")#0.001 # the change of auxin in each cell must be below this value to call a step stable
        self.c_rtol = 0.1 # relative tolerance accepted by ODE solver
        self.c_atol = 0.1 # absolute tolerance accepted by ODE solver
        self.c_new_simulation = False # start new simulation every run
        self.c_primordium_fade_out_time = 200 #the time required for primordium to disapear
        self.c_primordium_fade_out_conc_max = 4.

        #### display constants
        self.c_disp_aux_max = 5
        self.c_show=True
        self.c_disp_pin_max= 0.2
        self.c_disp_pin_min=0.1
        self.c_dynamic_pin=False
        self.c_dynamic_aux=True
        
        self.nbr_prim=2
        self.frame=0
        
        self.create()
        

    def stable_step( self, nbr=1 ):
        for i in range(nbr):
            self.run()        

    def create( self ):
        self.init_aux()
        self.init_pin()
        self.prepare_sys_map()


    def run( self ):
        if self.c_new_simulation:
            self.create( )
        self.prepare_sys_map()
        for i in range( self.c_step_nbr):
            stable = False
            i = 0
            while not stable and i < self.c_break_step_nbr:
                print i, self.t
                i+=1
                (res,self.info)= scipy.integrate.odepack.odeint( self.f, self.prepare_x0(), [self.t, self.t+self.h], rtol=self.c_rtol, atol=self.c_atol,  full_output=1 )
                self.t += self.h                
                stable = self.rate_error( res[0], res[1])
                self.update( res[1] )
                y=[]
                z = 0
                # quantitie
                for j in self.cell2sys:
                    y.append(res[1][ self.cell2sys[ j ] ] )
                    z +=  res[1][ self.cell2sys[ j ] ] 
                print "  #: aux qua avg: ", z/len( self.tissue_system.tissue.cells() ), "aux con min:", min(y), "aux con max:", max(y)
                y2=[]
                z2=0
                for j in self.wall2sys:
                    y2.append(res[1][ self.wall2sys[ j ] ] )
                    z2 +=  res[1][ self.wall2sys[ j ] ]
                print "  #: pin qua avg: ", z2/len( y2 ), "pin qua min:", min(y2), "pin qua max:", max(y2)
                print self.info
            if not stable:
                print "  #: stable not reached.. breaking."

    
    def update( self, x ):
        t = self.system.tissue
        for i in t.cells():
            t0 = x[ self.cell2sys[ i ] ]
            #t0 = min(self.c_aux_max, max(0,t0) )
            self.aux( cell=i, value= t0)
        for i in t.cell_edges():
            (c1,c2)=i
            t1=x[ self.wall2sys[ (c1,c2) ] ]
            t2=x[ self.wall2sys[ (c2,c1) ] ]
            if self.c_PIN_capping_enabled:
                t1 = min( t1,self.c_max_PIN)
                t2 = min( t2,self.c_max_PIN)
            self.pin( cell_edge=(c1,c2), value=t1 )
            self.pin( cell_edge=(c2,c1), value=t2 )        
    

    def rate_error( self, xn, xnprim ):
        max = -float("infinity")
        for c in self.tissue_system.tissue.cells():
            i = self.cell2sys[ c ]
            if abs( xn[i] - xnprim[i] )> max:
                max=abs( xn[i] - xnprim[i] )
        print " #: max con diff between last steps =  ", max# abs( xn[i] - xnprim[i] )
        return self.c_stable_tolerance > max

    def prepare_x0( self ):
        x0 = []
        t = self.system.tissue
        for x in range( len(t.cells()) + len( 2*t.cell_edges() ) ):
            x0.append(0)
        for i in t.cells():
            x0[ self.cell2sys[ i ] ] = self.aux( i )
            #self.cell2surface[  i  ] = calculate_cell_surface( t, cell=i )
        for i in t.cell_edges():
            (s,t)=i
            x0[ self.wall2sys[ (s,t) ] ] = self.pin( cell_edge=(s,t) )
            x0[ self.wall2sys[ (t,s) ] ] = self.pin( cell_edge=(t,s) )
        return x0

    

    def prepare_x0( self ):
        x0 = []
        t = self.system.tissue
        for x in range( len(t.cells()) + len( 2*t.cell_edges() ) ):
            x0.append(0)
        for i in t.cells():
            x0[ self.cell2sys[ i ] ] = self.aux( i )
            self.cell2surface[  i  ] = calculate_cell_surface( t, cell=i )
        for i in t.cell_edges():
            (s,t)=i
            x0[ self.wall2sys[ (s,t) ] ] = self.pin( cell_edge=(s,t) )
            x0[ self.wall2sys[ (t,s) ] ] = self.pin( cell_edge=(t,s) )
        return x0

    def prepare_sys_map( self ):
        self.cell2sys = {}
        self.wall2sys = {}
        self.error_tol = []
        self.cell2surface = {}
        self.cell_edge2wall_length = {}
        self.cell2overall_wall_length = {}
        t = self.system.tissue
        ind = 0
        for i in t.cells():
            self.cell2sys[ i ] = ind
            #self.error_tol.append( self.c_aux_tol )
            self.cell2surface[ i ] = calculate_cell_surface( t, cell=i )
            ind += 1
            self.cell2overall_wall_length[ i ] = 0

        for (x,y) in t.cell_edges():
            #(s,t) = i
            self.wall2sys[ (x,y) ] = ind
            #self.error_tol.append( self.c_pin_tol )
            ind += 1
            self.wall2sys[ (y,x) ] = ind
            #self.error_tol.append( self.c_pin_tol )
            ind += 1
            wl = calculate_wall_length( t, wv_edge= cell_edge2wv_edge( t, (x,y) ) )
            self.cell_edge2wall_length[ (x,y) ] =  wl
            self.cell_edge2wall_length[ (y,x) ] =  wl
            self.cell_edge2wall_length[ (x,y) ] =  wl
            self.cell_edge2wall_length[ (y,x) ] =  wl
            self.cell2overall_wall_length[ x ] +=  wl
            self.cell2overall_wall_length[ y ] +=  wl
            
    def f( self, x, t ):
        def P( wid, t, x):
            return x[ self.wall2sys[ wid ] ] 

        def D( (i, j), t, x):
            return (A(i,t,x)-A(j,t,x))
        
        def J( (i, j), t, x):
            t=0.
            if self.c_iaa_diff_enabled:
                t += self.c_gamma_diff*(A(i,t,x)-A(j,t,x))
            if self.c_iaa_act_enabled:    
                t += self.c_gamma_act*(-A(j,t,x)*P((j,i),t,x)+A(i,t,x)*P((i,j),t,x))
            return W((i,j))*t
        
        def A( cid, t, x ):
            return x[ self.cell2sys[ cid ] ]
        
        def S( i ):
            return self.cell2surface[ i ]
        
        def W( (i,j) ):
            return self.cell_edge2wall_length[ (i,j) ]
        
        t = self.tissue_system.tissue

        x2 = len(x)*[0.]
        
        for i in t.cells():
            #x2[ self.cell2sys[ i ] ]=0
            if not self.i_local_evacuate( i ):
                x2[ self.cell2sys[ i ] ] = self.c_sigma_a - (self.c_theta_a+self.i_center_evacuate( i )*self.c_theta_a_prim)*A(i,t,x) 
                for n in t.cell_neighbors(i):
                    x2[ self.cell2sys[ i ] ] += J((n,i),t,x)/S(i) #- J((i,n),t,x)
                    
            elif not self.c_sink_fixed_concentration:
                x2[ self.cell2sys[ i ] ] = self.c_sigma_a - (self.c_theta_a+self.c_sink_destruction_rate)*A(i,t,x) 
                for n in t.cell_neighbors( cell=i ):
                    x2[ self.cell2sys[ i ] ] += J((n,i),t,x)/S(i) #- J((i,n),t,x)                    
        for (i,j) in t.cell_edges():
            x2[ self.wall2sys[(i,j)] ] = self.f_phi(J((i,j),t,x)/W((i,j)))+self.c_sigma_p-self.c_theta_p*P((i,j),t,x)
            x2[ self.wall2sys[(j,i)] ] = self.f_phi(J((j,i),t,x)/W((i,j)))+self.c_sigma_p-self.c_theta_p*P((j,i),t,x)
        return x2
    
    def i_local_evacuate( self, cell ):
        t = self.system.tissue
        if t.cell_property( cell=cell, property="PrC") or t.cell_property( cell=cell, property="PrZ") > 0:
        #if self.h_prim_cells[ cell ]:
            return 1
        else:
            return 0
        
    def i_center_evacuate( self, cell ):
        t = self.system.tissue
        if t.cell_property( cell=cell, property="CZ") > 0:
        #if self.h_centre_cells[ cell ]:
            return 1
        else:
            return 0
        
    def init_aux(self):
        t = self.system.tissue
        for c in t.cells():
            self.aux(cell= c, value= self.c_iaa_init_val ) #+random.random() )
            if self.i_local_evacuate( c ):
                self.aux(cell= c, value= 0. ) #+random.random() )

    def init_pin( self ):
        t = self.system.tissue
        for (i,j) in t.cell_edges():
            self.pin( (i,j), self.c_pin_init )
            self.pin( (j,i), self.c_pin_init )

    def search_for_primodium( self ):
        t = self.system.tissue
        pc = []
        for c in t.cells():
            if t.cell_property( cell=c, property="PZ"):
                if self.aux( cell = c ) > self.c_prim_trs:
                    pc.append( c )
        return pc
        
    def create_primordiums( self, primordium_cand=None):
        t = self.system.tissue
        if len(primordium_cand)>0:
            primordium_cand.sort( lambda x, y: cmp( self.aux( cell = y ),  self.aux( cell = x ) ))
            c = primordium_cand[ 0 ]
            t.cell_property( cell=c, property="PrC", value=self.nbr_prim)
            t.cell_property( cell=c, property="PrZ", value=self.nbr_prim)
            t.tissue_property( property="prim2creation_time")[ self.nbr_prim ]= self.t
            t.tissue_property( property="prim2creation_pos")[ self.nbr_prim ]= cell_center( t, c )
            for n in t.cell_neighbors( c ):
                t.cell_property( cell=n, property="PrZ", value=self.nbr_prim)
            self.nbr_prim+=1
            #self.step()


# reading tissue.
t = read_walled_tissue( file_name=wt_filename, const=const )


#viewer settings
pd.set_instant_update_visualisation_policy( policy = False )
pgl.Viewer.animation( True )
pgl.Viewer.frameGL.setSize(900,900)
pgl.Viewer.frameGL.setBgColor(pgl.Color3(255,255,255))
pgl.Viewer.camera.setOrthographic()
pgl.Viewer.light.enabled=False
pgl.Viewer.display(pd.SCENES[0])     
pgl.Viewer.camera.lookAt( (0,0,-140), (0,0,0) )
# visulaization of tissue


system=TissueSystem(t)
phys = Phys(tissue_system=system)
#phys.init_pin()
#phys.init_aux()
#
#for i in range(10):
#    phys.stable_step()

visualisation(t, visualisation_conf)

