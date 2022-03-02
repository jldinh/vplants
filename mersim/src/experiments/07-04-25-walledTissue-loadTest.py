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
__revision__="$Id: 07-04-25-walledTissue-loadTest.py 7875 2010-02-08 18:24:36Z cokelaer $"

from openalea.mersim.tissue.walled_tissue import WalledTissue
from openalea.mersim.const.const import WalledTissueTest
from openalea.mersim.tissue.algo.walled_tissue import *
from openalea.mersim.tissue.algo.walled_tissue_division_policies import *
#from openalea.mersim.tissue.algo.walled_tissue_cfd import *
from openalea.mersim.tissue.algo.walled_tissue_dscs import *
from openalea.mersim.serial.walled_tissue import *
from openalea.mersim.gui.tissue import *

#wt = WalledTissue( const=WalledTissueTest() )
#create_tissue_topology_from_simulation( wt )
#wt._tissue_properties[ "dupa" ] = "taka sobie.."
#import random
#for i in wt.wv_edges():
#    wt.wv_edge_property( wv_edge=i, property="pin_level", value=[random.random(),random.random()] )
#for i in wt.cells():
#    wt.cell_property( cell=i, property="auxine_level", value=random.random() )

#for z in [1,2,3]:
#    for i in wt.cells():
#        print i
#        wt.divide_cell(cell=i, dscs=dscs_shortest_wall )
#    show_cells_with_wvs( wt, True )
#show_cells_with_wvs( wt, True )
#show_cells( wt, True )
#wt.divide_cell(cell=10, dscs=dscs_shortest_wall )
#show_cells_with_wvs( wt, True )

#wtp = WalledTissuePickleWriter( "/home/stymek/tmp/bigReconstructedMeristem", mode="w",
#                       tissue=WalledTissue2IOTissue(wt, id=IntIdGenerator( wt.wv_edges() )),
#                       tissue_properties=WalledTissue2IOTissueProperties( wt  ),
#                       cell_properties=WalledTissue2IOCellPropertyList( wt  ),
#                       wv_properties=WalledTissue2IOEdgePropertyList( wt ),
#		       wv_edge_properties=WalledTissue2IOWallPropertyList( wt, id=IntIdGenerator( wt.wv_edges() ) ),
#                       description="examplarycd desc" )
#wtp.write_all()

wtpr = WalledTissuePickleReader( "/home/stymek/tmp/circular2D", mode="r")
wtpr.read_tissue()
wt3=IOTissue2WalledTissue( wtpr.tissue, wtpr.wv_properties[ "_positions" ] )
#for z in range(1):
#    for i in wt.cells():
#        wt3.divide_cell(cell=i, dscs=dscs_shortest_wall )
#show_cells_with_wvs( wt3, True )

#wtpr = WalledTissuePickleReader( "/home/stymek/tmp/circular2D", mode="r")
#wtpr.read_tissue()
#wt2 = IOTissue2WalledTissue( wtpr.tissue, wtpr.wv_properties[ "_positions" ] )
#for z in [1,2,3]:
#    for i in wt2.cells():
#        wt2.divide_cell(cell=i, dscs=dscs_shortest_wall )

#show_cells_with_wvs( wt2, True )

import random
for i in wt3.wv_edges():
    wt3.wv_edge_property( wv_edge=i, property="pin_level", value=[random.random(),random.random()] )
for i in wt3.cells():
    wt3.cell_property( cell=i, property="auxin_level", value=random.random() )
#visualisation1( wt3 )

visualisation_pgl_2D_linear_tissue_aux_pin( wt3, concentration_range=(0,10), pin_range=(0,4), max_wall_absolute_thickness=0.075, cell_marker_size=0.1)
        #cz=self.cell_remover.c_remove_2d_radius( self.tissue, concentration_range=self.concentration_range, pin_range=self.pin_range )
pd.instant_update_viewer()