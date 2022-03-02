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
__revision__="$Id: 07-06-20-geneNetwork2Dexperiment.py 7875 2010-02-08 18:24:36Z cokelaer $"

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
        

class TissueSystem:
    """Stub tissue system..
    """
    def __init__( self, tissue, const=None ):
        self.tissue = tissue
        self.const=const
        self.phys=PhysReactionDiffusion1( tissue_system=self )
        self.growth=RadialGrowth( tissue=self.tissue, center= pgl.Vector3())
        self.cell_remover = SimulationRemoveCellStrategy2D_1( self, c_remove_2d_radius=2 )
        self.cell_identities =  PhysMarkCellIdentitiesWithFixedRegionsIn2D_2( tissue_system=self)
        self.frame=0
        self.tissue.time=0
        self.concentration_range=(5,20)
        
    def loop( self, nbr=3 ):
        while self.frame < nbr:
            self.step()
            
    def step( self, nbr=1 ):
        for i in range( nbr ):
            self.tissue.time+=1
            self.phys.step()
            self.update_visualisation()
            self.growth.apply()
            self.divide_cells()
            self.remove_cells()
           # raw_input()
        
 
       
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
        visualisation2( self.tissue, concentration_range=self.concentration_range, concentration_rangeH=self.concentration_rangeH )
        #cont_prims_visualisation1( self )
        pgl.Viewer.frameGL.saveImage(str(self.frame)+".png")

 
    def update_conc_range( self ):
        l=[]
        for i in self.tissue.cells():
            l.append(self.tissue.cell_property( i , "auxin_level"))#/calculate_cell_surface(self.tissue, i )
        self.concentration_range = (min(l),max(l))
        l=[]
        for i in self.tissue.cells():
            l.append(self.tissue.cell_property( i , "inh"))#/calculate_cell_surface(self.tissue, i )
        self.concentration_rangeH = (min(l),max(l))



#wtpr = WalledTissuePickleReader( "/home/stymek/mdata/circ,2D", mode="r")
wtpr = WalledTissuePickleReader( "/home/stymek/mdata/circ,2d,4cana", mode="r")
wtpr.read_tissue()
wt3=IOTissue2WalledTissue( wtpr.tissue, wtpr.wv_properties[ "_positions" ], const=WalledTissueReactionDiffusion1() )

s=TissueSystem( wt3, const=WalledTissueReactionDiffusion1() )
s.tissue.const=WalledTissueReactionDiffusion1()
s.cell_identities.mark_cell_identities()
#for c in s.tissue.cells():
    
ss=pd.AISphere()
ss.visible=False
s.update_visualisation()
pgl.Viewer.animation( True )
pgl.Viewer.camera.lookAt( (0,0,4), (0,0,0) )
pd.ASPHERE_PRIMITIVE.slices=20
for i in s.tissue.cells():
    s.tissue.cell_property(i, "auxin_level", 5*random.random() )
    s.tissue.cell_property(i, "inh", 1 )
    
for i in s.tissue.cells():
    if s.tissue.cell_property( i, "IC" ) == 0:
        s.tissue.remove_cell( i )
        
c = cell_center( s.tissue, s.tissue.cells()[ 0 ] )
d = c - s.growth.center

for i in s.tissue.wvs():
    s.tissue.wv_pos( i, s.tissue.wv_pos( i ) - d )
s.update_visualisation()    

