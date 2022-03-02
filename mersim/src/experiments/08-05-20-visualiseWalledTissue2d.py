#!/usr/bin/env python
"""View walled2dtissue in PlantGl.

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
__revision__="$Id: 08-05-20-visualiseWalledTissue2d.py 7875 2010-02-08 18:24:36Z cokelaer $"

from openalea.mersim.const.const import TissueConst
from openalea.mersim.serial.walled_tissue import  read_walled_tissue
import openalea.plantgl.all as pgl
import  openalea.plantgl.ext.all as pd
from openalea.mersim.gui.tissue import auxin2material5, mark_regions5
from openalea.mersim.gui.tissue import  visualisation_pgl_2D_linear_tissue_aux_pin2

const=TissueConst()
const.cell_properties ={
        "PrC": 0,
        "auxin_level": 0,
        "PrZ": 0,
        "CZ":0,
        "PZ":0,
    }
const.wv_edge_properties={
        "pin_level":[0,0],
}
const.tissue_properties={}


def visualisation( tissue, conf, **keys ):
    pd.SCENES[ 0 ].clear()
    visualisation_pgl_2D_linear_tissue_aux_pin2( tissue, concentration_range=conf["concentration_range"],
                                                pin_range=conf["pin_range"], max_wall_absolute_thickness=conf["max_wall_absolute_thickness"],
                                                cell_marker_size=conf["cell_marker_size"], abs_intercellular_space=conf["abs_intercellular_space"],
                                                material_f=conf["material_f"], revers=conf["revers"],
                                                prim_cells_with_pin=conf["prim_cells_with_pin"],
                                                f_mark_regions=conf["f_mark_regions"], stride=conf["stride"], **keys)

visualisation_conf={"concentration_range":[0,1],
                    "pin_range":[0.1,0.2],
                    "max_wall_absolute_thickness":0.9,
                    "cell_marker_size":0.8,
                    "abs_intercellular_space":0.2,
                    "revers":False,
                    "material_f":auxin2material5,
                    "prefix":"",
                    "prim_cells_with_pin": True,
                    "f_mark_regions": mark_regions5,
                    "stride": 15,
}

# reading tissue
path="/home/stymek/mdata/08-05-21-marianne01/"
wt_filename="/home/stymek/mdata/08-05-21-marianne01-mersim/"
t = read_walled_tissue( file_name=wt_filename, const=const )



#viewer settings
pd.set_instant_update_visualisation_policy( policy = False )
pgl.Viewer.animation( True )
pgl.Viewer.frameGL.setSize(900,900)
pgl.Viewer.frameGL.setBgColor(pgl.Color3(255,255,255))
pgl.Viewer.camera.setOrthographic()
pgl.Viewer.light.enabled=False
pgl.Viewer.display(pd.SCENES[0])     
pgl.Viewer.camera.lookAt( (0,0,-125), (0,0,0) )
# visulaization of tissue
#visualisation(t, visualisation_conf)
#pd.instant_update_viewer()


### zones
tol=0.5
cc = [955,958,954,959,961,974,988,987,975,960,953,
      940,936,937,942,938,943,944,952,977,984,985,
      983,982,978,979,951,945,976,986,1083]
p0=971
p1=1185
p2=1450
p3=1127
p4=1300
p5=1047
from openalea.mersim.physio.influence_zones import set_property_with_weight_on_tissue_component
from openalea.mersim.tissue.algo.walled_tissue import pin_level
from openalea.mersim.gui.tissue import f_weighted_property2material

#visualisation_conf["material_f"] = auxin2material5
#visualisation(t, visualisation_conf)

set_property_with_weight_on_tissue_component(wt=t, cell=cc[0], f_component=pin_level, tol=tol, property="cC",
                                 property_value=True, additional_vertices=cc )
set_property_with_weight_on_tissue_component(wt=t, cell=p0, f_component=pin_level, tol=tol, property="cP0",
                                 property_value=True )
set_property_with_weight_on_tissue_component(wt=t, cell=p1, f_component=pin_level, tol=tol, property="cP1",
                                 property_value=True )
set_property_with_weight_on_tissue_component(wt=t, cell=p2, f_component=pin_level, tol=tol, property="cP2",
                                 property_value=True )
set_property_with_weight_on_tissue_component(wt=t, cell=p3, f_component=pin_level, tol=tol, property="cP3",
                                 property_value=True )
set_property_with_weight_on_tissue_component(wt=t, cell=p4, f_component=pin_level, tol=tol, property="cP4",
                                 property_value=True )
set_property_with_weight_on_tissue_component(wt=t, cell=p5, f_component=pin_level, tol=tol, property="cP5",
                                 property_value=True )


for i in range(8,20):
    range=[0,i]
    visualisation_conf["material_f"]=f_weighted_property2material("cC", range=range)
    visualisation( t, visualisation_conf )
    pgl.Viewer.frameGL.saveImage("08-05-21-marianne01-mersim-real-cC-t"+str(range[1])+".png")
    visualisation_conf["material_f"]=f_weighted_property2material("cP0", range=range)
    visualisation( t, visualisation_conf )
    pgl.Viewer.frameGL.saveImage("08-05-21-marianne01-mersim-real-cP0-t"+str(range[1])+".png")
    visualisation_conf["material_f"]=f_weighted_property2material("cP1", range=range)
    visualisation( t, visualisation_conf )
    pgl.Viewer.frameGL.saveImage("08-05-21-marianne01-mersim-real-cP1-t"+str(range[1])+".png")
    visualisation_conf["material_f"]=f_weighted_property2material("cP2", range=range)
    visualisation( t, visualisation_conf )
    pgl.Viewer.frameGL.saveImage("08-05-21-marianne01-mersim-real-cP2-t"+str(range[1])+".png")
    visualisation_conf["material_f"]=f_weighted_property2material("cP3", range=range)
    visualisation( t, visualisation_conf )
    pgl.Viewer.frameGL.saveImage("08-05-21-marianne01-mersim-real-cP3-t"+str(range[1])+".png")
    visualisation_conf["material_f"]=f_weighted_property2material("cP4", range=range)
    visualisation( t, visualisation_conf )
    pgl.Viewer.frameGL.saveImage("08-05-21-marianne01-mersim-real-cP4-t"+str(range[1])+".png")
    visualisation_conf["material_f"]=f_weighted_property2material("cP5", range=range)
    visualisation( t, visualisation_conf )
    pgl.Viewer.frameGL.saveImage("08-05-21-marianne01-mersim-real-cP5-t"+str(range[1])+".png")

