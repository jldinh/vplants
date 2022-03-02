#!/usr/bin/env python
"""Real meristem flux maps.

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
__revision__="$Id: 07-08-01-canOnGrid-acropetal.py 7875 2010-02-08 18:24:36Z cokelaer $"

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
        self.phys=Phys2DGrid_RL_acropetal( tissue_system=self )
        self.growth=RadialGrowth( tissue=self.tissue, center= pgl.Vector3())
        self.cell_remover = SimulationRemoveCellStrategy2D_1( self, c_remove_2d_radius=2 )
        #self.cell_identities =  PhysMarkCellIdentitiesWithFixedRegionsIn2D_2( tissue_system=self)
        self.cont_prims =ContinousPrimsGrowth( profile_f=(lambda x:(-x*x +2.2*2.2)/4.), c_remove_radius = 5)
        self.frame=0
        self.tissue.time=0
        self.concentration_range=(5,20)
        self.pin_range = (1.,1.3)

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
        
    def loop( self, nbr=3 ):
        while self.frame < nbr:
            self.step()
            
    def step( self, nbr=1 ):
        for i in range( nbr ):
            #if nbr>1:
            #    self.phys.c_change=float("inf")
            self.tissue.time+=1
            #self.cell_identities.apply()
            for i in range(50):
                self.phys.step(1, 0)
            self.update_visualisation(346)
            #self.growth.apply()
            #self.divide_cells()
            #self.remove_cells()
            #self.cont_prims.move()
           # raw_input()
        
 
    def update_conc_range( self ):
        l=[]
        for i in self.tissue.cells():
            l.append(self.tissue.cell_property( i , "auxin_level"))#/calculate_cell_surface(self.tissue, i ))
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
    
    def update_visualisation( self, cell=None ):
        self.frame+=1
        pd.SCENES[ 0 ].clear()
        self.update_conc_range()
        self.update_pin_range()
        #visualisationTODO2( self.tissue, concentration_range=self.concentration_range, pin_range=self.pin_range )
        #visualisation_of_flux_zones_1(s.tissue,[cell]+self.tissue.cell_neighbors(cell),1.1)
        visualisation_pgl_2D_linear_tissue_aux_pin( self.tissue, concentration_range=self.concentration_range, pin_range=(0,4), max_wall_absolute_thickness=0.075, cell_marker_size=0.1)
        #cz=self.cell_remover.c_remove_2d_radius( self.tissue, concentration_range=self.concentration_range, pin_range=self.pin_range )
        pd.instant_update_viewer()
        pgl.Viewer.frameGL.saveImage(str(self.frame)+".png")

        visualisation_pgl_2D_linear_tissue_aux_pin( self.tissue, concentration_range=self.concentration_range, pin_range=self.pin_range, max_wall_absolute_thickness=0.075, cell_marker_size=0.1)
        #cz=self.cell_remover.c_remove_2d_radius( self.tissue, concentration_range=self.concentration_range, pin_range=self.pin_range )
        pd.instant_update_viewer()
        pgl.Viewer.frameGL.saveImage("r"+str(self.frame)+".png")

    def mark_center_cells( self, cell ):
        n1 = self.tissue.cell_neighbors( cell )
        for c in n1:
            self.tissue.cell_property( c, "CZ", True )
            for n in self.tissue.cell_neighbors( c ):
                self.tissue.cell_property( n, "CZ", True )
        
    def mark_prim_cells( self, cell, nbr ):
        n1 = self.tissue.cell_neighbors( cell )
        self.tissue.cell_property( cell, "PrZ", nbr )
        self.tissue.cell_property( cell, "PrC", nbr )
        for c in n1:
            self.tissue.cell_property( c, "PrZ", nbr )


w = WalledTissue( const=WalledTissuePinMapsExp2() )

s = TissueSystem( w )
for c in s.tissue.cells():
    if len( s.tissue.cell2wvs( c ) )  < 3:
        s.tissue.remove_cell( c )
        print "removed: ", c
clear_incorrect_neighborhood( s.tissue )


for i in s.tissue.wvs():
    s.tissue.wv_pos( i, 10*s.tissue.wv_pos( i ) ) 

#for ce in l:
#    pin_level( s.tissue, cell_edge=(int(ce[ 0 ]), int(ce[ 1 ]) ), value=1.4 )

center_cell = 346
p2 = 170
p1 = 258
p0 = 460

#for i in [(p0,1),(p1,2),(p2,3)]:
#    s.mark_prim_cells( i[0], i[1] )


wtpr = WalledTissuePickleReader( "/home/stymek/mdata/07-07-11-gridTissue", mode="r")
wtpr.read_tissue()
wt3=IOTissue2WalledTissue( wtpr.tissue, wtpr.wv_properties[ "_positions" ], const=WalledTissueCanalisationExp1() )
s=TissueSystem( wt3, const=WalledTissueCanalisationExp1() )
s.tissue.const=WalledTissueCanalisationExp1() 



#s.growth.center=cell_center( s.tissue, cell=center_cell )
s.cell_remover.c_remove_2d_radius=4
#for i in s.tissue.cells():
#    s.tissue.cell_property( cell=i, property="auxin_level", value=1.*calculate_cell_surface(s.tissue, i) + random.random()*0.01)
#for i in s.tissue.cells():
#    s.tissue.cell_property( cell=i, property="auxin_level", value=5.)
##for i in [p0,p1,p2]:
#    s.tissue.cell_property( cell=i, property="auxin_level", value=s.tissue.cell_property( cell=i, property="auxin_level")+0.25*calculate_cell_surface(s.tissue, i) )

#for i in s.tissue.
ss=pd.AISphere()
ss.visible=False
#s.mark_center_cells(346)
for i in range(0,15):
    s.tissue.cell_property( i, "CZ", 1)
#for i in range(210,225):
#    s.tissue.cell_property( i, "PrZ", 1)

for i in s.tissue.wvs():
    s.tissue.wv_pos( i, s.tissue.wv_pos(i)*10 )

#s.tissue.cell_property( 7, "CZ", 1)
#s.tissue.cell_property( 217, "PrZ", 1)

#for i in range(0,211,15):
#    print i, i+14
#    s.tissue._cells.add_edge(i, i+14)

s.phys.init_aux()
s.phys.init_pin()
    
s.update_visualisation( cell = center_cell)
pgl.Viewer.animation( True )
pgl.Viewer.camera.set( (0,1,3), -90, -90 )
pd.ASPHERE_PRIMITIVE.slices=20
#s.step()