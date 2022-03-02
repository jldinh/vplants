#!/usr/bin/env python
"""Module to import misc file structures from Pierrs merrysim code.

Import is done by reading text files/

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
__revision__="$Id: merrysim_plugin.py 7875 2010-02-08 18:24:36Z cokelaer $"

import re

def read_links( link_fn=None ):
    """Read graph representing the cell to cell conections.
    
    <Long description of the function functionality.>
    
    :parameters:
        link_fn : `string`
            Name of the file containing the cell to cell links.
    :rtype: [(cell_id,cell_id)]
    :return: List of cell_ids pairs.
    :raise Exception: <Description of situation raising `Exception`>
    """
    ret = []
    exp  = "[-+]?\d+ [-+]?\d+"
    r = re.compile( exp )
    f = open( link_fn )
    try:
        for line in f:
            if r.match( line ):
                ret.append( tuple( line.split() ) )
    finally:
        f.close()
    return ret

def read_dat_file( dat_filename=None, get_z_coords=False, const=None ):
    """Reads tissue stored in Pierres .dat file.
    
    <Long description of the function functionality.>
    
    :parameters:
        dat_filename : string
            .dat file name (maybe with full path)
    :rtype: WalledTissue
    :return: Tissue resulting from conversion
    :raise Exception: when the filename is not set.
    """
    if not dat_filename:
        raise Exception(" .dat file not set!")
    from openalea.mersim.tissue.walled_tissue import WalledTissue
    
    if const==None:
        from openalea.mersim.const.const import TissueConst
        const=TissueConst()
    from openalea.mersim.tissue.algo.walled_tissue import create_tissue_topology_from_simulation, clear_incorrect_neighborhood
    w = WalledTissue( const=const )
    w.const.meristem_data=dat_filename
    
    create_tissue_topology_from_simulation( w, get_z_coords=get_z_coords, clear_all=False )
    
    for c in w.cells():
        if len( w.cell2wvs( c ) )  < 3:
            w.remove_cell( c )       
    clear_incorrect_neighborhood( w )
    
    return w

def save_dat_file_as_WT( dat_filename=None, wt_filename=None, description="", walled_tissue=None, const=None ):
    """Reads tissue stored in Pierres .dat file and saves it in WT format.
    
    <Long description of the function functionality.>
    
    :parameters:
        dat_filename : string
            .dat file name (maybe with full path)
        wt_filename : string
            .dat file name (maybe with full path)
    :rtype: WalledTissue
    :return: Tissue resulting from conversion
    :raise Exception: <Description of situation raising `Exception`>
    """
    from openalea.mersim.serial.walled_tissue import WalledTissuePickleWriter, WalledTissue2IOTissueProperties, WalledTissue2IOCellPropertyList, WalledTissue2IOEdgePropertyList, WalledTissue2IOWallPropertyList, WalledTissue2IOTissue
    from openalea.mersim.tools.misc import IntIdGenerator
    if not walled_tissue:
        if not wt_filename:
            raise Exception("wt_filename not set!")
        wt = read_dat_file( dat_filename=dat_filename, const=const )
    else: wt = walled_tissue
    wtp = WalledTissuePickleWriter( wt_filename, mode="w",
                       tissue=WalledTissue2IOTissue(wt, id=IntIdGenerator( wt.wv_edges() )),
                       tissue_properties=WalledTissue2IOTissueProperties( wt  ),
                       cell_properties=WalledTissue2IOCellPropertyList( wt  ),
                       wv_properties=WalledTissue2IOEdgePropertyList( wt ),
		       wv_edge_properties=WalledTissue2IOWallPropertyList( wt, id=IntIdGenerator( wt.wv_edges() ) ),
                       description=description )
    wtp.write_all()

def save_dat_and_lyn_files_as_WT( dat_filename=None, lyn_filename=None, wt_filename=None, description="", get_z_coords=False, const=None ):
    """Reads tissue stored in Pierres .dat file and saves it in WT format.
    
    <Long description of the function functionality.>
    
    :parameters:
        filename : string
            .dat file name (maybe with full path)
        wt_filename : string
            .dat file name (maybe with full path)
    :rtype: WalledTissue
    :return: Tissue resulting from conversion
    :raise Exception: <Description of situation raising `Exception`>
    """
    from openalea.mersim.tissue.algo.walled_tissue import pin_level
    if not lyn_filename:
        raise Exception(".lyn filename not set!")
    l = read_links(lyn_filename)
    w = read_dat_file( dat_filename=dat_filename, get_z_coords=get_z_coords, const=const)
    for ce in  w.cell_edges():
        pin_level( w, cell_edge=(int(ce[ 0 ]), int(ce[ 1 ]) ), value=0. )
        pin_level( w, cell_edge=(int(ce[ 1 ]), int(ce[ 0 ]) ), value=0. )
    for ce in l:
        pin_level( w, cell_edge=(int(ce[ 0 ]), int(ce[ 1 ]) ), value=1. )
    save_dat_file_as_WT( dat_filename=dat_filename, wt_filename=wt_filename, description=description, const=const, walled_tissue=w )
