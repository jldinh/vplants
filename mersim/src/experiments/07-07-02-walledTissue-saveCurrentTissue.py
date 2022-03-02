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
__revision__="$Id: 07-07-02-walledTissue-saveCurrentTissue.py 7875 2010-02-08 18:24:36Z cokelaer $"

from openalea.mersim.tissue.walled_tissue import WalledTissue
from openalea.mersim.const.const import WalledTissueTest
from openalea.mersim.tissue.algo.walled_tissue import *
from openalea.mersim.tissue.algo.walled_tissue_division_policies import *
#from openalea.mersim.tissue.algo.walled_tissue_cfd import *
from openalea.mersim.tissue.algo.walled_tissue_dscs import *
from openalea.mersim.serial.walled_tissue import *
from openalea.mersim.gui.tissue import *

def write( s, name="tissue", path="/home/stymek/tmp" ):
    wtp = WalledTissuePickleWriter( path+"/"+name, mode="w",
                           tissue=WalledTissue2IOTissue(s, id=IntIdGenerator( s.wv_edges() )),
                           tissue_properties=WalledTissue2IOTissueProperties( s  ),
                           cell_properties=WalledTissue2IOCellPropertyList( s  ),
                           wv_properties=WalledTissue2IOEdgePropertyList( s ),
                           wv_edge_properties=WalledTissue2IOWallPropertyList( s, id=IntIdGenerator( s.wv_edges() ) ),
                           description=name,
                           wv_edges2int_id=IntIdGenerator( s.wv_edges() ))
    wtp.write_all()



