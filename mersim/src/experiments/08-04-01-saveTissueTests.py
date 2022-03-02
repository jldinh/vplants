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
__revision__="$Id: 08-04-01-saveTissueTests.py 7875 2010-02-08 18:24:36Z cokelaer $"

from openalea.mersim.serial.merrysim_plugin import save_dat_and_lyn_files_as_WT
from openalea.mersim.const.const import TissueConst
from openalea.mersim.serial.walled_tissue import  read_walled_tissue
const=TissueConst()
const.cell_properties ={
        "PrC": 0,
        "auxin_level": 0,
    }
const.wv_edge_properties={
        "pin_level":[0,0],
}

path="/home/stymek/mdata/07-07-05-PINwithImmunolab/"
wt_filename="/home/stymek/tmp/tis_test/"
save_dat_and_lyn_files_as_WT( dat_filename=path+"c16-proj-grey.dat", lyn_filename=path+"c16-proj-grey.link", wt_filename=wt_filename, const=const)

const.cell_properties ={
        "auxin_level": 0,
    }
t = read_walled_tissue( file_name=wt_filename, const=const )

from openalea.mersim.tissue.algo.walled_tissue import show_cells
show_cells( t, True)
