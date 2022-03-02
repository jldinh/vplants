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
__revision__="$Id: 07-09-21-2d,hex,can,merSurf,fromAnalitical.py 7875 2010-02-08 18:24:36Z cokelaer $"

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
            self.update_conc_range()
            self.update_pin_range()
            self.update_visualisation(concentration_range=self.concentration_range, pin_range=self.pin_range)
 
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

    
    def update_visualisation( self, cell=None, **keys ):
        self.frame+=1
        pd.SCENES[ 0 ].clear()
        self.update_conc_range()
        self.update_pin_range()
        abs_intercellular_space = 0.07
        if keys.has_key( "concentration_range" ): concentration_range = keys[ "concentration_range" ]
        else: concentration_range = (0., self.phys.c_aux_max)
        if keys.has_key( "pin_range" ): pin_range = keys[ "pin_range" ]
        else: pin_range=(0.1,self.phys.c_pin_max)
        visualisation_pgl_2D_linear_tissue_aux_pin( self.tissue, concentration_range=concentration_range, pin_range=pin_range, max_wall_absolute_thickness=abs_intercellular_space+0.25, cell_marker_size=0.09, abs_intercellular_space=abs_intercellular_space )
        pd.instant_update_viewer()
        name = ("%.5d.png") % self.frame
        pgl.Viewer.frameGL.saveImage(name)

    def mark_center_cells( self, cell ):
        n1 = self.tissue.cell_neighbors( cell )
        for c in n1:
            self.tissue.cell_property( c, "CZ", True )
            auxin_level( self.tissue, c, 0 )
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
        self.phys.update_identity_dics()


wtpr = WalledTissuePickleReader( "/home/stymek/mdata/hexa210_hexa", mode="r")
wtpr.read_tissue()
wt3=IOTissue2WalledTissue( wtpr.tissue, wtpr.wv_properties[ "_positions" ], const=WalledTissueCanalisationExp1() )
s=TissueSystem( wt3, const=WalledTissueCanalisationExp1() )
s.tissue.const=WalledTissueCanalisationExp1() 


for i in s.tissue.wvs():
    s.tissue.wv_pos( i, s.tissue.wv_pos( i )*100 ) 

cc = 1012
p0 = 648
p1 = 1376
p2 = 838
prims = [(p0,1),(p1,2),(p2,3)]

for i in s.tissue.cells():
    s.tissue.cell_property(i, "BC", 0)
    
#for i in s.tissue.nth_layer_from_cell(cc, 8):
#    s.tissue.cell_property(i, "BC", 1)

for i in prims:
    s.mark_center_cells( i[0] )

#for i in prims:
#    s.mark_prim_cells( i[0], i[1] )

#ccn=s.tissue.cell_neighbors( cc )
#s.phys.pin( (cc,ccn[0]), 0.4 )
    
ss=pd.AISphere()
ss.visible=False
pgl.Viewer.animation( True )
pgl.Viewer.camera.set( (0,1,35), -90, -90 )
pd.ASPHERE_PRIMITIVE.slices=20
s.phys=Phys2DcanalisationWithExtBoundary1( tissue_system=s )
s.phys.init_aux()
s.phys.init_pin()
ccn=s.tissue.cell_neighbors( cc )
#s.phys.pin( (cc,ccn[0]), 0.4 )
#
#for i in s.tissue.cell_neighbors( 701 ):
#    s.phys.pin( (i, 701), 0.4 )
#    
#for i in s.tissue.cell_neighbors( 1331 ):
#    s.phys.pin( (1331, i), 0.4 )    


s.update_visualisation( )
