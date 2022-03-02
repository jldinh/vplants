#!/usr/bin/env python
"""Real meristem running canalisation to get nice PIN-maps fit.

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
__revision__="$Id: 08-03-13-pinDynBiggerCenter.py 7875 2010-02-08 18:24:36Z cokelaer $"

from openalea.mersim.tissue.walled_tissue import WalledTissue
from openalea.mersim.const.const import *
from openalea.mersim.tissue.algo.walled_tissue import *
from openalea.mersim.tissue.algo.walled_tissue_division_policies import *
#from openalea.mersim.tissue.algo.walled_tissue_cfd import *
from openalea.mersim.tissue.algo.walled_tissue_dscs import *
from openalea.mersim.serial.walled_tissue import *
from openalea.mersim.serial.merrysim_plugin import *
from openalea.mersim.gui.tissue import *
from openalea.mersim.physio.canalisation import *
from openalea.mersim.physio.cell_identities import *
#from openalea.mersim.mass_spring.forces import * 
#from openalea.mersim.mass_spring.system import *
from openalea.mersim.tissue.algo.walled_tissue_division_policies import *
from openalea.mersim.tissue.algo.walled_tissue_dscs import *
from openalea.mersim.tissue.algo.walled_tissue_cfd import ds_surface
from openalea.mersim.simulation.remove_cell_strategy import *


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
        self.c_theta_a_prim = 0.08
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
                                            return 0.18*x"""
        self.f_phi = pyfunction( self.c_phi_str )
        self.c_PIN_capping_enabled=True
        self.c_max_PIN=2.
        self.c_sink_fixed_concentration=True
        self.c_sink_destruction_rate=0.1
        #### meristem geometry constants
        self.c_prim_trs = 7.0
        self.c_com_zone = 10
        
        #### computation constants
        self.t = 0
        self.h = 1
        self.c_step_nbr = 1 # nbr of stable step in a run procedure
        self.c_break_step_nbr=1 # if stable step is not found we break after this number of steps
        self.c_stable_tolerance=float("-inf")#0.001 # the change of auxin in each cell must be below this value to call a step stable
        self.c_rtol = 0.1 # relative tolerance accepted by ODE solver
        self.c_atol = 0.1 # absolute tolerance accepted by ODE solver
        self.c_new_simulation = False # start new simulation every run
        #### display constants
        self.c_disp_aux_max = 5
        self.c_show=True
        self.c_disp_pin_max= 0.2
        self.c_disp_pin_min=0.1
        self.c_dynamic_pin=False
        self.c_dynamic_aux=True
        
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
            return t
        
        def A( cid, t, x ):
            return x[ self.cell2sys[ cid ] ]
        
        def S( i ):
            return self.cell2surface[ i ]
        
        def W( (i,j) ):
            return self.cell_edge2wall_length[ (i,j) ]
        
        t = self.tissue_system.tissue

        x2 = len(x)*[0.]
        for i in t.cells():
            x2[ self.cell2sys[ i ] ]=0
            if not self.i_local_evacuate( i ):
                x2[ self.cell2sys[ i ] ] = self.c_sigma_a - (self.c_theta_a+self.i_center_evacuate(i)*self.c_theta_a_prim)*A(i,t,x) 
                for n in t.cell_neighbors(i):
                    x2[ self.cell2sys[ i ] ] += J((n,i),t,x) - J((i,n),t,x)
            elif not self.c_sink_fixed_concentration:
                x2[ self.cell2sys[ i ] ] = self.c_sigma_a - (self.c_theta_a+self.c_sink_destruction_rate)*A(i,t,x) 
                for n in t.cell_neighbors( cell=i ):
                    x2[ self.cell2sys[ i ] ] += J((n,i),t,x) - J((i,n),t,x)                    
        for (i,j) in t.cell_edges():
            x2[ self.wall2sys[(i,j)] ] = self.f_phi(J((i,j),t,x))+self.c_sigma_p-self.c_theta_p*P((i,j),t,x)
            x2[ self.wall2sys[(j,i)] ] = self.f_phi(J((j,i),t,x))+self.c_sigma_p-self.c_theta_p*P((j,i),t,x)
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
            if self.i_center_evacuate( c ) or self.i_local_evacuate( c ):
                self.aux(cell= c, value= 0. ) #+random.random() )

    def init_pin( self ):
        t = self.system.tissue
        for (i,j) in t.cell_edges():
            self.pin( (i,j), self.c_pin_init )
            self.pin( (j,i), self.c_pin_init )


class TissueSystem:
    """Stub tissue system..
    """
    def __init__( self, tissue, const=None ):
        self.tissue = tissue
        self.const=const
#        self.phys=PhysAuxinTransportModel36( tissue_system=self )
        self.frame=0
        self.tissue.time=0
        self.concentration_range=(5,20)
        
    def loop( self, nbr=3 ):
        while self.frame < nbr:
            self.step()
            
    def step( self, nbr=1 ):
        for i in range( nbr ):
            self.tissue.time+=1
            for i in range(50):
                self.phys.step(1, 0)
            self.update_visualisation(346)
 
    def update_conc_range( self ):
        l=[]
        for i in self.tissue.cells():
            l.append(self.tissue.cell_property( i , "auxin_level"))#/calculate_cell_surface(self.tissue, i ))
        self.concentration_range = (min(l),max(l))

    def update_pin_range( self ):
        l=[]
        min = float("inf")
        max = float("-inf")
        for i in self.tissue.cells():
            for n in self.tissue.cell_neighbors( i ):
                v = pin_level( s.tissue, cell_edge=(i,n))
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
            self.tissue.remove_cell( cell=i )

    
    def update_visualisation( self, max_wall_absolute_thickness=0.5, cell_marker_size=0.5,
                             abs_intercellular_space=0.5, revers=True, material_f=auxin2material5,
                             prefix="", **keys ):
        self.frame+=1
        pd.SCENES[ 0 ].clear()
        self.update_conc_range()
        self.update_pin_range()
        #abs_intercellular_space = 0.07
        
        if self.phys.c_dynamic_aux: concentration_range=self.concentration_range
        else: concentration_range=(0., self.phys.c_disp_aux_max)
        if self.phys.c_dynamic_pin: pin_range = self.pin_range
        else: pin_range = (self.phys.c_disp_pin_min,self.phys.c_disp_pin_max)
        #max_wall_absolute_thickness=keys.get("max_wall_absolute_thickness", 0.5)
        #cell_marker_size=keys.get("cell_marker_size", 0.5)
        #abs_intercellular_space=keys.get("abs_intercellular_space",0.5)
        #revers=keys.get("revers",True)
        #material_f=keys.get("material_f", auxin2material5)
        #prefix=keys.get("prefix", "")
        visualisation_pgl_2D_linear_tissue_aux_pin2( self.tissue, concentration_range=concentration_range, pin_range=pin_range, max_wall_absolute_thickness=max_wall_absolute_thickness,
                                                    cell_marker_size=cell_marker_size,abs_intercellular_space=abs_intercellular_space, material_f=material_f, revers=revers,
                                                    prim_cells_with_pin=self.phys.c_disp_pin_max, **keys)

        pd.instant_update_viewer()
        name = ("%.5d.png") % self.frame
        name = prefix+name
        pgl.Viewer.frameGL.saveImage(name)

    def mark_center_cells( self, cell, iaa_level=0 ):
        n1 = self.tissue.cell_neighbors( cell )
        self.tissue.cell_property( cell, "CZ", True )
        auxin_level( self.tissue, cell, iaa_level )
        for c in n1:
            self.tissue.cell_property( c, "CZ", True )
            auxin_level( self.tissue, c, iaa_level )
            for n in self.tissue.cell_neighbors( c ):
                self.tissue.cell_property( n, "CZ", True )
                auxin_level( self.tissue, n, 0 )
        try:
            self.phys.update_identity_dics()
        except Exception:
            print "Phys identity dics not updated"
    def mark_prim_cells( self, cell, nbr ):
        n1 = self.tissue.cell_neighbors( cell )
        self.tissue.cell_property( cell, "PrZ", nbr )
        self.tissue.cell_property( cell, "PrC", nbr )
        auxin_level( self.tissue, cell, 0 )
        for c in n1:
            self.tissue.cell_property( c, "PrZ", nbr )
            auxin_level( self.tissue, c, 0 )
        #self.phys.update_identity_dics()

    def write_tissue( self, file_name ):
        wtp = WalledTissuePickleWriter( file_name, mode="w",
                               tissue=WalledTissue2IOTissue(self.tissue, id=IntIdGenerator( self.tissue.wv_edges() )),
                               tissue_properties=WalledTissue2IOTissueProperties( self.tissue  ),
                               cell_properties=WalledTissue2IOCellPropertyList( self.tissue  ),
                               wv_properties=WalledTissue2IOEdgePropertyList( self.tissue ),
                               wv_edge_properties=WalledTissue2IOWallPropertyList( self.tissue, id=IntIdGenerator( self.tissue.wv_edges() ) ),
                               description="Tissue with aux and pin, hexagonal, 3sinks appearing in a raw." )
        wtp.write_all()
        print " #: tissue written.."
        
    def load_tissue( self, file_name ):
        wtpr = WalledTissuePickleReader( file_name, mode="r")
        wtpr.read_tissue()
        self.tissue=IOTissue2WalledTissue( wtpr.tissue, wtpr.wv_properties[ "_positions" ], const=WalledTissueCanalisationExp1() )
        wtpr.read_property( "auxin_level" )
        wtpr.read_property( "pin_level" )
        wtpr.read_property( "PrC" )
        wtpr.read_property( "PrZ" )
        for i in wt3.cells():
            self.tissue.cell_property( cell=i, property="auxin_level", value=wtpr.cell_properties[ "auxin_level" ][ i ] )
            self.tissue.cell_property( cell=i, property="PrZ", value=wtpr.cell_properties[ "PrZ" ][ i ] )
            self.tissue.cell_property( cell=i, property="PrC", value=wtpr.cell_properties[ "PrC" ][ i ] )
        #return wtpr #wtpr.wv_edge_properties[ "pin_level" ]
        for i in wtpr.tissue.scale_relations[1]:
            self.tissue.wv_edge_property( wv_edge=tuple(wtpr.tissue.scale_relations[1][i]), property="pin_level", value=wtpr.wv_edge_properties[ "pin_level" ][ i ] )
            


    def play1( self, folder="/home/stymek/mtmp/08-03-13-pinDynBiggerCenter/" ):
        green_range._position_list=[0.,0.94,1.]
        self.phys.c_dynamic_aux=False
        self.phys.c_disp_aux_max=5
        while True:
            self.load_tissue( folder+str(self.frame))
            #self.update_visualisation()
            #self.update_visualisation(abs_intercellular_space=0.05, revers=True, material_f=auxin2material6, wall_color=pgl.Color4(255,255,255,0))
            self.update_visualisation(max_wall_absolute_thickness=0.06,cell_marker_size=0.05,abs_intercellular_space=0.01,revers=True, material_f=auxin2material6, pump_color=pgl.Color4(255,0,0,0), wall_color=pgl.Color4(0,0,0,0),
                                      prefix=folder+"vis/1/")
            #self.frame+=1
            
    def run( self, nbr=60, nbr2=10, folder="/home/stymek/mtmp/08-03-13-pinDynBiggerCenter/" ):
        cc = 346
        p0 = 460
        p1 = 258
        p2 = 170
        prims = [(p0,1),(p1,2),(p2,3)]
        #prims = [(p0,1)]
        self.phys.c_break_step_nbr=nbr2
        self.phys.c_dynamic_aux=True
        self.phys.c_disp_aux_max=5.
        self.phys.c_disp_pin_max=0.2
        green_range._position_list=[0.,0.94,1.]
        self.phys.h=0.25
        for i in prims:
            self.mark_prim_cells( i[0], i[1] )
        self.mark_center_cells(cc, 1)

        #for i in self.tissue.cells():
        #    self.tissue.cell_property(i, "PrZ", 0)
            
        for i in range(nbr):
            self.phys.run()
            self.update_visualisation(max_wall_absolute_thickness=0.06,cell_marker_size=0.05,abs_intercellular_space=0.01,revers=True, material_f=auxin2material6, pump_color=pgl.Color4(255,0,0,0), wall_color=pgl.Color4(0,0,0,0),
                                      prefix=folder+"vis/1/")
            self.write_tissue(folder+str(self.frame))
            #self.frame+=1
            
        for i in prims:
            s.mark_prim_cells( 418, 4 )
        
        for i in range(30):
            self.phys.run()
            self.update_visualisation(max_wall_absolute_thickness=0.06,cell_marker_size=0.05,abs_intercellular_space=0.01,revers=True, material_f=auxin2material6, pump_color=pgl.Color4(255,0,0,0), wall_color=pgl.Color4(0,0,0,0),
                                      prefix=folder+"vis/1/")
            self.write_tissue(folder+str(self.frame))
            #self.frame+=1

        

wtpr = WalledTissuePickleReader( "/home/stymek/mdata/Pierres1", mode="r")
wtpr.read_tissue()
wt3=IOTissue2WalledTissue( wtpr.tissue, wtpr.wv_properties[ "_positions" ], const=WalledTissueCanalisationExp1() )
s=TissueSystem( wt3, const=WalledTissueCanalisationExp1() )
s.tissue.const=WalledTissueCanalisationExp1() 


#for i in s.tissue.wvs():
#    s.tissue.wv_pos( i, s.tissue.wv_pos( i )*100 ) 

cc = 346
p0 = 460
p1 = 258
p2 = 170
suporting_center_cell=322
prims = [(p0,1),(p1,2),(p2,3)]
prims = [(p0,1)]
     
    
ss=pd.AISphere()
ss.visible=False
pgl.Viewer.animation( True )
pgl.Viewer.camera.set( (0,1,3), -90, -90 )
pd.ASPHERE_PRIMITIVE.slices=20
s.phys=Phys( tissue_system=s )
s.phys.init_aux()
s.phys.init_pin()

pgl.Viewer.animation( True )
pgl.Viewer.frameGL.setSize(900,900)
pgl.Viewer.frameGL.setBgColor(pgl.Color3(255,255,255))
pgl.Viewer.camera.setOrthographic()
pgl.Viewer.camera.lookAt( (3.55,3.55,7.5), (3.55,3.55,0) )
pgl.Viewer.light.enabled=False

for i in prims:
    s.mark_prim_cells( i[0], i[1] )

#s.load_tissue("/home/stymek/mtmp/hex,3sinks-1/0")
s.phys.c_dynamic_aux=False
s.update_visualisation(abs_intercellular_space=0.01, revers=True, material_f=auxin2material3, pump_color=pgl.Color4(255,255,255,0), wall_color=pgl.Color4(0,0,0,0))
s.frame=0
s.phys.init_pin()
s.phys.init_aux()
#assert False
#s.run()
from openalea.mersim.physio.influence_zones import set_property_on_tissue_component
s.load_tissue("/home/stymek/mtmp/08-03-13-pinDynBiggerCenter/60/")
#s.load_tissue("/home/stymek/mtmp/realPierres1-1/61/")
center_cell=cc
tol=0.12
set_property_on_tissue_component(wt=s.tissue, cell=center_cell, f_component=pin_level, tol=tol, property="cC",
                                 property_value=True )
#set_property_on_tissue_component(wt=s.tissue, cell=suporting_center_cell, f_component=pin_level, tol=tol, property="cC",
#                                 property_value=True )
set_property_on_tissue_component(wt=s.tissue, cell=p0, f_component=pin_level, tol=tol, property="cP0",
                                 property_value=True )
set_property_on_tissue_component(wt=s.tissue, cell=p1, f_component=pin_level, tol=tol, property="cP1",
                                 property_value=True )
set_property_on_tissue_component(wt=s.tissue, cell=p2, f_component=pin_level, tol=tol, property="cP2",
                                 property_value=True )

s.update_visualisation( max_wall_absolute_thickness=0.06,cell_marker_size=0.05,abs_intercellular_space=0.01,revers=False,pump_color=pgl.Color4(255,0,0,0), wall_color=pgl.Color4(0,0,0,0),
                       material_f= f_property2material("cC"), prefix="can-c-"+str(tol)+"-")
s.update_visualisation( max_wall_absolute_thickness=0.06,cell_marker_size=0.05,abs_intercellular_space=0.01,revers=False,pump_color=pgl.Color4(255,0,0,0), wall_color=pgl.Color4(0,0,0,0),
                       material_f= f_property2material("cP0"), prefix="can-p0-"+str(tol)+"-")
s.update_visualisation( max_wall_absolute_thickness=0.06,cell_marker_size=0.05,abs_intercellular_space=0.01,revers=False,pump_color=pgl.Color4(255,0,0,0), wall_color=pgl.Color4(0,0,0,0),
                       material_f= f_property2material("cP1"), prefix="can-p1-"+str(tol)+"-")
s.update_visualisation( max_wall_absolute_thickness=0.06,cell_marker_size=0.05,abs_intercellular_space=0.01,revers=False,pump_color=pgl.Color4(255,0,0,0), wall_color=pgl.Color4(0,0,0,0),
                       material_f= f_property2material("cP2"), prefix="can-p2-"+str(tol)+"-")