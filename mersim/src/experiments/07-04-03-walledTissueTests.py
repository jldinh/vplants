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
__revision__="$Id: 07-04-03-walledTissueTests.py 7875 2010-02-08 18:24:36Z cokelaer $"

from openalea.mersim.tissue.walled_tissue import WalledTissue
from openalea.mersim.const.const import WalledTissueTest
from openalea.mersim.tissue.algo.walled_tissue import *
from openalea.mersim.tissue.algo.walled_tissue_division_policies import *
#from openalea.mersim.tissue.algo.walled_tissue_cfd import *
from openalea.mersim.tissue.algo.walled_tissue_dscs import *
from openalea.mersim.serial.walled_tissue import *
from openalea.mersim.gui.tissue import *

wtpr = WalledTissuePickleReader( "/home/stymek/tmp/cell", mode="r")
wtpr.read_tissue()
wt=IOTissue2WalledTissue( wtpr.tissue, wtpr.wv_properties[ "_positions" ] )


wtp = WalledTissuePickleWriter( "/home/stymek/tmp/cellSS", mode="w",
                       tissue=WalledTissue2IOTissue(wt, id=IntIdGenerator( wt.wv_edges() )),
                       tissue_properties=WalledTissue2IOTissueProperties( wt  ),
                       cell_properties=WalledTissue2IOCellPropertyList( wt  ),
                       wv_properties=WalledTissue2IOEdgePropertyList( wt ),
		       wv_edge_properties=WalledTissue2IOWallPropertyList( wt, id=IntIdGenerator( wt.wv_edges() ) ),
                       description="examplary desc" )
wtp.write_all()



