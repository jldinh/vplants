#!/usr/bin/env python
"""Configuration file for conversion from merrysim to mersim.

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
__revision__="$Id: convertFromMerrysimConfig.py 7875 2010-02-08 18:24:36Z cokelaer $"


# scale use to convert the units of merrysim to micrometers
scale_factor = 1.
#remove big cells?
remove_big_cells = False
#cells to remove
remove_cell_list = []
# big cells are removed if their surface is bigger than remove_big_cells_factor*avarage_cell_surface
remove_big_cells_factor = 2.
# path to merrysim data
merrysim_file_folder = ""
# merrysim .dat file name
merrysim_dat_file = ".dat"
# merrysim .lyn file name
merrysim_lyn_file = ".lyn"
# use lyn file to set pumps?
merrysim_use_lyn_file = True
# path to mersim file data
mersim_file_folder = ""
#tissue description
description=""

# properties to set wiht tissue
from openalea.mersim.const.const import TissueConst
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

# for each property the properties dictionary will be searched. if no value is found, the properties will be set as default
# if the dictionary contains a key with property name it can contain a dictionary inside with {cellId: modifiedProperty}
cell_properties = {}

display_tissue= True 
