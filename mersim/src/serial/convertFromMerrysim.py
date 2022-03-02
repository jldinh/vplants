#!/usr/bin/env python
"""Reading and converting merrysim data to mersim. Output saved in the file. 
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
__revision__="$Id: convertFromMerrysim.py 7875 2010-02-08 18:24:36Z cokelaer $"

from openalea.mersim.serial.merrysim_plugin import save_dat_and_lyn_files_as_WT
from openalea.mersim.const.const import TissueConst
from openalea.mersim.serial.walled_tissue import  read_walled_tissue
from openalea.plantgl.all import Vector3
import openalea.plantgl.all as pgl
from openalea.mersim.serial.walled_tissue import  WalledTissuePickleWriter, WalledTissue2IOWallPropertyList, WalledTissue2IOTissueProperties, WalledTissue2IOCellPropertyList,  WalledTissue2IOEdgePropertyList, WalledTissue2IOTissue
from openalea.mersim.tools.misc import IntIdGenerator
import math
from openalea.mersim.tissue.algo.walled_tissue import calculate_cell_surface
from openalea.mersim.tissue.algo.walled_tissue_topology import initial_find_the_inside_of_tissue

class Config:
   """ Load a python configuration file """
   def __init__(self, filename):
        print " #: reading..", filename
        execfile(filename, self.__dict__)


def convert( config ):
    """Convert merrysim data to mersim data.
    
    <Long description of the function functionality.>
    
    :parameters:
        config : string
            Filename of file containing config. If None config is taken from current directory from convert_config.py
    :raise Exception: <Description of situation raising `Exception`>
    """
    if config: c = Config( config )
    else: c = Config( "convert_config.py")
    
    #print "cells to remove:", c.remove_cell_list
    #print "cell_properties", c.cell_properties
    
    if c.merrysim_use_lyn_file:
        save_dat_and_lyn_files_as_WT( dat_filename=c.merrysim_file_folder+c.merrysim_dat_file,
                                 lyn_filename=c.merrysim_file_folder+c.merrysim_lyn_file,
                                 wt_filename=c.mersim_file_folder, const=c.const)
    else:
        print "Not supported: merrysim_use_lyn_file must be True"
        return 1
    
    #reading to edit
    t = read_walled_tissue( file_name=c.mersim_file_folder, const=c.const )
    
    # scalling to get mikrometers units,
    # moving to have the center of the meristem in the (0,0,0)
    # changing x to 
    # rotating
    avg=Vector3()
    for i in t.wvs():
        t.wv_pos(i, t.wv_pos(i)/c.scale_factor)
        avg+=t.wv_pos(i)
    avg = avg/float(len(t.wvs()))
    for i in t.wvs():
        t.wv_pos(i, t.wv_pos(i)-avg)
    
    m = pgl.Matrix3().axisRotation((0,0,1),math.pi/2.)
    for i in t.wvs():
        t.wv_pos(i, m*t.wv_pos(i))
     
        
    s=0.
    for i in t.cells():
        s+=calculate_cell_surface(t, i)
    s=s/float(len(t.cells()))

    for i in c.remove_cell_list:
        t.remove_cell(i)
    
    if c.remove_big_cells:
        for i in t.cells():
            if calculate_cell_surface(t, i) > c.remove_big_cells_factor*s:
                t.remove_cell(i)
                 
    # setting cell properties
    for i in c.cell_properties.keys():
        if i in c.const.cell_properties.keys():
            for j in c.cell_properties[ i  ].keys():
                t.cell_property(j, i, c.cell_properties[ i  ][ j ] )

    initial_find_the_inside_of_tissue( t )

    #saving
    wtp = WalledTissuePickleWriter( c.mersim_file_folder, mode="w",
                           tissue=WalledTissue2IOTissue(t, id=IntIdGenerator( t.wv_edges() )),
                           tissue_properties=WalledTissue2IOTissueProperties( t  ),
                           cell_properties=WalledTissue2IOCellPropertyList( t  ),
                           wv_properties=WalledTissue2IOEdgePropertyList( t ),
                           wv_edge_properties=WalledTissue2IOWallPropertyList( t, id=IntIdGenerator( t.wv_edges() ) ),
                           description=c.description )
    wtp.write_all()
    print " #: tissue written.."
    
    
    if c.display_tissue:
        from openalea.mersim.tissue.algo.walled_tissue import show_cells
        t.const.cell_node_size=0.1
        show_cells( t, True)
