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
__revision__="$Id: 07-04-26-walledTissue-staticPumpingWithCanalisation.py 7875 2010-02-08 18:24:36Z cokelaer $"

from openalea.mersim.tissue.walled_tissue import WalledTissue
from openalea.mersim.const.const import WalledTissueTest
from openalea.mersim.tissue.algo.walled_tissue import *
from openalea.mersim.tissue.algo.walled_tissue_division_policies import *
#from openalea.mersim.tissue.algo.walled_tissue_cfd import *
from openalea.mersim.tissue.algo.walled_tissue_dscs import *
from openalea.mersim.serial.walled_tissue import *
from openalea.mersim.gui.tissue import *
from openalea.mersim.physio.canalisation import *

class TissueSystem:
    def __init__( self, tissue ):
        self.tissue = tissue

wtpr = WalledTissuePickleReader( "/home/stymek/mdata/circular2D", mode="r")
wtpr.read_tissue()
wt3=IOTissue2WalledTissue( wtpr.tissue, wtpr.wv_properties[ "_positions" ] )

import random
for i in wt3.cell_edges():
    wt3.cell_edge_property( cell_edge=i, property="pin_level", value=[0.,0.] )
for i in wt3.cells():
    wt3.cell_property( cell=i, property="auxin_level", value=random.random() )
wt3.cell_property( cell=94, property="PrC", value=1 )
wt3.cell_property( cell=105, property="PrC", value=1 )
wt3.cell_property( cell=43, property="PrC", value=1 )

p = PhysAuxinTransportModel14( tissue_system = TissueSystem( wt3 ) )
p.apply()

visualisation1( wt3 )