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
__revision__="$Id: 08-01-23-longitudinalDemo.py 7875 2010-02-08 18:24:36Z cokelaer $"

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




class TissueSystem:
    """Stub tissue system..
    """
    def __init__( self, tissue, const=None ):
        self.tissue = tissue
        self.const=const
        self.phys=PhysAuxinLongitudianTransportModel3( tissue_system=self )
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
            self.update_visualisation()
        
 
    def update_conc_range( self ):
        l=[]
        for i in self.tissue.cells():
            l.append(self.tissue.cell_property( i , "auxin_level") )
        self.concentration_range = (min(l),max(l))
       
    
    def update_visualisation( self ):
        self.frame+=1
        pd.clear_scene()
        self.update_conc_range()
        visualisation_pgl_2D_linear_tissue_aux_pin2( self.tissue, concentration_range=self.concentration_range, pin_range=(0.1,1), max_wall_absolute_thickness=0.04, cell_marker_size=0.03,abs_intercellular_space=0.003, material_f=auxin2material1, revers=False)
        pd.instant_update_viewer()
        pgl.Viewer.frameGL.saveImage(str(self.frame)+".png")

wtpr = WalledTissuePickleReader( "/home/stymek/mdata/2DlongitudinalCut", mode="r")
wtpr.read_tissue()
wt3=IOTissue2WalledTissue( wtpr.tissue, wtpr.wv_properties[ "_positions" ], const=WalledTissueLongitudinalCutExp1() )

s=TissueSystem( wt3, const=WalledTissueLongitudinalCutExp1() )
s.tissue.const=WalledTissueLongitudinalCutExp1() 
#for i in s.tissue.cells():
#    s.tissue.cell_property( cell=i, property="auxin_level", value=(1-0.1*random.random())*0.05*calculate_cell_surface(s.tissue, i) )
ss=pd.AISphere()
ss.visible=False
pgl.Viewer.animation( True )
pgl.Viewer.camera.set( (0,1,3), -90, -90 )
pd.ASPHERE_PRIMITIVE.slices=20

for i in range(160,192):
    s.tissue.cell_property( cell=i, property="PrZ", value=1)

for i in [144,91,84,82,119,71,54,132,80,145,154,47,57]:
    s.tissue.cell_property( cell=i, property="CZ", value=1)

s.phys.init_pin()
s.phys.init_aux()

import random
for i in s.tissue.cell_edges():
    pin_level( s.tissue, i, random.random())

s.update_visualisation()
