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
__revision__="$Id: 08-05-20-saveMarianneMeristem01AsMersimPickle.py 7875 2010-02-08 18:24:36Z cokelaer $"

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
path="/home/stymek/mdata/08-05-21-marianne01/"
wt_filename="/home/stymek/mdata/08-05-21-marianne01-mersim/"
save_dat_and_lyn_files_as_WT( dat_filename=path+"4.dat", lyn_filename=path+"4.link", wt_filename=wt_filename, const=const)

cc = [955,958,954,959,961,974,988,987,975,960,953,
      940,936,937,942,938,943,944,952,977,984,985,
      983,982,978,979,951,945,976,986,1083]
p0=971
p1=1185
p2=1450
p3=1127
p4=1300
p5=1047

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

for i in t.cells():
    if calculate_cell_surface(t, i) > 2.*s:
        t.remove_cell(i)

for i in [1433, 740, 817, 0]:
    t.remove_cell(i)
        

t.const.cell_node_size=0.1



for i in cc:
    t.cell_property( i, "CZ", True)
t.cell_property(p0, "PrC", 1)
t.cell_property(p1, "PrC", 2)
t.cell_property(p2, "PrC", 3)
t.cell_property(p3, "PrC", 4)
t.cell_property(p4, "PrC", 5)
t.cell_property(p5, "PrC", 6)

t.cell_property(p0, "PrZ", 1)
t.cell_property(p1, "PrZ", 2)
t.cell_property(p2, "PrZ", 3)
t.cell_property(p3, "PrZ", 4)
t.cell_property(p4, "PrZ", 5)
t.cell_property(p5, "PrZ", 6)

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
