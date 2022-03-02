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
__revision__="$Id: 07-10-17-canalisationWar-smallerTissue,withCenter.py 7875 2010-02-08 18:24:36Z cokelaer $"

from openalea.mersim.tissue.walled_tissue import WalledTissue
from openalea.mersim.const.const import *
from openalea.mersim.tissue.algo.walled_tissue import *
from openalea.mersim.tissue.algo.walled_tissue_division_policies import *
#from openalea.mersim.tissue.algo.walled_tissue_cfd import *
from openalea.mersim.tissue.algo.walled_tissue_dscs import *
from openalea.mersim.serial.walled_tissue import *
from openalea.mersim.gui.tissue import *
from openalea.mersim.physio.canalisation import *
from openalea.mersim.physio.cell_identities import *
#from openalea.mersim.mass_spring.forces import * 
#from openalea.mersim.mass_spring.system import *
from openalea.mersim.tissue.algo.walled_tissue_division_policies import *
from openalea.mersim.tissue.algo.walled_tissue_dscs import *
from openalea.mersim.tissue.algo.walled_tissue_cfd import ds_surface
from openalea.mersim.simulation.remove_cell_strategy import *
import random

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
            
            
            
            
class ContinousPrimsGrowth:
    class Prim:
        def __init__( self, pos, radius ):
            self.pos = pos
            self.radius = radius
            #ts=pd.AISphere()
            #ts.geometry.slices=50
            #ts.visible=False
            #ts=pd.AICylinder()
            #ts.geometry.slices=50
            #ts.visible=False
            
    def __init__( self, profile_f=None, c_remove_radius=5 ):
        self.prims = {}
        self._prim_id = 0
        self.c_initial_radius = 0.2
        self.c_remove_z =profile_f( c_remove_radius )
        self.c_step=0.03
        self.profile_f = profile_f
        
    def add_prim( self, pos ):
        np = pos
        np.z += - self.c_initial_radius 
        self.prims[ self._prim_id ] = ContinousPrimsGrowth.Prim(pos,self.c_initial_radius)
        self._prim_id += 1
        
    def move( self ):
        to_remove = []
        for i in self.prims:
            p = self.prims[ i ]
            if p.pos.z > self.c_remove_z:
                t = pgl.Vector3( p.pos )
                t.z = 0
                n = pgl.norm( t )
                new_z = self.profile_f( n+self.c_step )
                t2 = pgl.Vector3( t )
                t2.normalize()
                t = t+t2*self.c_step
                t.z=new_z
                self.prims[ i ].pos = t
                self.prims[ i ].radius = 0.2-self.prims[ i ].pos.z/10
            else:
                to_remove.append( i )
        for p in to_remove:
            self.prims.pop( p )
        
        

class TissueSystem:
    """Stub tissue system..
    """
    def __init__( self, tissue, const=None ):
        self.tissue = tissue
        self.const=const
        self.phys=Phys2DcanalisationForDynamicTopView3( tissue_system=self )
        self.growth=RadialGrowth( tissue=self.tissue, center= pgl.Vector3())
        self.cell_remover = SimulationRemoveCellStrategy2D_1( self, c_remove_2d_radius=1.5 )
        self.cell_identities =  PhysMarkCellIdentitiesWithFixedRegionsIn2D_2( tissue_system=self)
        self.cont_prims =ContinousPrimsGrowth( profile_f=(lambda x:(-x*x +2.2*2.2)/4.), c_remove_radius = 5)
        self.frame=0
        self.tissue.time=0
        self.c_save_simulation=True
        self.concentration_range=(5,20)
        self.c_prim_min_con = 0
        self.c_prim_max_con = 2000
        
    def loop( self, nbr=3 ):
        while self.frame < nbr:
            self.step()
    
    def f_factor( self, prim ):
        # returns the concentration in prim acording to its position
        d = cell_center( self.tissue, prim ) - pgl.Vector3()
        f = (pgl.norm( d )/(self.cell_remover.c_remove_2d_radius-self.const.PZ_absolute_dist+math.sqrt(self.const.cs_surf_max_surface_before_division)/1.2) )
        return self.c_prim_min_con+max(0, self.c_prim_max_con*f)
    
    def change_conc_in_prim( self ):
        h = {}
        for i in self.tissue.cells():
            if self.tissue.cell_property( i, "PrC" ):
                h[ self.tissue.cell_property( i, "PrC" ) ] = self.f_factor( i )
        for i in self.tissue.cells():
            if self.tissue.cell_property( i, "PrZ" ):
                self.phys.aux(i, h[self.tissue.cell_property( i, "PrZ" )])
            
    def step( self, nbr=1 ):
        for i in range( nbr ):
            #if nbr>1:
            #    self.phys.c_change=float("inf")
            self.tissue.time+=1
            self.cell_identities.apply()
            self.change_conc_in_prim()
            self.phys.step(1, 0)
            self.update_pin_range()
            self.update_conc_range()
            self.update_visualisation()
            self.save_simulation()
            self.growth.apply()
            self.divide_cells()
            self.remove_cells()
            self.cont_prims.move()
           # raw_input()
        
    def save_simulation( self, save_path="/home/stymek/src/openalea/mersim/experiments/simulation", filename=None ):
        if self.c_save_simulation:
           import d
           import pickle
           if not filename: name = ("%.5d") % self.frame
           else: name = filename
           d.write( self.tissue, name="s"+name, path=save_path )
           pickle.dump( self.tissue._wv_edge2properties, file( save_path+"/"+"s"+name+".pickle", "w" ), protocol=2 )
                                                              
    def load_simulation( self, step=0, path="/home/stymek/src/openalea/mersim/experiments/simulation", filename=None, read_pin=True ):
        import pickle                                    
        if not filename:
            name = ("%.5d") % self.step
            filename = "s"+name
        wtpr2 = WalledTissuePickleReader( path+"/"+filename, mode="r")
        wtpr2.read_tissue()
        self.tissue=IOTissue2WalledTissue( wtpr2.tissue, wtpr2.wv_properties[ "_positions" ], const=WalledTissueCanalisationExp1() )
        wtpr2.read_property( "auxin_level" )
        wtpr2.read_property( "PrC" )
        for i in self.tissue.cells():
            for pr in [ "auxin_level", "PrC" ]:
                self.tissue.cell_property( cell=i, property=pr, value=wtpr2.cell_properties[ pr ][ i ] )
        if read_pin:
            try:
                self.tissue._wv_edge2properties=pickle.load(file(path+"/"+filename+".pickle", "r"))
            except IOError:
                self.tissue._wv_edge2properties=pickle.load(file(path+"/"+"s"+str(int(filename[1:]))+".pickle", "r"))
        self.growth.tissue = self.tissue
        self.cell_identities.apply()
        
        
    def play_simulation( self, path="/home/stymek/src/openalea/mersim/experiments/simulation", concentration_range=None, pin_range=None):
        import os
        import os.path
        content = os.listdir(path)
        simulations=[]
        for i in content:
            if os.path.isdir( os.path.join(path, i) ):
                simulations.append( i )
        simulations.sort()
        
        
        for i in simulations:
            print " #loading ", i
            self.load_simulation( path=path, filename=i )
            self.update_conc_range()
            #self.concentration_range=(0,1)
            self.update_visualisation2( concentration_range=self.concentration_range, pin_range=pin_range,filename=i+".png")
        
            
        

    def update_conc_range( self ):
        l=[]
        for i in self.tissue.cells():
            l.append(self.tissue.cell_property( i , "auxin_level"))
        self.concentration_range = (min(l),max(l))
        
    def update_pin_range( self ):
        l=[]
        min = float("inf")
        max = float("-inf")
        for i in self.tissue.cells():
            for n in self.tissue.cell_neighbors( i ):
                v = pin_level( self.tissue, cell_edge=(i,n))
                if v < min:
                    min = v
                if v > max:
                    max = v
        self.pin_range = (min,max)
        
    #def t_d( self, cn, pn ):
    #    self.load_simulation( 48 )
    #    n = self.tissue.cell_neighbors( 1532 )
    #    n=n[0]
    #    for i in self.tissue.cells():
    #        if i != 1532 and i != n:
    #            self.tissue.remove_cell( i )
    #    self.phys.pin( (n,i ), 1. )
    #    self.phys.pin( (i,n ), 0.5 )
    #    self.update_visualisation2( concentration_range=cn, pin_range=pn )

    def remove_cells( self ):
        l = self.cell_remover.cells_to_remove()
        for i in l:
            if self.tissue.cell_property( cell=i, property="PrC" ):
                cc = cell_center( wt=self.tissue, cell=i )
                dir = pgl.Vector3( cc )
                cc = cc*(2.2/pgl.norm( cc ))
                cc.z = -0.2
                self.cont_prims.add_prim( pos=cc )
            self.tissue.remove_cell( cell=i )

    def mark_prim( self, cell, nbr ):
        self.tissue.cell_property( cell, "PrC", nbr )
        self.tissue.cell_property( cell, "PrZ", 1 )
        self.phys.aux( cell, 0 )
        for i in self.tissue.cell_neighbors( cell ):
            self.tissue.cell_property( i, "PrZ", 1 )
            self.phys.aux( i, 0 )
            
    def divide_cells( self ):
        ds_surface( self.tissue, dscs_shortest_wall_with_geometric_shrinking, pre=pre_4, post=post_4 )
    
    #def update_visualisation( self ):
    #    self.frame+=1
    #    pd.SCENES[ 0 ].clear()
    #    self.update_conc_range()
    #    visualisation1( self.tissue, concentration_range=self.concentration_range )
    #    cont_prims_visualisation1( self )
    #    cz=self.cell_remover.c_remove_2d_radius
    #    create_meristem_stem( central_zone=cz+0.2, distance=3, profile_f=(lambda x:(-x*x +(cz+0.2)*(cz+0.2))/4.) )
    #    pd.instant_update_viewer()
    #    pgl.Viewer.frameGL.saveImage(str(self.frame)+".png")
        
    def update_visualisation( self, cell=None, dynamic_concentration_range=True, dynamic_pin_range=True, **keys ):
        self.frame+=1
        pd.SCENES[ 0 ].clear()
        self.update_conc_range()
        self.update_pin_range()
        abs_intercellular_space = 0.01
        if keys.has_key( "concentration_range" ): concentration_range = keys[ "concentration_range" ]
        else:
            if dynamic_concentration_range: concentration_range=self.concentration_range
            else: concentration_range = (0., self.phys.c_aux_max)
        if keys.has_key( "pin_range" ): pin_range = keys[ "pin_range" ]
        else:
            if dynamic_pin_range: pin_range=self.pin_range
            else: pin_range=(0., self.phys.c_pin_max)
        #visualisation_pgl_2D_linear_tissue_aux_pin( self.tissue, concentration_range=concentration_range, pin_range=pin_range, max_wall_absolute_thickness=abs_intercellular_space+0.020, cell_marker_size=0.01, abs_intercellular_space=abs_intercellular_space )
        visualisation_pgl_2D_spherical_aux(self.tissue, concentration_range=concentration_range, cell_marker_size=0.02, marker_displacement=pgl.Vector3(0,0,0.3), c_sphere_radius_factor=0.7)
        #visualisation_pgl_2D_linear_tissue_aux_pin( self.tissue, concentration_range=self.concentration_range, pin_range=self.pin_range, max_wall_absolute_thickness=abs_intercellular_space+0.020, cell_marker_size=0.01, abs_intercellular_space=abs_intercellular_space )
        cz=self.cell_remover.c_remove_2d_radius
        pd.instant_update_viewer()
        name = ("%.5d.png") % self.frame
        pgl.Viewer.frameGL.saveImage(name)
        
    def update_visualisation2( self, cell=None, filename=None, **keys ):
        self.frame+=1
        pd.SCENES[ 0 ].clear()
        self.update_conc_range()
        abs_intercellular_space = 0.01
        if keys.has_key( "concentration_range" ): concentration_range = keys[ "concentration_range" ]
        else: concentration_range = (0., self.phys.c_aux_max)
        if keys.has_key( "pin_range" ): pin_range = keys[ "pin_range" ]
        else: pin_range=(0.1,self.phys.c_pin_max)
        #visualisation_pgl_2D_linear_tissue_aux_pin( self.tissue, concentration_range=concentration_range, pin_range=pin_range, max_wall_absolute_thickness=abs_intercellular_space+0.020, cell_marker_size=0.01, abs_intercellular_space=abs_intercellular_space )
        visualisation_pgl_2D_linear_tissue_aux_pin( self.tissue, concentration_range=concentration_range, pin_range=pin_range, max_wall_absolute_thickness=abs_intercellular_space+0.020, cell_marker_size=0.01, abs_intercellular_space=abs_intercellular_space )
        cz=self.cell_remover.c_remove_2d_radius
        pd.instant_update_viewer()
        if not filename: name = ("%.5d.png") % self.frame
        else: name=filename
        pgl.Viewer.frameGL.saveImage(name)


def check_tissue( tissue ):
    wv2cells={}
    cell2wvs={}
    for i in tissue.cells():
        cell2wvs[ i ] = []
    for i in tissue.wvs():
        wvs2cell[ i ] = []
    for i in tissue.cells():
        cw=tissue.cell2wvs( i )
        for j in cw:
            pass
            
            
        
#wtpr = WalledTissuePickleReader( "/home/stymek/mdata/circ,2D", mode="r")
#circ,2d,4cana
wtpr = WalledTissuePickleReader( "/home/stymek/mdata/2d.can,graTo0,pumps-stable", mode="r")
#wtpr = WalledTissuePickleReader( "/home/stymek/src/openalea/mersim/experiments/simulation/s00148", mode="r")
wtpr.read_tissue()
wt3=IOTissue2WalledTissue( wtpr.tissue, wtpr.wv_properties[ "_positions" ], const=WalledTissueCanalisationExp1() )

s=TissueSystem( wt3, const= WalledTissueDynamicCanalisation() )
s.tissue.const=WalledTissueDynamicCanalisation() 

s.remove_cells()
pd.ASPHERE_PRIMITIVE.slices=20
s.cell_identities.apply()
s.phys.init_pin()
s.phys.init_aux()
s.update_conc_range()
s.update_pin_range()
s.update_visualisation(concentration_range=(0,4500))
pgl.Viewer.animation( True )
pgl.Viewer.camera.lookAt( (0,0,4), (0,0,0) )
s.const.cell_properties.pop("inh")
s.const.cell_properties.pop("innerSink")
s.update_visualisation(concentration_range=s.concentration_range)

