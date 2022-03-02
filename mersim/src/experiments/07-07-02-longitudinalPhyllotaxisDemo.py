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
__revision__="$Id: 07-07-02-longitudinalPhyllotaxisDemo.py 7875 2010-02-08 18:24:36Z cokelaer $"

from openalea.mersim.tissue.walled_tissue import WalledTissue
from openalea.mersim.const.const import *
from openalea.mersim.tissue.algo.walled_tissue import *
from openalea.mersim.tissue.algo.walled_tissue_division_policies import *
#from openalea.mersim.tissue.algo.walled_tissue_cfd import *
from openalea.mersim.tissue.algo.walled_tissue_dscs import *
from openalea.mersim.serial.walled_tissue import *
from openalea.mersim.gui.tissue import *
from openalea.mersim.physio.canalisation import *
from openalea.mersim.physio.cell_identities import *
#from openalea.mersim.mass_spring.forces import * 
#from openalea.mersim.mass_spring.system import *
from openalea.mersim.tissue.algo.walled_tissue_division_policies import *
from openalea.mersim.tissue.algo.walled_tissue_dscs import *
from openalea.mersim.tissue.algo.walled_tissue_cfd import ds_surface
from openalea.mersim.simulation.remove_cell_strategy import *
import random

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
        
        

class TissueSystem:
    """Stub tissue system..
    """
    def __init__( self, tissue, const=None ):
        self.tissue = tissue
        self.const=const
        self.phys=PhysAuxinLongitudianTransportModel1( tissue_system=self )
        self.growth=RadialGrowth( tissue=self.tissue, center= pgl.Vector3())
        self.cell_remover = SimulationRemoveCellStrategy2D_1( self, c_remove_2d_radius=2 )
        self.cell_identities =  PhysMarkCellIdentitiesWithFixedRegionsIn2D_2( tissue_system=self)
        self.cont_prims =ContinousPrimsGrowth( profile_f=(lambda x:(-x*x +2.2*2.2)/4.), c_remove_radius = 5)
        self.frame=0
        self.tissue.time=0
        self.concentration_range=(5,20)
        
    def loop( self, nbr=3 ):
        while self.frame < nbr:
            self.step()
            
    def step( self, nbr=1 ):
        for i in range( nbr ):
            #if nbr>1:
            #    self.phys.c_change=float("inf")
            self.tissue.time+=1
            self.cell_identities.apply()
            for i in range(50):
                self.phys.step(1, 0)
            self.update_visualisation()
            #self.growth.apply()
            #self.divide_cells()
            #self.remove_cells()
            #self.cont_prims.move()
           # raw_input()
        
 
    def update_conc_range( self ):
        l=[]
        for i in self.tissue.cells():
            l.append(self.tissue.cell_property( i , "auxin_level")/calculate_cell_surface(self.tissue, i ))
        self.concentration_range = (min(l),max(l))
       
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


    def divide_cells( self ):
        ds_surface( self.tissue, dscs_shortest_wall_with_geometric_shrinking, pre=pre_3, post=post_3 )
    
    def update_visualisation( self ):
        self.frame+=1
        pd.SCENES[ 0 ].clear()
        self.update_conc_range()
        visualisation1( self.tissue, concentration_range=self.concentration_range )
        cz=self.cell_remover.c_remove_2d_radius
        pd.instant_update_viewer()
        pgl.Viewer.frameGL.saveImage(str(self.frame)+".png")

wtpr = WalledTissuePickleReader( "/home/stymek/mdata/2DlongitudinalCut", mode="r")
wtpr.read_tissue()
wt3=IOTissue2WalledTissue( wtpr.tissue, wtpr.wv_properties[ "_positions" ], const=WalledTissueLongitudinalCutExp1() )

s=TissueSystem( wt3, const=WalledTissueLongitudinalCutExp1() )
s.tissue.const=WalledTissueLongitudinalCutExp1() 
for i in s.tissue.cells():
    s.tissue.cell_property( cell=i, property="auxin_level", value=(1-0.1*random.random())*0.05*calculate_cell_surface(s.tissue, i) )
ss=pd.AISphere()
ss.visible=False
s.update_visualisation()
pgl.Viewer.animation( True )
pgl.Viewer.camera.set( (0,1,3), -90, -90 )
pd.ASPHERE_PRIMITIVE.slices=20
s.tissue.cell_property( cell=144, property="innerSink", value=True )
s.tissue.cell_property( cell=176, property="PrC", value=1)
#s.step()
#s.phys.aux_prim_trs_con=0.89
#s.step()
#s.phys.aux_prim_trs_con=90.89
#for i in s.tissue.cells():
#    if s.tissue.cell_property( i, "PrC" )>0:
#        c = i
#l = [c]
#for i in s.tissue.cell_neighbors( c ):
#    l.append( i )
#pd.SCENES[ 0 ].clear()
#visualisation_of_flux_zones_1( s.tissue, cells=l, tol=1.25 )  
