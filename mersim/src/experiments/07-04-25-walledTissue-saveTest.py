#!/usr/bin/env python
"""The simple script testing the WalledTissue after refactoring.

No details.

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
__revision__="$Id: 07-04-25-walledTissue-saveTest.py 7875 2010-02-08 18:24:36Z cokelaer $"

from openalea.mersim.tissue.walled_tissue import WalledTissue
from openalea.mersim.const.const import WalledTissueTest
from openalea.mersim.tissue.algo.walled_tissue import *
from openalea.mersim.tissue.algo.walled_tissue_division_policies import *
#from openalea.mersim.tissue.algo.walled_tissue_cfd import *
from openalea.mersim.tissue.algo.walled_tissue_dscs import *
from openalea.mersim.serial.walled_tissue import *
from openalea.mersim.gui.tissue import *

wt = WalledTissue( const=WalledTissueTest() )
create_tissue_topology_from_simulation( wt )
wt._tissue_properties[ "dupa" ] = "taka sobie.."
import random
for i in wt.wv_edges():
    wt.wv_edge_property( wv_edge=i, property="pin_level", value=[random.random(),random.random()] )
for i in wt.cells():
    wt.cell_property( cell=i, property="auxine_level", value=random.random() )


wtp = WalledTissuePickleWriter( "/home/stymek/tmp/bigReconstructedMeristem", mode="w",
                       tissue=WalledTissue2IOTissue(wt, id=IntIdGenerator( wt.wv_edges() )),
                       tissue_properties=WalledTissue2IOTissueProperties( wt  ),
                       cell_properties=WalledTissue2IOCellPropertyList( wt  ),
                       wv_properties=WalledTissue2IOEdgePropertyList( wt ),
		       wv_edge_properties=WalledTissue2IOWallPropertyList( wt, id=IntIdGenerator( wt.wv_edges() ) ),
                       description="examplary desc" )
wtp.write_all()



