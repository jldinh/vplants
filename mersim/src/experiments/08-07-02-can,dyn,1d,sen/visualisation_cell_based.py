#!/usr/bin/env python
"""Used to make projections based on the dictionary data.

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
__revision__="$Id: visualisation_cell_based.py 7875 2010-02-08 18:24:36Z cokelaer $"

from openalea.mersim.tissue.walled_tissue import WalledTissue
from openalea.mersim.const.const import WalledTissueTest
from openalea.mersim.tissue.algo.walled_tissue import *
from openalea.mersim.tissue.algo.walled_tissue_division_policies import *
#from openalea.mersim.tissue.algo.walled_tissue_cfd import *
from openalea.mersim.tissue.algo.walled_tissue_dscs import *
from openalea.mersim.serial.walled_tissue import *
from openalea.mersim.gui.tissue import *

def set_iaa_and_pin_from_pickle_file( file_name=None, tissue=None ):
    """Sets the IAA and PIN levels form file
    
    <Long description of the function functionality.>
    
    :parameters:
        file_name : string
            Filename containing IAA and PIN.
        tissue : WT
            WalledTissue
    :rtype: `T`
    :return: <Description of ``return_object`` meaning>
    :raise Exception: <Description of situation raising `Exception`>
    """
    import pickle
    d = pickle.load( file(file_name, "r") )
    for i in d[ "IAA" ]:
        tissue.cell_property( cell=i, property="auxin_level", value=d["IAA"][ i ] )
    for i in d["PIN"]:
        pin_level( wtt=tissue, cell_edge=i, value=d["PIN"][i] )
        

wtpr = WalledTissuePickleReader( "/home/stymek/mdata/1DlinearTissue", mode="r")
wtpr.read_tissue()
wt3=IOTissue2WalledTissue( wtpr.tissue, wtpr.wv_properties[ "_positions" ] )

for i in wt3.cells():
    if i >= 20:
        wt3.remove_cell( i )

set_iaa_and_pin_from_pickle_file( "test.pickle", wt3)

visualisation_pgl_2D_linear_tissue_aux_pin( wt3, concentration_range=(0,6), pin_range=(0,0.6), max_wall_absolute_thickness=0.075, cell_marker_size=0.1, material_f=auxin2material4)
        #cz=self.cell_remover.c_remove_2d_radius( self.tissue, concentration_range=self.concentration_range, pin_range=self.pin_range )
#pd.instant_update_viewer()
pgl.Viewer.animation( True )
pgl.Viewer.camera.set( (0,1,0), -90, -90 )
