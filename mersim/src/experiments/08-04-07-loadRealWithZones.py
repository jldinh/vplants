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
__revision__="$Id: 08-04-07-loadRealWithZones.py 7875 2010-02-08 18:24:36Z cokelaer $"

from openalea.mersim.serial.merrysim_plugin import save_dat_and_lyn_files_as_WT
from openalea.mersim.const.const import TissueConst
from openalea.mersim.serial.walled_tissue import  read_walled_tissue
const=TissueConst()
const.cell_properties ={
#        "PrC": 0,
	"PrZ":0,
	"CZ":0,
        "auxin_level": 0,
    }
const.wv_edge_properties={
        "pin_level":[0,0],
}

wt_filename="/home/stymek/tmp/tis_test/"

t = read_walled_tissue( file_name=wt_filename, const=const )

import openalea.plantgl.all as pgl
import openalea.plantgl.ext.all as pd
pgl.Viewer.animation( True )
pgl.Viewer.frameGL.setSize(900,900)
pgl.Viewer.frameGL.setBgColor(pgl.Color3(255,255,255))
pgl.Viewer.camera.setOrthographic()
pgl.Viewer.camera.lookAt( (3.55,3.55,7.5), (3.55,3.55,0) )
pgl.Viewer.light.enabled=False

from openalea.mersim.gui.tissue import auxin2material5, visualisation_pgl_2D_linear_tissue_aux_pin2
visualisation_pgl_2D_linear_tissue_aux_pin2( t, concentration_range=[0,1], pin_range=[0,0.2],
                                            max_wall_absolute_thickness=0.5, cell_marker_size=0.5,
                                            abs_intercellular_space=0.5, revers=True, material_f=auxin2material5)

pd.instant_update_viewer()


