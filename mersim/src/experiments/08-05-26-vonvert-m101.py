#!/usr/bin/env python
"""Reading and converting m10 meristem
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
__revision__="$Id: 08-05-26-vonvert-m101.py 7875 2010-02-08 18:24:36Z cokelaer $"

from openalea.mersim.serial.merrysim_plugin import save_dat_and_lyn_files_as_WT
from openalea.mersim.const.const import TissueConst
from openalea.mersim.serial.walled_tissue import  read_walled_tissue
const=TissueConst()
const.cell_properties ={
        "auxin_level": 0,
        "PrC": 0,
        "PrZ":0,
        "CZ":0,
        "PZ":0,
    }
const.wv_edge_properties={
        "pin_level":[0,0],
}

const.tissue_properties={}
path="/home/stymek/mdata/m101/"
wt_filename="/home/stymek/mdata/m101-mersim/"
save_dat_and_lyn_files_as_WT( dat_filename=path+"M101a'-S01.dat", lyn_filename=path+"M101a'-S01.link", wt_filename=wt_filename, const=const)

cc = []

#reading
t = read_walled_tissue( file_name=wt_filename, const=const )

# scalling to get mikrometers units,
# moving to have the center of the meristem in the (0,0,0)
# changing x to 
# rotating
from openalea.plantgl.all import Vector3
avg=Vector3()
for i in t.wvs():
    t.wv_pos(i, t.wv_pos(i)/4.)
    avg+=t.wv_pos(i)
avg = avg/float(len(t.wvs()))
for i in t.wvs():
    t.wv_pos(i, t.wv_pos(i)-avg)

#for i in t.wvs():
#    x=t.wv_pos(i)
#    x.y=-x.y
#    t.wv_pos(i, x)

import openalea.plantgl.all as pgl
import math
m = pgl.Matrix3().axisRotation((0,0,1),math.pi/2.)
for i in t.wvs():
    t.wv_pos(i, m*t.wv_pos(i))
 
    
from openalea.mersim.tissue.algo.walled_tissue import calculate_cell_surface
s=0.
for i in t.cells():
    s+=calculate_cell_surface(t, i)
s=s/float(len(t.cells()))

#for i in t.cells():
#    if calculate_cell_surface(t, i) > 3.*s:
#        t.remove_cell(i)
#        

t.const.cell_node_size=0.1



for i in cc:
    t.cell_property( i, "CZ", True)

#saving
from openalea.mersim.serial.walled_tissue import  WalledTissuePickleWriter, WalledTissue2IOWallPropertyList, WalledTissue2IOTissueProperties, WalledTissue2IOCellPropertyList,  WalledTissue2IOEdgePropertyList, WalledTissue2IOTissue
from openalea.mersim.tools.misc import IntIdGenerator
wtp = WalledTissuePickleWriter( wt_filename, mode="w",
                       tissue=WalledTissue2IOTissue(t, id=IntIdGenerator( t.wv_edges() )),
                       tissue_properties=WalledTissue2IOTissueProperties( t  ),
                       cell_properties=WalledTissue2IOCellPropertyList( t  ),
                       wv_properties=WalledTissue2IOEdgePropertyList( t ),
                       wv_edge_properties=WalledTissue2IOWallPropertyList( t, id=IntIdGenerator( t.wv_edges() ) ),
                       description="Tissue with aux and pin, taken from Marianne, meristem 01. The geometry was corrected and 1unit=1micrometer" )
wtp.write_all()
print " #: tissue written.."

from openalea.mersim.tissue.algo.walled_tissue import show_cells
show_cells( t, True)
