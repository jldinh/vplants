#!/usr/bin/env python
"""Cell identities marking policies.

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
__revision__="$Id: cell_identities.py 7875 2010-02-08 18:24:36Z cokelaer $"

from openalea.mersim.tissue.algo.walled_tissue import *
import openalea.plantgl.all as pgl
import math

class PhysInterface:
    """Interface for physiology process in the tissue.
    """
    def __init__( self, tissue_system=None):
        self.tissue_system = tissue_system
        
    def apply( self ):
        pass


                  
class PhysMarkCellIdentitiesWithDynamicIC(PhysInterface):
    """ Marking cell identities basing on previous step.
    """
    
    def __init__( self, tissue_system=None):
        PhysInterface.__init__( self, tissue_system=tissue_system)
    
    def apply( self ):
        self.reset_cell_identities()
        self.mark_cell_identities()
    
    def reset_cell_identities( self ):
        for c in self.tissue_system.tissue.cells():
            self.tissue_system.tissue.cell_property( cell = c, property="CZ", value=False)
            self.tissue_system.tissue.cell_property( cell = c, property="PZ", value=False)
            self.tissue_system.tissue.cell_property( cell = c, property="NZ", value=True)    
            
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
        self.reset_cell_identities()
        CZ_size =2
        PZ_size =2
        for c in self.tissue_system.tissue.cells():
            if  self.tissue_system.tissue.cell_property( cell = c, property="IC"):
                IC=c 
        CZ = self.tissue_system.tissue.nth_layer_from_cell( cell=IC, distance=CZ_size, smaller_than=True)+[IC]
        PZ = []
        for i in range(PZ_size):
            PZ += self.tissue_system.tissue.nth_layer_from_cell( cell=IC, distance=CZ_size+1+i, smaller_than=False)

        self.tissue_system.tissue.cell_property( cell = IC, property="IC", value=True)
        for c in CZ:
            self.tissue_system.tissue.cell_property( cell = c, property="CZ", value=True)
        for c in PZ:
            self.tissue_system.tissue.cell_property( cell = c, property="PZ", value=True)

class PhysMarkCellIdentitiesWithTopIC(PhysInterface):
    """Marking the cell identities basing only on current geometric information.
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
        self.reset_cell_identities()
        CZ_size =2
        PZ_size =2
        IC= self.tissue_system.tissue.find_top_cell_by_z_coord() 
        CZ = self.tissue_system.tissue.nth_layer_from_cell( cell=IC, distance=CZ_size, smaller_than=True)+[IC]
        PZ = []
        for i in range(PZ_size):
            PZ += self.tissue_system.tissue.nth_layer_from_cell( cell=IC, distance=CZ_size+1+i, smaller_than=False)

        self.tissue_system.tissue.cell_property( cell = IC, property="IC", value=True)
        for c in CZ:
            self.tissue_system.tissue.cell_property( cell = c, property="CZ", value=True)
        for c in PZ:
            self.tissue_system.tissue.cell_property( cell = c, property="PZ", value=True)

class PhysMarkCellIdentitiesWithCentralIC(PhysInterface):
    """Marking the cell identities basing only on current geometric information.
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
        cc = t.cell_centers()
        gc = visual.vector()
        for i in cc.values():
            gc += i
        gc = gc/len( cc )
        gc0 = visual.vector( gc )
        gc0.z = 0
        r = {}
        for i in cc:
            v = gc0 - cc[ i ]
            v.z = 0
            r[ visual.mag( v ) ] = i
        
        d = {"center_cell_id": r[ min(r.keys()) ], "gravity_center":gc} 

        self.reset_cell_identities()
        CZ_size =120 #150
        PZ_size =200 #200
        IC= d[ "center_cell_id" ]
        
        CZ=[]
        PZ=[]
        for i in cc:
            r = cc[ i ] - gc
            r0 = visual.vector(r)
            r0.z = 0
            mr0 = mag( r0 )
            if  mr0 < PZ_size:
                if mr0 < CZ_size:
                    CZ.append( i )
                else:
                    PZ.append( i )

        self.tissue_system.tissue.cell_property( cell = IC, property="IC", value=True)
        for c in CZ:
            self.tissue_system.tissue.cell_property( cell = c, property="CZ", value=True)
        for c in PZ:
            self.tissue_system.tissue.cell_property( cell = c, property="PZ", value=True)

class PhysMarkCellIdentitiesWithFixedRegionsIn2D(PhysInterface):
    """Marking the cell identities basing only on current geometric information.
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
        cc = t.cell_centers()
        center=self.tissue_system.forces["radial_move"].center
        self.reset_cell_identities()
        PZ_distance =150 #200
        
        CZ=[]
        PZ=[]
        rr = math.sqrt(self.tissue_system.const.cs_surf_max_surface_before_division)#/1.5
        min_dist = float("infinity")
        for i in cc:
            mr0 = mag( cc[ i ] - center )
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

class PhysMarkCellIdentitiesWithFixedRegionsIn2D_1(PhysInterface):
    """Marking the cell identities basing only on current geometric information.
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
        PZ_distance =0.5 #120#200
        
        CZ=[]
        PZ=[]
        rr = math.sqrt(self.tissue_system.const.cs_surf_max_surface_before_division)/1.5
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
                for i in t.cell_neighbors(c):
                    self.tissue_system.tissue.cell_property( cell = i, property="PrZ", value=pr_id)

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
                    

