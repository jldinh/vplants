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
__revision__="$Id: 08-07-10-uniformGrowth.py 7875 2010-02-08 18:24:36Z cokelaer $"

from openalea.mersim.tissue.walled_tissue import WalledTissue
from openalea.mersim.const.const import *
from openalea.mersim.tissue.algo.walled_tissue import *
from openalea.mersim.tissue.algo.walled_tissue_division_policies import *
#from openalea.mersim.tissue.algo.walled_tissue_cfd import *
from openalea.mersim.tissue.algo.walled_tissue_dscs import *
from openalea.mersim.serial.walled_tissue import *
from openalea.mersim.gui.tissue import *
from openalea.mersim.physio.canalisation import *
from openalea.mersim.tissue.algo.walled_tissue_division_policies import *
from openalea.mersim.tissue.algo.walled_tissue_dscs import *
from openalea.mersim.tissue.algo.walled_tissue_cfd import ds_surface
from openalea.mersim.simulation.remove_cell_strategy import *
import random

            
            
            
                    
class PhysMarkCellIdentitiesWithFixedRegionsIn2D_2(PhysInterface):
    """Marking the cell identities basing only on current geometric information.
    
    bigger center zone comparing to PhysMarkCellIdentitiesWithFixedRegionsIn2D_1
    """
    
    def __init__( self, tissue_system=None):
        PhysInterface.__init__( self, tissue_system=tissue_system)
        self.reset_cell_identities()
        self.mark_cell_identities()
    
    def apply( self ):
        self.reset_cell_identities()
        self.mark_cell_identities()
    
    def reset_cell_identities( self ):
        for c in self.tissue_system.tissue.cells():
            self.tissue_system.tissue.cell_property( cell = c, property="IC", value=False)
            self.tissue_system.tissue.cell_property( cell = c, property="CZ", value=False)
            self.tissue_system.tissue.cell_property( cell = c, property="PZ", value=False)
            self.tissue_system.tissue.cell_property( cell = c, property="NZ", value=True)    
            self.tissue_system.tissue.cell_property( cell = c, property="PrZ", value=0)
            self.tissue_system.tissue.cell_property( cell = c, property="PrZ_stub", value=0)
            
    def mark_cell_identities( self ):
        """Sets properties for cell identities. The overal meristem
        identity difision should be clearly defined in conf. Currently they
        are possible regions:
            * initial cell IC(must be already initialized)
            * central zone CZ (closest cells attached to initial zone, aux insensitive)
            * peripheral zone PZ (one more ring after central zone, aux sensitive, can form
            primodium)
            * primodium zone PrZ (attracts pumps)
            * rest of the meristem
        """
        # finding the initial cell
        t=self.tissue_system.tissue
        cc = cell_centers(t)
        center=self.tissue_system.growth.center
        self.reset_cell_identities()
        PZ_distance =self.tissue_system.const.PZ_absolute_dist#0.7 #120#200
        
        CZ=[]
        PZ=[]
        rr = math.sqrt(self.tissue_system.const.cs_surf_max_surface_before_division)/1.2
        min_dist = float("infinity")
        for i in cc:
            mr0 = pgl.norm( cc[ i ] - center )
            if  mr0 < PZ_distance+rr:
                if mr0 < PZ_distance-rr:
                    CZ.append( i )
                    if mr0 < min_dist:
                        IC = i
                        min_dist = mr0
                else:
                    PZ.append( i )

        #self.tissue_system.tissue.cell_property( cell = IC, property="IC", value=True)
        for c in CZ:
            self.tissue_system.tissue.cell_property( cell = c, property="CZ", value=True)
            self.tissue_system.tissue.cell_property( cell = c, property="NZ", value=False)
        for c in PZ:
            self.tissue_system.tissue.cell_property( cell = c, property="PZ", value=True)
            self.tissue_system.tissue.cell_property( cell = c, property="NZ", value=False)
        self.tissue_system.tissue.cell_property( cell = IC, property="IC", value=True)
        self.tissue_system.tissue.cell_property( cell = IC, property="NZ", value=False)
        
        for c in t.cells(): 
            pr_id = self.tissue_system.tissue.cell_property( cell = c, property="PrC")
            if pr_id > 0:
                self.tissue_system.tissue.cell_property( cell = c, property="PrZ", value=pr_id)
                for i in t.cell_neighbors(c):
                    self.tissue_system.tissue.cell_property( cell = i, property="PrZ", value=pr_id)
                        
        for c in t.cells(): 
            pr_id = self.tissue_system.tissue.cell_property( cell = c, property="PrC_stub")
            if pr_id > 0:
                self.tissue_system.tissue.cell_property( cell = c, property="PrZ_stub", value=pr_id)
                for i in t.cell_neighbors(c):
                    self.tissue_system.tissue.cell_property( cell = i, property="PrZ_stub", value=pr_id)

class RadialGrowth:
    def __init__(self, tissue=None, center = visual.vector(), c_v0=0.01, c_zone=0.8):
        """RadialGrowth constructor.

        """
        self.center = center
        self.c_czone = c_zone
        self.c_v0 = c_v0
        self.tissue=tissue
    
    def apply( self ):
        for vw in self.tissue.wvs():
            p = self.tissue.wv_pos( vw )
            d = p - self.center
            n = d.normalize()
            self.tissue.wv_pos( vw, p+d*self.c_v0*(n/self.c_czone) )
            
    def displacement_vector( self, p ):
        d = p - self.center
        n = d.normalize()
        return p+d*self.c_v0*(n/self.c_czone) 

class TissueSystem:
    """Stub tissue system..
    """
    def __init__( self, tissue, const, visualisation_conf, visualisation  ):
        self.tissue = tissue
        self.const=const
        self.growth=RadialGrowth( tissue=self.tissue, center= pgl.Vector3())
        self.cell_remover = SimulationRemoveCellStrategy2D_1( self, c_remove_2d_radius=1.5 )
        self.frame=0
        self.tissue.time=0
        self.c_save_simulation=True
        self.c_tissue_dir="/home/stymek/mtmp/08-07-10-uniformGrowth/"
        self.visualisation_conf=visualisation_conf
        self.visualisation=visualisation

    def run( self , nbr):
        self.step(nbr)
        
    def play( self, folder=""):
        if not folder: folder=self.c_tissue_dir
        while True:
            self.load_tissue( folder+str(self.frame))
            self.visualisation( self.tissue, self.visualisation_conf, prefix=folder+"/vis/1/")
            self.frame+=1
            
            
    def step( self, nbr=1 ):
        for i in range( nbr ):
            self.frame+=1
            self.tissue.time+=1
            self.growth.apply()
            self.divide_cells()
            self.remove_cells()
            self.update_visualisation()
        
            
    def write_tissue( self, file_name=None ):
        if not file_name: file_name=self.c_tissue_dir
        wtp = WalledTissuePickleWriter( file_name, mode="w",
                               tissue=WalledTissue2IOTissue(self.tissue, id=IntIdGenerator( self.tissue.wv_edges() )),
                               tissue_properties=WalledTissue2IOTissueProperties( self.tissue  ),
                               cell_properties=WalledTissue2IOCellPropertyList( self.tissue  ),
                               wv_properties=WalledTissue2IOEdgePropertyList( self.tissue ),
                               wv_edge_properties=WalledTissue2IOWallPropertyList( self.tissue, id=IntIdGenerator( self.tissue.wv_edges() ) ),
                               description="Tissue with aux and pin, hexagonal, 3sinks appearing in a raw." )
        wtp.write_all()
        print " #: tissue written.."
        
    def load_tissue( self, file_name=None ):
        #if not file_name: file_name=self.c_tissue_dir
        wtpr = WalledTissuePickleReader( file_name, mode="r")
        wtpr.read_tissue()
        self.tissue=IOTissue2WalledTissue( wtpr.tissue, wtpr.wv_properties[ "_positions" ], const=WalledTissueCanalisationExp1() )
        

    def remove_cells( self ):
        for i in self.cell_remover.cells_to_remove():
            self.tissue.remove_cell( cell=i )

            
    def divide_cells( self ):
        ds_surface( self.tissue, dscs_shortest_wall_with_geometric_shrinking, pre=pre_5, post=post_5 )
    


    def update_visualisation( self, 
                             prefix="", **keys ):
        
        self.visualisation(self.tissue, self.visualisation_conf)        
        #for i in cell_centers( self.tissue ).values():
        #    #print i 
        #    a=pd.AIArrow(pos=i, axis=(self.growth.displacement_vector(i)-i)*6., radius=0.007)
        #    #pd.get_scene().add(pgl.Shape(a,pgl.Material( (0,0,0) )))
        pd.instant_update_viewer()
        name = ("%.5d.png") % self.frame
        name = prefix+name
        pgl.Viewer.frameGL.saveImage(name)
        
    def reverse_tissue_if_needed( self ):
        c = self.tissue.cells()[0]
        cwvs = self.tissue.cell2wvs(c)
        cc = cell_center( self.tissue, c)
        #print  (pgl.cross(s.tissue.wv_pos(cwvs[0]) - cc, s.tissue.wv_pos(cwvs[1]) - cc)).z
        return not(0 < (pgl.cross(s.tissue.wv_pos(cwvs[0]) - cc, s.tissue.wv_pos(cwvs[1]) - cc)).z)
        

            

from openalea.mersim.const.const import TissueConst
from openalea.mersim.serial.walled_tissue import  read_walled_tissue
import openalea.plantgl.all as pgl
import  openalea.plantgl.ext.all as pd
from openalea.mersim.gui.tissue import auxin2material5, mark_regions5
from openalea.mersim.gui.tissue import  visualisation_pgl_2D_plain

const=TissueConst()
const.cell_properties ={}
const.wv_edge_properties={}
const.tissue_properties={}


def visualisation( tissue, conf, **keys ):
    pd.SCENES[ 0 ].clear()
    visualisation_pgl_2D_plain( tissue,  max_wall_absolute_thickness=conf["max_wall_absolute_thickness"],
                                                abs_intercellular_space=conf["abs_intercellular_space"],
                                                material_f=conf["material_f"], revers=conf["revers"],
                                                stride=conf["stride"], **keys)


visualisation_conf={
                    "max_wall_absolute_thickness":0.9,
                    "abs_intercellular_space":0.01,
                    "revers":True,
                    "material_f":f_green_material,
                    "prefix":"",
                    "stride": 25,
}

# reading tissue
wt_filename="/home/stymek/mdata/2d.can,graTo0,pumps-stable"
t = read_walled_tissue( file_name=wt_filename, const=const )



#viewer settings
pd.set_instant_update_visualisation_policy( policy = False )
pgl.Viewer.animation( True )
pgl.Viewer.frameGL.setSize(900,900)
pgl.Viewer.frameGL.setBgColor(pgl.Color3(0,0,0))
pgl.Viewer.camera.setOrthographic()
pgl.Viewer.light.enabled=False
pgl.Viewer.display(pd.SCENES[0])     
pgl.Viewer.camera.lookAt( (0,0,-1 ), (0,0,0) )

s = TissueSystem(t, const, visualisation_conf, visualisation)


# preparing divisions and removal
o=[]
oo=[]
for i in t.cells():
    o.append(calculate_cell_surface(t, i))
    oo.append(pgl.norm(cell_center(t,i)))
t.const.cs_surf_max_surface_before_division=max(o)
s.cell_remover.c_remove_2d_radius = max(oo)

# visulaization of tissue
s.update_visualisation()
pd.instant_update_viewer()
