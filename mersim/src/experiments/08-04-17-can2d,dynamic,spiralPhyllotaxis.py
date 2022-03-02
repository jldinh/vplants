#!/usr/bin/env python
"""<Short description of the module functionality.>

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
__revision__="$Id: 08-04-17-can2d,dynamic,spiralPhyllotaxis.py 7875 2010-02-08 18:24:36Z cokelaer $"

from openalea.mersim.tissue.walled_tissue import WalledTissue
from openalea.mersim.const.const import *
from openalea.mersim.tissue.algo.walled_tissue import *
from openalea.mersim.tissue.algo.walled_tissue_division_policies import *
#from openalea.mersim.tissue.algo.walled_tissue_cfd import *
from openalea.mersim.tissue.algo.walled_tissue_dscs import *
from openalea.mersim.serial.walled_tissue import *
from openalea.mersim.gui.tissue import *
from openalea.mersim.physio.canalisation import *
#from openalea.mersim.physio.cell_identities import *
#from openalea.mersim.mass_spring.forces import * 
#from openalea.mersim.mass_spring.system import *
from openalea.mersim.tissue.algo.walled_tissue_division_policies import *
from openalea.mersim.tissue.algo.walled_tissue_dscs import *
from openalea.mersim.tissue.algo.walled_tissue_cfd import ds_surface
from openalea.mersim.simulation.remove_cell_strategy import *
import random

class Phys(PhysAuxinTransportModel):
    """Model with correct resolution using scipy.
    
    The target is to check pin realocation model and its influance on the overal behaviour.
    
    """

    def __init__(self, tissue_system = None):
        PhysAuxinTransportModel.__init__( self, tissue_system=tissue_system)
        self.system = tissue_system

        ########################################################
        #### equation constants
        self.c_sigma_a = 0.1 #creation of IAA
        self.c_theta_a = 0.01 #destruction of IAA
        self.c_theta_a_prim=0.05
        self.c_gamma_act = 0.1 #active flux coef.
        self.c_iaa_act_enabled=True
        self.c_gamma_diff = 0.03 # diffusion coef.
        self.c_iaa_diff_enabled=True
        self.c_sigma_p = 0.01 # creation of PIN
        self.c_theta_p = 0.1 # destruciton of PIN
        self.c_iaa_init_val= 0. # iaa initial value for *normal* cell is computed: v = c_iaa_init_val*(1+random()*c_iaa_init_rand_fact)
        self.c_iaa_init_rand_fact= 0. # look above
        self.c_prim_iaa_conc = 0. # the concentration of IAA in the primordium (kept fixed)
        self.c_pin_init = self.c_sigma_p/self.c_theta_p # pin initial value
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
            #self.cell2surface[ i ] = calculate_cell_surface( t, cell=i )
            #ind += 1
            #self.cell2overall_wall_length[ i ] = 0

        for (x,y) in t.cell_edges():
            #(s,t) = i
            self.wall2sys[ (x,y) ] = ind
            #self.error_tol.append( self.c_pin_tol )
            ind += 1
            self.wall2sys[ (y,x) ] = ind
            #self.error_tol.append( self.c_pin_tol )
            ind += 1
            #wl = calculate_wall_length( t, wv_edge= cell_edge2wv_edge( t, (x,y) ) )
            #self.cell_edge2wall_length[ (x,y) ] =  wl
            #self.cell_edge2wall_length[ (y,x) ] =  wl
            #self.cell_edge2wall_length[ (x,y) ] =  wl
            #self.cell_edge2wall_length[ (y,x) ] =  wl
            #self.cell2overall_wall_length[ x ] +=  wl
            #self.cell2overall_wall_length[ y ] +=  wl
    

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
        if t.cell_property( cell=cell, property="PrC") or t.cell_property( cell=cell, property="PrZ") > 0 or t.cell_property( cell=cell,property="PrC_stub")or t.cell_property( cell=cell,property="PrZ_stub") :
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

class RadialGrowth:
    def __init__(self, tissue=None, center = visual.vector(), c_v0=0.01, c_zone=0.8):
        """RadialGrowth constructor.

        """
        self.center = center
        self.c_czone = c_zone
        self.c_v0 = c_v0
        self.tissue=tissue
    
    def apply( self ):
        for vw in self.tissue.wvs():
            p = self.tissue.wv_pos( vw )
            d = p - self.center
            n = d.normalize()
            self.tissue.wv_pos( vw, p+d*self.c_v0*(n/self.c_czone) )
            
            
            
            
class ContinousPrimsGrowth:
    class Prim:
        def __init__( self, pos, radius ):
            self.pos = pos
            self.radius = radius
            #ts=pd.AISphere()
            #ts.geometry.slices=50
            #ts.visible=False
            #ts=pd.AICylinder()
            #ts.geometry.slices=50
            #ts.visible=False
            
    def __init__( self, profile_f=None, c_remove_radius=5 ):
        self.prims = {}
        self._prim_id = 0
        self.c_initial_radius = 0.2
        self.c_remove_z =profile_f( c_remove_radius )
        self.c_step=0.03
        self.profile_f = profile_f
        
    def add_prim( self, pos ):
        np = pos
        np.z += - self.c_initial_radius 
        self.prims[ self._prim_id ] = ContinousPrimsGrowth.Prim(pos,self.c_initial_radius)
        self._prim_id += 1
        
    def move( self ):
        to_remove = []
        for i in self.prims:
            p = self.prims[ i ]
            if p.pos.z > self.c_remove_z:
                t = pgl.Vector3( p.pos )
                t.z = 0
                n = pgl.norm( t )
                new_z = self.profile_f( n+self.c_step )
                t2 = pgl.Vector3( t )
                t2.normalize()
                t = t+t2*self.c_step
                t.z=new_z
                self.prims[ i ].pos = t
                self.prims[ i ].radius = 0.2-self.prims[ i ].pos.z/10
            else:
                to_remove.append( i )
        for p in to_remove:
            self.prims.pop( p )
        
class PhysMarkCellIdentitiesWithFixedRegionsIn2D_2(PhysInterface):
    """Marking the cell identities basing only on current geometric information.
    
    bigger center zone comparing to PhysMarkCellIdentitiesWithFixedRegionsIn2D_1
    """
    
    def __init__( self, tissue_system=None):
        PhysInterface.__init__( self, tissue_system=tissue_system)
        self.reset_cell_identities()
        self.mark_cell_identities()
    
    def apply( self ):
        self.reset_cell_identities()
        self.mark_cell_identities()
    
    def reset_cell_identities( self ):
        for c in self.tissue_system.tissue.cells():
            self.tissue_system.tissue.cell_property( cell = c, property="IC", value=False)
            self.tissue_system.tissue.cell_property( cell = c, property="CZ", value=False)
            self.tissue_system.tissue.cell_property( cell = c, property="PZ", value=False)
            self.tissue_system.tissue.cell_property( cell = c, property="NZ", value=True)    
            self.tissue_system.tissue.cell_property( cell = c, property="PrZ", value=0)
            self.tissue_system.tissue.cell_property( cell = c, property="PrZ_stub", value=0)
            
    def mark_cell_identities( self ):
        """Sets properties for cell identities. The overal meristem
        identity difision should be clearly defined in conf. Currently they
        are possible regions:
            * initial cell IC(must be already initialized)
            * central zone CZ (closest cells attached to initial zone, aux insensitive)
            * peripheral zone PZ (one more ring after central zone, aux sensitive, can form
            primodium)
            * primodium zone PrZ (attracts pumps)
            * rest of the meristem
        """
        # finding the initial cell
        t=self.tissue_system.tissue
        cc = cell_centers(t)
        center=self.tissue_system.growth.center
        self.reset_cell_identities()
        PZ_distance =self.tissue_system.const.PZ_absolute_dist#0.7 #120#200
        
        CZ=[]
        PZ=[]
        rr = math.sqrt(self.tissue_system.const.cs_surf_max_surface_before_division)/1.2
        min_dist = float("infinity")
        for i in cc:
            mr0 = pgl.norm( cc[ i ] - center )
            if  mr0 < PZ_distance+rr:
                if mr0 < PZ_distance-rr:
                    CZ.append( i )
                    if mr0 < min_dist:
                        IC = i
                        min_dist = mr0
                else:
                    PZ.append( i )

        #self.tissue_system.tissue.cell_property( cell = IC, property="IC", value=True)
        for c in CZ:
            self.tissue_system.tissue.cell_property( cell = c, property="CZ", value=True)
            self.tissue_system.tissue.cell_property( cell = c, property="NZ", value=False)
        for c in PZ:
            self.tissue_system.tissue.cell_property( cell = c, property="PZ", value=True)
            self.tissue_system.tissue.cell_property( cell = c, property="NZ", value=False)
        self.tissue_system.tissue.cell_property( cell = IC, property="IC", value=True)
        self.tissue_system.tissue.cell_property( cell = IC, property="NZ", value=False)
        
        for c in t.cells(): 
            pr_id = self.tissue_system.tissue.cell_property( cell = c, property="PrC")
            if pr_id > 0:
                self.tissue_system.tissue.cell_property( cell = c, property="PrZ", value=pr_id)
                for i in t.cell_neighbors(c):
                    self.tissue_system.tissue.cell_property( cell = i, property="PrZ", value=pr_id)
                        
        for c in t.cells(): 
            pr_id = self.tissue_system.tissue.cell_property( cell = c, property="PrC_stub")
            if pr_id > 0:
                self.tissue_system.tissue.cell_property( cell = c, property="PrZ_stub", value=pr_id)
                for i in t.cell_neighbors(c):
                    self.tissue_system.tissue.cell_property( cell = i, property="PrZ_stub", value=pr_id)

class TissueSystem:
    """Stub tissue system..
    """
    def __init__( self, tissue, const=None ):
        self.tissue = tissue
        self.const=const
        self.phys=Phys(tissue_system=self) #Phys2DcanalisationForDynamicTopView3( tissue_system=self )
        self.growth=RadialGrowth( tissue=self.tissue, center= pgl.Vector3())
        self.cell_remover = SimulationRemoveCellStrategy2D_1( self, c_remove_2d_radius=1.5 )
        self.cell_identities =  PhysMarkCellIdentitiesWithFixedRegionsIn2D_2( tissue_system=self)
        self.cont_prims =ContinousPrimsGrowth( profile_f=(lambda x:(-x*x +2.2*2.2)/4.), c_remove_radius = 5)
        self.frame=0
        self.tissue.time=0
        self.c_save_simulation=True
        self.concentration_range=(5,20)
        self.c_prim_min_con = 0
        self.c_prim_max_con = 2
        self.c_tissue_dir="/home/stymek/mtmp/08-02-28-can2d,dynamic,spiralPhyllotaxis2/"
        #self._primordium_removal_hist={}
    
    def f_factor( self, prim ):
        # returns the concentration in prim acording to its position
        d = cell_center( self.tissue, prim ) - pgl.Vector3()
        f = (pgl.norm( d )/(self.cell_remover.c_remove_2d_radius-self.const.PZ_absolute_dist+math.sqrt(self.const.cs_surf_max_surface_before_division)/1.2) )
        return self.c_prim_min_con+max(0, self.c_prim_max_con*f)
    
    def f_factor_time( self, prim ):
        """returns [0,1] depending on the prim removal time and 
        """
        return (self.phys.t-self.tissue.tissue_property("prim2removal_time")[prim])/self.phys.c_primordium_fade_out_time
    
    def change_conc_in_prim( self ):
        h = {}
        for i in self.tissue.cells():
            if self.tissue.cell_property( i, "PrC" ):
                h[ self.tissue.cell_property( i, "PrC" ) ] = 0.#self.f_factor( i )
        for i in self.tissue.cells():
            if self.tissue.cell_property( i, "PrZ" ):
                self.phys.aux(i, h[self.tissue.cell_property( i, "PrZ" )])

    def change_conc_in_prim_stubs( self ):
        h = {}
        for i in self.tissue.cells():
            if self.tissue.cell_property( i, "PrC_stub" ):
                h[ self.tissue.cell_property( i, "PrC_stub" ) ] = self.f_factor_time( self.tissue.cell_property( i, "PrC_stub" ) )*self.phys.c_primordium_fade_out_conc_max
                for j in self.tissue.cell_neighbors(i):
                    self.phys.aux(j, h[self.tissue.cell_property( i, "PrC_stub" )])

    def run( self , nbr):
        self.phys.c_stable_tolerance=0.01
        self.phys.c_atol=0.001
        self.phys.c_rtol=0.001
        self.phys.c_sigma_a=0.3
        self.phys.c_theta_a=0.03
        self.phys.c_theta_a_prim=0.06
        self.phys.c_gamma_act=0.125
        self.phys.c_break_step_nbr=200
        self.phys.c_step_nbr=1
        self.phys.h=1.
        self.phys.c_prim_trs=6.9
        self.phys.c_primordium_fade_out_conc_max=5
        self.phys.c_primordium_fade_out_time=400
        self.phys.init_aux()
        self.phys.init_pin()
        self.phys.c_dynamic_aux=True
        self.step(nbr)
        
    def run2( self , nbr):
        self.c_tissue_dir="/home/stymek/mtmp/08-02-28-can2d,dynamic,spiralPhyllotaxis2-2/"
        self.phys.c_stable_tolerance=0.01
        self.phys.c_atol=0.001
        self.phys.c_rtol=0.001
        self.phys.c_sigma_a=0.3
        self.phys.c_theta_a=0.03
        self.phys.c_theta_a_prim=0.06
        self.phys.c_gamma_act=0.125
        self.phys.c_break_step_nbr=200
        self.phys.c_step_nbr=1
        self.phys.h=1.
        self.phys.c_prim_trs=6.8
        self.phys.c_primordium_fade_out_conc_max=5
        self.phys.c_primordium_fade_out_time=400
        self.phys.init_aux()
        self.phys.init_pin()
        self.phys.c_dynamic_aux=True
        self.step(nbr)

    def play2( self, folder=""):
        self.c_tissue_dir="/home/stymek/mtmp/08-02-28-can2d,dynamic,spiralPhyllotaxis2-2/"
        if not folder: folder=self.c_tissue_dir
        green_range._position_list=[0.,0.9,1.]
        self.c_dynamic_aux=False
        self.phys.c_disp_aux_max=7.2
        pgl.Viewer.frameGL.setBgColor(pgl.Color3(255,255,255))
        while True:
            self.load_tissue( folder+str(self.frame))
            self.update_visualisation( revers=True, material_f=auxin2material6, pump_color=pgl.Color4(255,0,0,0), wall_color=pgl.Color4(0,0,0,0),
                                      prefix=folder+"/vis/1/")
            self.frame+=1
            
    def save_phyllotactic_data2( self, folder=""):
        from openalea.mersim.tools.phyllotaxis import get_primordia_data
        self.c_tissue_dir="/home/stymek/mtmp/08-02-28-can2d,dynamic,spiralPhyllotaxis2-2/"
        if not folder: folder=self.c_tissue_dir
        d = {"step2PrC":{}, "step2PrC_stub":{}, "cells":{}}
        c = {}
        try:
            while True:
                self.load_tissue( folder+str(self.frame))
                get_primordia_data(wt=self.tissue, step2PrC=d[ "step2PrC" ], step2PrC_stub=d[ "step2PrC_stub" ],
                                            step=self.frame)
                d["cells"][self.frame]=self.tissue.cells()
                self.frame+=1
                #if self.frame > 10: break
        except:
            pass
        import pickle
        pickle.dump(d, file(self.c_tissue_dir+"primHist.dict","w"))

    def play2_center_IAA_conc( self, folder=""):
        self.c_tissue_dir="/home/stymek/mtmp/08-02-28-can2d,dynamic,spiralPhyllotaxis2-2/"
        if not folder: folder=self.c_tissue_dir
        self.center_iaa_conc={}
        while True:
            self.load_tissue( folder+str(self.frame))
            n=0
            s=0.
            for i in self.tissue.cells():
                if self.tissue.cell_property(i, "CZ"):
                    n+=1
                    s+=auxin_level( self.tissue, i )
            self.center_iaa_conc[ self.frame ]=s/n
            self.frame+=1
        
    def disp_aux_cen( self ):
        import pylab
        k = self.center_iaa_conc.keys()
        k.sort()
        x=[]
        y=[]
        for i in k:
            x.append(i)
            y.append(self.center_iaa_conc[ i ])
        pylab.plot(x, y)
        pylab.show()
            
    def run3( self , nbr):
        self.c_tissue_dir="/home/stymek/mtmp/08-02-28-can2d,dynamic,spiralPhyllotaxis2-3/"
        self.phys.c_stable_tolerance=0.01
        self.phys.c_atol=0.001
        self.phys.c_rtol=0.001
        self.phys.c_sigma_a=0.3
        self.phys.c_theta_a=0.03
        self.phys.c_theta_a_prim=0.06
        self.phys.c_gamma_act=0.125
        self.phys.c_break_step_nbr=200
        self.phys.c_step_nbr=1
        self.phys.h=1.
        self.phys.c_prim_trs=7.1
        self.phys.c_primordium_fade_out_conc_max=5
        self.phys.c_primordium_fade_out_time=400
        self.phys.init_aux()
        self.phys.init_pin()
        self.phys.c_dynamic_aux=True
        self.step(nbr)

    def play3( self, folder=""):
        self.c_tissue_dir="/home/stymek/mtmp/08-02-28-can2d,dynamic,spiralPhyllotaxis2-3/"
        if not folder: folder=self.c_tissue_dir
        green_range._position_list=[0.,0.6,1.]
        self.c_dynamic_aux=False
        self.phys.c_disp_aux_max=7.4
        pgl.Viewer.frameGL.setBgColor(pgl.Color3(255,255,255))
        while True:
            self.load_tissue( folder+str(self.frame))
            self.update_visualisation( revers=True, material_f=auxin2material6, pump_color=pgl.Color4(255,0,0,0), wall_color=pgl.Color4(0,0,0,0),
                                      prefix=folder+"/vis/1/")
            self.frame+=1
            
    def save_phyllotactic_data3( self, folder=""):
        from openalea.mersim.tools.phyllotaxis import get_primordia_data
        self.c_tissue_dir="/home/stymek/mtmp/08-02-28-can2d,dynamic,spiralPhyllotaxis2-3/"
        if not folder: folder=self.c_tissue_dir
        d = {"step2PrC":{}, "step2PrC_stub":{}, "cells":{}}
        c = {}
        try:
            while True:
                self.load_tissue( folder+str(self.frame))
                get_primordia_data(wt=self.tissue, step2PrC=d[ "step2PrC" ], step2PrC_stub=d[ "step2PrC_stub" ],
                                            step=self.frame)
                d["cells"][self.frame]=self.tissue.cells()
                self.frame+=1
                #if self.frame > 10: break
        except:
            pass
        import pickle
        pickle.dump(d, file(self.c_tissue_dir+"primHist.dict","w"))
            
    def step( self, nbr=1 ):
        for i in range( nbr ):
            self.tissue.time+=1
            self.cell_identities.apply()
            self.change_conc_in_prim()
            self.change_conc_in_prim_stubs()
            self.phys.run()
            self.phys.create_primordiums(self.phys.search_for_primodium())
            self.update_pin_range()
            self.update_conc_range()
            self.update_visualisation( revers=True, material_f=auxin2material3, pump_color=pgl.Color4(255,0,0,0), wall_color=pgl.Color4(0,0,0,0), prefix=self.c_tissue_dir+"vis/1/")
            self.growth.apply()
            self.write_tissue(self.c_tissue_dir+str(self.frame))
            self.frame+=1
            self.divide_cells()
            self.remove_cells()
            self.cont_prims.move()
        
            
    def write_tissue( self, file_name=None ):
        if not file_name: file_name=self.c_tissue_dir
        wtp = WalledTissuePickleWriter( file_name, mode="w",
                               tissue=WalledTissue2IOTissue(self.tissue, id=IntIdGenerator( self.tissue.wv_edges() )),
                               tissue_properties=WalledTissue2IOTissueProperties( self.tissue  ),
                               cell_properties=WalledTissue2IOCellPropertyList( self.tissue  ),
                               wv_properties=WalledTissue2IOEdgePropertyList( self.tissue ),
                               wv_edge_properties=WalledTissue2IOWallPropertyList( self.tissue, id=IntIdGenerator( self.tissue.wv_edges() ) ),
                               description="Tissue with aux and pin, hexagonal, 3sinks appearing in a raw." )
        wtp.write_all()
        print " #: tissue written.."
        
    def load_tissue( self, file_name=None ):
        #if not file_name: file_name=self.c_tissue_dir
        wtpr = WalledTissuePickleReader( file_name, mode="r")
        wtpr.read_tissue()
        self.tissue=IOTissue2WalledTissue( wtpr.tissue, wtpr.wv_properties[ "_positions" ], const=WalledTissueCanalisationExp1() )
        wtpr.read_property( "auxin_level" )
        wtpr.read_property( "pin_level" )
        wtpr.read_property( "PrC" )
        wtpr.read_property( "PrZ" )
        wtpr.read_property( "CZ"  )
        wtpr.read_property( "PZ"  )
        f_PrC_stub=False
        try:
            wtpr.read_property( "PrC_stub"  )
            f_PrC_stub=True
        except:
            pass
        
        for i in self.tissue.cells():
            self.tissue.cell_property( cell=i, property="auxin_level", value=wtpr.cell_properties[ "auxin_level" ][ i ] )
            self.tissue.cell_property( cell=i, property="PrZ", value=wtpr.cell_properties[ "PrZ" ][ i ] )
            self.tissue.cell_property( cell=i, property="PrC", value=wtpr.cell_properties[ "PrC" ][ i ] )
            self.tissue.cell_property( cell=i, property="CZ", value=wtpr.cell_properties[ "CZ" ][ i ] )
            self.tissue.cell_property( cell=i, property="PZ", value=wtpr.cell_properties[ "PZ" ][ i ] )
            if f_PrC_stub:
                self.tissue.cell_property( cell=i, property="PrC_stub", value=wtpr.cell_properties[ "PrC_stub" ][ i ] )
        #return wtpr #wtpr.wv_edge_properties[ "pin_level" ]
        for i in wtpr.tissue.scale_relations[1]:
            self.tissue.wv_edge_property( wv_edge=tuple(wtpr.tissue.scale_relations[1][i]), property="pin_level", value=wtpr.wv_edge_properties[ "pin_level" ][ i ] )
            


    def play1( self, folder=""):
        if not folder: folder=self.c_tissue_dir
        green_range._position_list=[0.,0.7,1.]
        self.c_dynamic_aux=False
        self.phys.c_disp_aux_max=6.8
        pgl.Viewer.frameGL.setBgColor(pgl.Color3(255,255,255))
        while True:
            self.load_tissue( folder+str(self.frame))
            self.update_visualisation( revers=True, material_f=auxin2material6, pump_color=pgl.Color4(255,0,0,0), wall_color=pgl.Color4(0,0,0,0),
                                      prefix=folder+"/vis/1/")
            self.frame+=1
        

    def update_conc_range( self ):
        l=[]
        for i in self.tissue.cells():
            l.append(self.tissue.cell_property( i , "auxin_level"))
        self.concentration_range = (min(l),max(l))
        
    def update_pin_range( self ):
        l=[]
        min = float("inf")
        max = float("-inf")
        for i in self.tissue.cells():
            for n in self.tissue.cell_neighbors( i ):
                v = pin_level( self.tissue, cell_edge=(i,n))
                if v < min:
                    min = v
                if v > max:
                    max = v
        self.pin_range = (min,max)
        

    def remove_cells( self ):
        l = self.cell_remover.cells_to_remove()
        for i in l:
            if self.tissue.cell_property( cell=i, property="PrC" ):
                cc = cell_center( wt=self.tissue, cell=i )
                dir = pgl.Vector3( cc )
                cc = cc*(2.2/pgl.norm( cc ))
                cc.z = -0.2
                self.cont_prims.add_prim( pos=cc )
                n = self.tissue.cell_neighbors( i )[ 0 ] # take 1st neighbor
                self.tissue.cell_property(n, "PrC_stub", self.tissue.cell_property(i, "PrC"))
                self.tissue.tissue_property("prim2removal_time")[self.tissue.cell_property(i, "PrC")]=self.phys.t
                self.tissue.tissue_property("prim2removal_pos")[self.tissue.cell_property(i, "PrC")]=cell_center(self.tissue, i)
            if self.tissue.cell_property( cell=i, property="PrC_stub" ):
                if self.phys.t - self.tissue.tissue_property("prim2removal_time")[self.tissue.cell_property(i, "PrC_stub")] < self.phys.c_primordium_fade_out_time:
                    n = self.tissue.cell_neighbors( i )[ 0 ] # take 1st neighbor
                    self.tissue.cell_property(n, "PrC_stub", self.tissue.cell_property(i, "PrC_stub"))
            self.tissue.remove_cell( cell=i )

    def mark_prim( self, cell, nbr ):
        self.tissue.cell_property( cell, "PrC", nbr )
        self.tissue.cell_property( cell, "PrZ", 1 )
        self.phys.aux( cell, 0 )
        for i in self.tissue.cell_neighbors( cell ):
            self.tissue.cell_property( i, "PrZ", 1 )
            self.phys.aux( i, 0 )
            
    def divide_cells( self ):
        ds_surface( self.tissue, dscs_shortest_wall_with_geometric_shrinking, pre=pre_4, post=post_4 )
    


    def update_visualisation( self, max_wall_absolute_thickness=0.04, cell_marker_size=0.01,
                             abs_intercellular_space=0.005, revers=True, material_f=auxin2material5,
                             prefix="", **keys ):
        #self.frame+=1
        pd.SCENES[ 0 ].clear()
        self.update_conc_range()
        self.update_pin_range()

        
        if self.phys.c_dynamic_aux: concentration_range=self.concentration_range
        else: concentration_range=(0., self.phys.c_disp_aux_max)
        if self.phys.c_dynamic_pin: pin_range = self.pin_range
        else: pin_range = (self.phys.c_disp_pin_min,self.phys.c_disp_pin_max)
        visualisation_pgl_2D_linear_tissue_aux_pin2( self.tissue, concentration_range=concentration_range, pin_range=pin_range, max_wall_absolute_thickness=max_wall_absolute_thickness,
                                                    cell_marker_size=cell_marker_size,abs_intercellular_space=abs_intercellular_space, material_f=material_f, revers=self.reverse_tissue_if_needed(),
                                                    prim_cells_with_pin=self.phys.c_disp_pin_max, stride=20, f_mark_regions=mark_regions4, **keys)

        pd.instant_update_viewer()
        name = ("%.5d.png") % self.frame
        name = prefix+name
        pgl.Viewer.frameGL.saveImage(name)
        
    def reverse_tissue_if_needed( self ):
        c = self.tissue.cells()[0]
        cwvs = self.tissue.cell2wvs(c)
        cc = cell_center( self.tissue, c)
        #print  (pgl.cross(s.tissue.wv_pos(cwvs[0]) - cc, s.tissue.wv_pos(cwvs[1]) - cc)).z
        return not(0 < (pgl.cross(s.tissue.wv_pos(cwvs[0]) - cc, s.tissue.wv_pos(cwvs[1]) - cc)).z)
        

            
def act2diff(x, pin_max):
    return x.phys.c_gamma_act*(pin_max-x.phys.c_sigma_p/x.phys.c_theta_p)/(x.phys.c_gamma_diff+x.phys.c_gamma_act*x.phys.c_sigma_p/x.phys.c_theta_p)
        
#wtpr = WalledTissuePickleReader( "/home/stymek/mdata/circ,2D", mode="r")
#circ,2d,4cana
wtpr = WalledTissuePickleReader( "/home/stymek/mdata/2d.can,graTo0,pumps-stable", mode="r")
#wtpr = WalledTissuePickleReader( "/home/stymek/src/openalea/mersim/experiments/simulation/s00148", mode="r")
wtpr.read_tissue()
wt3=IOTissue2WalledTissue( wtpr.tissue, wtpr.wv_properties[ "_positions" ], const=WalledTissueCanalisationExp1() )

s=TissueSystem( wt3, const= WalledTissueDynamicCanalisation2() )
s.tissue.const=WalledTissueDynamicCanalisation2()
s.tissue._tissue_properties
s.remove_cells()
pd.ASPHERE_PRIMITIVE.slices=20
s.cell_identities.apply()
s.phys.init_pin()
s.phys.init_aux()
s.update_conc_range()
s.update_pin_range()
s.phys.c_dynamic_aux=False
#s.update_visualisation()
s.const.cell_properties.pop("inh")
s.const.cell_properties.pop("innerSink")
s.tissue.tissue_property("prim2removal_time",{})
s.tissue.tissue_property("prim2creation_time",{})
s.tissue.tissue_property("prim2removal_pos",{})
s.tissue.tissue_property("prim2creation_pos",{})

s.cell_identities.apply()
s.mark_prim(592,1)
s.change_conc_in_prim()
s.update_visualisation( revers=True, material_f=auxin2material3, pump_color=pgl.Color4(255,255,255,0), wall_color=pgl.Color4(0,0,0,0))
pgl.Viewer.animation( True )
pgl.Viewer.camera.lookAt( (0,0,3), (0,0,0) )
pgl.Viewer.camera.setOrthographic()
pgl.Viewer.frameGL.setSize(1200,1200)
s.frame=0
