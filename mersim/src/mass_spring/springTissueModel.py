#!/usr/bin/env python

"""springTissueModel.py

Contains the engine of the tissue simulation sytstem. 


:version: 2006-07-28 12:01:15CEST
:author: szymon stoma
"""

import visual
import math
import convexhull
import sets
import random
import pickle
import scipy
import scipy.integrate.odepack



#import PlantGL as pgl 
import openalea.plantgl.all as pgl
from merrysim import *
import walledTissue as w
from const import *
from tissueSystemVisualisation import *
from tissueSystemVisualisationVisual import *
import simulationRemoveCellStrategy
import tools

        

      






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
        PZ_distance =120 #200
        
        CZ=[]
        PZ=[]
        rr = math.sqrt(self.tissue_system.const.cs_surf_max_surface_before_division)/1.5
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
        

class PhysAuxinTransportModel(PhysInterface):
    def __init__(self, tissue_system = None):
        PhysInterface.__init__( self, tissue_system=tissue_system )

    def aux_con( self, cell = None, con=None, nbr=None ):
        if con == None and nbr==None:    
            return self.tissue_system.tissue.cell_property( cell = cell, property="auxin_level") / self.tissue_system.tissue.calculate_cell_surface( cell = cell) 
        else:
            if con == None:
                self.tissue_system.tissue.cell_property( cell = cell, property="auxin_level", value= nbr )
            else:
                self.tissue_system.tissue.cell_property( cell = cell, property="auxin_level", value= con*self.tissue_system.tissue.calculate_cell_surface( cell = cell) )
                
        
    def aux_con_1( self, cell = None, con=None, nbr=None ):
        if con == None and nbr==None:    
            return self.tissue_system.tissue.cell_property( cell = cell, property="auxin_level_1") / self.tissue_system.tissue.calculate_cell_surface( cell = cell) 
        else:
            if con == None:
                self.tissue_system.tissue.cell_property( cell = cell, property="auxin_level_1", value= nbr )
            else:
                self.tissue_system.tissue.cell_property( cell = cell, property="auxin_level_1", value= con*self.tissue_system.calculate_cell_surface( cell = cell) )

    def upd_aux_con_1( self, cell = None, nbr=None ):
        if nbr==None:    
            print " #! upd_aux_con_1: not updated.."
        else:
            self.tissue_system.tissue.cell_property( cell = cell, property="auxin_level_1", value= nbr+self.tissue_system.tissue.cell_property( cell =cell, property="auxin_level_1" ) )

    def upd_aux_con( self, cell = None, nbr=None ):
        if nbr==None:    
            print " #! upd_aux_con_1: not updated.."
        else:
            self.tissue_system.tissue.cell_property( cell = cell, property="auxin_level", value= nbr+self.tissue_system.tissue.cell_property( cell =cell, property="auxin_level" ) )


    def pre_step( self, nbr_step=50 ):
        for i in range( nbr_step ):
            self.apply()
        print self.avr_con()

    def aux( self, cell, value=None ):
        if value == None:    
            return self.tissue_system.tissue.cell_property( cell = cell, property="auxin_level")  
        else:
            self.tissue_system.tissue.cell_property( cell = cell, property="auxin_level", value= value )
    
    def pin( self, cell_edge, value=None ):
        if value == None:    
            s = self.tissue_system.tissue.cell_edge_property( cell_edge = self.tissue_system.tissue.cell_edge_id( cell_edge ), property="pin_level")  
            if cell_edge == self.tissue_system.tissue.cell_edge_id( cell_edge ):
                return s[ 0 ]
            else:
                return s[ 1 ]
        else:
            s = copy.copy( self.tissue_system.tissue.cell_edge_property( cell_edge = self.tissue_system.tissue.cell_edge_id( cell_edge ), property="pin_level") )  
            if cell_edge == self.tissue_system.tissue.cell_edge_id( cell_edge ):
                s[ 0 ]= value
            else:
                s[ 1 ]= value
            self.tissue_system.tissue.cell_edge_property( cell_edge = self.tissue_system.tissue.cell_edge_id( cell_edge ), property="pin_level", value= s )

class PhysAuxinTransportModel0(PhysAuxinTransportModel):
    def __init__(self, tissue_system = None):
        PhysAuxinTransportModel.__init__( self, tissue_system=tissue_system)
        # TODO get rid of system
        self.system = tissue_system
        #for first
        #self.aux_production_in_border = 0.1
        #self.aux_production_in_IC = 0.8
        #self.aux_production_in_close_neigh_of_IC = 0.4
        #self.aux_production_in_prim = 0.4
        #self.aux_production_in_close_neigh_of_prim = 0.2
        #self.nbr_prim=1
        #self.aux_degradation_coef=0.999
        #self.aux_diff_coef = 0.01
        #self.aux_pump_coef = 0.05

        ##nice and 4 sides
        #self.aux_production_in_border = 0.1
        #self.aux_production_in_IC = 0.8
        #self.aux_production_in_close_neigh_of_IC = 0.4
        #self.aux_production_in_prim = 0.3
        #self.aux_production_in_close_neigh_of_prim = 0.2
        #self.nbr_prim=1
        #self.aux_degradation_coef=0.998
        #self.aux_diff_coef = 0.01
        #self.aux_pump_coef = 0.05
        
        #working with IF=6
        #self.aux_production_in_border = 0.1
        #self.aux_production_in_IC = 0.8
        #self.aux_production_in_close_neigh_of_IC = 0.4
        #self.aux_production_in_prim = 0.9
        #self.aux_production_in_close_neigh_of_prim = 0.5
        #self.nbr_prim=1
        #self.aux_degradation_coef=0.998
        #self.aux_conc_for_primordium_forming = 30
        #self.aux_diff_coef = 0.01
        #self.aux_pump_coef = 0.05
        self.init_aux_everythere=1
        self.init_aux_near_IC=4
        
        self.aux_production_in_border = 0.#1
        self.aux_production_in_IC = 2.2
        self.aux_production_in_close_neigh_of_IC = 0.8
        self.aux_production_in_prim = 0.5
        self.aux_production_in_close_neigh_of_prim = 0.05
        self.nbr_prim=1
        self.aux_degradation_coef=0.998
        self.aux_conc_for_primordium_forming = 55
        self.aux_diff_coef = 0.02
        self.aux_pump_coef = 0.08
        self.aux_production_everywhere=0.01
        self.init_aux_everythere=1.5
        self.init_aux_near_IC=5

        #self.init_aux()
        
    def apply( self ):
        self.step( nbr_step=5)
         
    def step( self, nbr_step=1 ):
        self.orient_pumps()
        self.search_for_primodium()
        self.spring_growth_if_under_tension
        for i in range( nbr_step ):
            self.aux_injection()
            self.degrad_aux()
            self.simple_aux_diff_step()
            self.simple_aux_pumping_step()
            #self.system.visualisation.update()

    def search_for_primodium( self ):
        t = self.system.tissue
        pc = []
        for c in t.cells():
            if t.cell_property( cell=c, property="PZ"):
                if t.cell_property( cell=c, property="auxin_level")>self.aux_conc_for_primordium_forming:
                    nL=t.cell_neighbors( cell=c)
                    #t.nth_layer_from_cell( cell=c, distance=5, smaller_than=True)
                    neigh_prim=False
                    for n in  nL:
                        if t.cell_property( cell=n, property="PrC") > 0:
                            neigh_prim=True
                    if not neigh_prim:
                        pc.append( c )    
        self.create_primordiums( primordium_cand=pc )
        
    def create_primordiums( self, primordium_cand=None):
        t = self.system.tissue
        primordium_cand.sort( lambda x, y: cmp( t.cell_property( cell=x, property="auxin_level"),  t.cell_property( cell=y, property="auxin_level")))
        for i in range( len( primordium_cand ) ):
            c = primordium_cand[ i ]
            nL=t.cell_neighbors( cell=c)
            #t.nth_layer_from_cell( cell=c, distance=5, smaller_than=True)
            neigh_prim=False
            for n in  nL:
                if t.cell_property( cell=n, property="PrC") > 0:
                    neigh_prim=True
                    break
            if not neigh_prim:
                t.cell_property( cell=c, property="PrC", value=self.nbr_prim)
                t.cell_property( cell=c, property="PrZ", value=self.nbr_prim)
                for n in t.cell_neighbors( c ):
                    t.cell_property( cell=n, property="PrZ", value=self.nbr_prim)
                self.nbr_prim+=1
    
    def cmp_aux_grad( self, c1, c2):
        t = self.system.tissue
        if t.cell_property( cell=c1, property="auxin_level") < t.cell_property( cell=c2, property="auxin_level"):
            return True
        return False
    
    def degrad_aux(self):
        t = self.system.tissue
        for c in t.cells():
            if t.cell_property(cell= c, property="auxin_level") > 100:
                t.cell_property(cell= c, property="auxin_level", value=t.cell_property(cell= c, property="auxin_level")*0.9)
            t.cell_property(cell= c, property="auxin_level", value=t.cell_property(cell= c, property="auxin_level")*self.aux_degradation_coef)
            
    def init_aux(self):
        t = self.system.tissue
        for c in t.cells():
            if t.cell_property(cell= c, property="IC"):
                IC = c
        for i in range( 20 ):
            for c in t.nth_layer_from_cell( cell = IC, distance=i, smaller_than=True):
                t.cell_property(cell= c, property="auxin_level", value=t.cell_property(cell= c, property="auxin_level")+self.init_aux_everythere)
        for i in range( 6 ):
            for c in t.nth_layer_from_cell( cell = IC, distance=i, smaller_than=True):
                t.cell_property(cell= c, property="auxin_level", value=t.cell_property(cell= c, property="auxin_level")+self.init_aux_near_IC)#12
                
            
        
        
    def orient_pumps( self ):
        t = self.system.tissue
        for cn in t.cell_edges():
            ( c, n ) = cn
            t.cell_edge_property( cell_edge=cn, property="pump_active", value=False )
        for c in t.cells():
            neighL = t.cell_neighbors( cell = c )
            
            N = neighL[ 0 ]
            Naux_con = t.cell_property( cell = N, property="auxin_level")
            for n in neighL:
                if Naux_con < t.cell_property( cell = n, property="auxin_level"):
                    N = n
                    Naux_con = t.cell_property( cell = n, property="auxin_level")
            #print Naux_con, t.cell_property( cell = c, property="auxin_level")
            if Naux_con >  t.cell_property( cell = c, property="auxin_level"):
                t.cell_edge_property( cell_edge=t.cell_edge_id( (c, N)), property="pump_active", value=True )
                t.cell_edge_property( cell_edge=t.cell_edge_id((c, N)), property="pump_direction", value=(c, N))
    
                
        ### ALL PUMPS
        #for cn in t.cell_edges():
        #    ( c, n ) = cn
        #    t.cell_edge_property( cell_edge=cn, property="pump_active", value=True )
        #    if t.cell_property( cell=c, property="auxin_level") <  t.cell_property( cell=n, property="auxin_level"):
        #        t.cell_edge_property( cell_edge=cn, property="pump_direction", value=(c, n))
        #    else:
        #        t.cell_edge_property( cell_edge=cn, property="pump_direction", value=(n, c))
    
    def simple_aux_diff_step( self ):
        """
        Just to test visu..
        """
        for c in self.system.tissue.cells():
            da = 0
            s = 0
            for n in self.system.tissue.cell_neighbors( cell = c ):
                #0.05
                da = self.aux_diff_coef * max(0, self.system.tissue.cell_property( c, "auxin_level") - self.system.tissue.cell_property( n, "auxin_level"))
                self.system.tissue.cell_property( n, "auxin_level_1", da+self.system.tissue.cell_property( n, "auxin_level_1") )
                s += da
            self.system.tissue.cell_property( c, "auxin_level_1", self.system.tissue.cell_property( c, "auxin_level_1")-s)
 
        self.aux_update()
        

    def simple_aux_pumping_step( self ):
        t = self.system.tissue
        for ce in t.cell_edges():
            if t.cell_edge_property( ce, "pump_active" ):
                direction = t.cell_edge_property( ce, "pump_direction" )
                c = direction[ 0 ]
                n = direction[ 1 ]
                da = min(self.aux_pump_coef, t.cell_property( c, "auxin_level")) 
                t.cell_property( n, "auxin_level_1", t.cell_property( n, "auxin_level_1") + da)
                t.cell_property( c, "auxin_level_1",  t.cell_property( c, "auxin_level_1") - da)
        self.aux_update()
        
    def aux_update( self ):
        for c in self.system.tissue.cells():
            self.system.tissue.cell_property( c, "auxin_level",  self.system.tissue.cell_property( c, "auxin_level")+self.system.tissue.cell_property( c, "auxin_level_1") )
            self.system.tissue.cell_property( c, "auxin_level_1", 0)
                
    def aux_injection( self ):
        t = self.system.tissue
        for c in t.cells():
            t.cell_property( c, "auxin_level", t.cell_property( c, "auxin_level")+self.aux_production_everywhere)
            if t.cell_property( c, "border_cell"):
                t.cell_property( c, "auxin_level", t.cell_property( c, "auxin_level")+self.aux_production_in_border)
            if t.cell_property( c, "IC"):
                t.cell_property( c, "auxin_level", t.cell_property( c, "auxin_level")+self.aux_production_in_IC)
                for n in t.nth_layer_from_cell( cell = c ):
                    t.cell_property( n, "auxin_level", t.cell_property( n, "auxin_level")+self.aux_production_in_close_neigh_of_IC)
            if t.cell_property( c, "PrC"):
                t.cell_property( c, "auxin_level", t.cell_property( c, "auxin_level")+self.aux_production_in_prim)
                for n in t.nth_layer_from_cell( cell = c ):
                    t.cell_property( n, "auxin_level", t.cell_property( n, "auxin_level")+self.aux_production_in_close_neigh_of_prim)
            
    def spring_growth_if_under_tension( self ):
        t = self.system.tissue
        for c in t.cells():
            if t.cell_property( cell=c, property="PrZ") > 0:
                for n in nL:
                    for e in t.cell2wvs_edges( cell=n):
                        s = t.wv_edge_id( e )
                        s.spring_growth_if_under_tension( factor=self.const.spring_growth_rate*2 )


class PhysAuxinTransportModel1(PhysAuxinTransportModel):

    def avr_con( self ):
        z = 0
        for i in self.tissue_system.tissue.cells():
            z += self.aux_con( i )
        return z/len(self.tissue_system.tissue.cells())

    def __init__(self, tissue_system = None):
        PhysAuxinTransportModel.__init__( self, tissue_system=tissue_system)
        self.system = tissue_system
        self.nbr_prim=1

        ###
        self.aux_max_con = 100
        
        self.aux_pro_IC_con_coe = 0.5#5
        self.aux_pro_IC_nei_con_coe = 0.3#25
        self.aux_pro_PR_con_coe = 0.6
        self.aux_pro_PR_nei_con_coe = 0.5#1
        self.aux_pro_NZ_con_coe = 0.3
        #auxin_average
        self.aux_pro_exa = 1500
        
        self.aux_deg_NZ_con_coe = 0.995
        
        #names confusing!
        self.aux_ini_NZ_con_exa = 25.5
        self.aux_ini_NZ_gra_con_exa = 0.1
        self.aux_ini_IZ_con_exa = 0
        
        #self.aux_prim_trs_con = 29        
        #self.aux_dif_coe = 0.02
        #self.aux_act_coe = 0.005
        self.aux_dif_coe = 0.02
        self.aux_act_coe = 0.002
        
        self.aux_prim_trs_con = 29
        
        """
        auxin_level == nbr of aux particles in a cell
        auxin_level_1 == change in number of particles of aux in next time step
        """
    def apply( self ):
        self.step( nbr_step=10)
         
    def step( self, nbr_step=1 ):
        #self.aux_injection()
        #self.degrad_aux()
        print self.avr_con()
        self.orient_pumps()
        for i in range( nbr_step ):
            self.aux_injection()
            self.degrad_aux()
            #self.simple_aux_diff_step()
            #self.simple_aux_pumping_step()
            self.aux_update()
            #self.system.visualisation.update()
        #self.search_for_primodium()
            #print " # finishing because of prim creation (step/outOf): ", i, nbr_step    
            #break


    def search_for_primodium( self ):
        t = self.system.tissue
        pc = []
        for c in t.cells():
            if t.cell_property( cell=c, property="PZ"):
                if self.aux_con( cell = c ) > self.aux_prim_trs_con:
                    #nL=t.cell_neighbors( cell=c)
                    nL=t.nth_layer_from_cell( cell=c, distance=6, smaller_than=True)
                    neigh_prim=False
                    for n in  nL:
                        if t.cell_property( cell=n, property="PrC") > 0:
                            neigh_prim=True
                    if not neigh_prim:
                        nL=t.cell_neighbors( cell=c)
                        for n in nL:
                            # for any!!
                            if self.aux_con( cell = n ) > self.aux_prim_trs_con:
                                pc.append( c )
                                break
        return self.create_primordiums( primordium_cand=pc )
        
    def create_primordiums( self, primordium_cand=None):
        t = self.system.tissue
        prim_created = False
        #TODO test sorting
        primordium_cand.sort( lambda x, y: cmp( self.aux_con( cell = y ),  self.aux_con( cell = x ) ))
        for i in range( len( primordium_cand ) ):
            c = primordium_cand[ i ]
            #nL=t.cell_neighbors( cell=c)
            nL=t.nth_layer_from_cell( cell=c, distance=6, smaller_than=True)
            neigh_prim=False
            for n in  nL:
                if t.cell_property( cell=n, property="PrC") > 0:
                    neigh_prim=True
                    break
            if not neigh_prim:
                t.cell_property( cell=c, property="PrC", value=self.nbr_prim)
                t.cell_property( cell=c, property="PrZ", value=self.nbr_prim)
                for n in t.cell_neighbors( c ):
                    t.cell_property( cell=n, property="PrZ", value=self.nbr_prim)
                self.nbr_prim+=1
                prim_created = True
        if prim_created:
            return True
        else:
            return False
    
        
    
    def degrad_aux(self):
        t = self.system.tissue
        for c in t.cells():
            if self.aux_con(cell= c) > self.aux_max_con:
                #self.aux_con(cell= c, con=self.aux_max_con)
                print " #! not pumped out aux.."
            self.aux_con( cell = c, con = self.aux_deg_NZ_con_coe * self.aux_con(cell = c)  )
            #t.cell_property(cell= c, property="auxin_level_1", value=t.cell_property(cell= c, property="auxin_level")*self.aux_degradation_coef)
            
    def init_aux(self):
        t = self.system.tissue
        for c in t.cells():
            if t.cell_property(cell= c, property="IC"):
                IC = c
        #for i in range( 20 ):
        #    for c in t.nth_layer_from_cell( cell = IC, distance=i, smaller_than=True):
        #        self.aux_con(cell= c, con= self.aux_con( cell =c ) + self.aux_ini_NZ_gra_con_exa )
        #for i in range( 10 ):
        #    for c in t.nth_layer_from_cell( cell = IC, distance=i, smaller_than=True):
        #        self.aux_con(cell= c, con= self.aux_con( cell =c ) + self.aux_ini_IZ_con_exa)
        #        
        for c in t.cells():
            self.aux_con(cell= c, con= self.aux_con( cell =c ) + self.aux_ini_NZ_con_exa) # +random.random() )
                       
    def orient_pumps( self ):
        t = self.system.tissue
        for cn in t.cell_edges():
            ( c, n ) = cn
            t.cell_edge_property( cell_edge=cn, property="pump_active", value=False )
        for c in t.cells():
            neighL = t.cell_neighbors( cell = c )
            #d = {}
            N = neighL[ 0 ]
            Naux_con = self.aux_con( cell = N )
            for n in neighL:
                if Naux_con < self.aux_con( cell = n):
                    N = n
                    Naux_con = self.aux_con( cell = n)
            #print Naux_con, t.cell_property( cell = c, property="auxin_level")
            if Naux_con >  self.aux_con( cell = c):
                t.cell_edge_property( cell_edge=t.cell_edge_id( (c, N)), property="pump_active", value=True )
                t.cell_edge_property( cell_edge=t.cell_edge_id((c, N)), property="pump_direction", value=(c, N))
    
    def simple_aux_diff_step( self ):
        """
        Just to test visu..
        """
        for c in self.system.tissue.cells():
            da = 0
            s = 0
            for n in self.system.tissue.cell_neighbors( cell = c ):
                #0.05
                da = self.aux_dif_coe * max(0, self.aux_con( c ) - self.aux_con( n ) ) * self.tissue_system.tissue.calculate_cell_surface( cell=c )
                self.system.tissue.cell_property( n, "auxin_level_1", da+self.system.tissue.cell_property( n, "auxin_level_1") )
                s += da
            self.system.tissue.cell_property( c, "auxin_level_1", self.system.tissue.cell_property( c, "auxin_level_1")-s)
 

    def simple_aux_pumping_step( self ):
        t = self.system.tissue
        for ce in t.cell_edges():
            if t.cell_edge_property( ce, "pump_active" ):
                direction = t.cell_edge_property( ce, "pump_direction" )
                c = direction[ 0 ]
                n = direction[ 1 ]
                da =  self.aux_act_coe *  t.cell_property( c, "auxin_level" )
                t.cell_property( n, "auxin_level_1", t.cell_property( n, "auxin_level_1") + da)
                t.cell_property( c, "auxin_level_1",  t.cell_property( c, "auxin_level_1") - da)
        
    def aux_update( self ):
        for c in self.system.tissue.cells():
            if self.system.tissue.cell_property( c, "auxin_level")-self.system.tissue.cell_property( c, "auxin_level_1")<0:
                print " #: insufficient aux in cell ", c, "deficit:",  self.system.tissue.cell_property( c, "auxin_level") - self.system.tissue.cell_property( c, "auxin_level_1")
                self.system.tissue.cell_property( c, "auxin_level_1", value=self.system.tissue.cell_property( c, "auxin_level") )  
            self.system.tissue.cell_property( c, "auxin_level",  self.system.tissue.cell_property( c, "auxin_level")+self.system.tissue.cell_property( c, "auxin_level_1") )
            self.system.tissue.cell_property( c, "auxin_level_1", 0)
                
    def aux_injection( self ):
        t = self.system.tissue
        for c in t.cells():
            s = self.aux_pro_exa*t.calculate_cell_surface( cell=c )/self.system.const.cs_surf_max_surface_before_division
            
            if t.cell_property( c, "IC"):
                self.aux_con( cell=c, nbr=s*self.aux_pro_IC_con_coe+t.cell_property( cell=c, property="auxin_level") )
                for n in t.nth_layer_from_cell( cell = c ):
                    self.aux_con( cell=n, nbr=s*self.aux_pro_IC_nei_con_coe+t.cell_property( cell=n, property="auxin_level") )
            if t.cell_property( c, "PrC"):
                self.aux_con( cell=c, nbr=s*self.aux_pro_PR_con_coe+t.cell_property( cell=c, property="auxin_level") )
                for n in t.nth_layer_from_cell( cell = c ):
                    self.aux_con( cell=n, nbr=s*self.aux_pro_PR_nei_con_coe+t.cell_property( cell=n, property="auxin_level") )
            ##if t.cell_property( c, "IC"):
            ##    self.aux_con( cell=c, nbr=s*self.aux_pro_IC_con_coe+t.cell_property( cell=c, property="auxin_level") )
            ##    for n in t.nth_layer_from_cell( cell = c ):
            ##        self.aux_con( cell=n, nbr=s*self.aux_pro_IC_nei_con_coe+t.cell_property( cell=n, property="auxin_level") )
            self.aux_con( cell=c, nbr=s*self.aux_pro_NZ_con_coe+t.cell_property( cell=c, property="auxin_level") )


class PhysAuxinTransportModel2(PhysAuxinTransportModel):
    def __init__(self, tissue_system = None):
        PhysAuxinTransportModel.__init__( self, tissue_system=tissue_system)
        self.system = tissue_system
        self.nbr_prim=1

        ###
        self.aux_max_con = 100
        
        self.aux_pro_IC_con_coe = 0.6#-3.0#5
        self.aux_pro_IC_nei_con_coe = 0.3#-1.5#25
        self.aux_pro_PR_con_coe = 0#-.4
        self.aux_pro_PR_nei_con_coe = 0#1
        self.aux_pro_NZ_con_coe = 0.1
        #auxin_average
        self.aux_pro_exa = 1000
        
        self.aux_deg_NZ_con_coe = 0.9998
        self.aux_deg_PrC_con_coe = 0.98
        self.aux_deg_PrC_nei_con_coe = 0.98
        self.aux_deg_IC_con_coe = 0.99
        self.aux_deg_IC_nei_con_coe = 0.99
        
        #names confusing!
        self.aux_ini_NZ_con_exa = 16.5
        self.aux_ini_NZ_gra_con_exa = -0.
        self.aux_ini_IZ_con_exa = 0
        
        self.aux_dif_coe = 0.008
        self.aux_act_coe = 0.00#4
        
        self.aux_prim_trs_con = 18
        
        """
        auxin_level == nbr of aux particles in a cell
        auxin_level_1 == change in number of particles of aux in next time step
        """
    def apply( self ):
        self.step( nbr_step=10)
         
    def step( self, nbr_step=1 ):
        #self.degrad_aux()
        #self.aux_injection()
        #self.aux_update()
        self.orient_pumps()
        print " #average auxin level: ", self.avr_con()
        for i in range( nbr_step ):
            #raw_input()
            for i in range( 1 ):
                self.degrad_aux()
                self.aux_injection()
                self.simple_aux_diff_step()
                self.simple_aux_pumping_step()
                self.aux_update()
                #self.system.visualisation.update()
        self.search_for_primodium()
                #print " # finishing because of prim creation (step/outOf): ", i, nbr_step    
                #break

    def search_for_primodium( self ):
        t = self.system.tissue
        pc = []
        for c in t.cells():
            if t.cell_property( cell=c, property="PZ"):
                if self.aux_con( cell = c ) > self.aux_prim_trs_con:
                    #nL=t.cell_neighbors( cell=c)
                    nL=t.nth_layer_from_cell( cell=c, distance=3, smaller_than=True)
                    neigh_prim=False
                    for n in  nL:
                        if t.cell_property( cell=n, property="PrC") > 0:
                            neigh_prim=True
                    if not neigh_prim:
                        nL=t.cell_neighbors( cell=c)
                        for n in nL:
                            # for any!!
                            if self.aux_con( cell = n ) > self.aux_prim_trs_con:
                                pc.append( c )
                                break
        return self.create_primordiums( primordium_cand=pc )
        
    def create_primordiums( self, primordium_cand=None):
        t = self.system.tissue
        prim_created = False
        #TODO test sorting
        primordium_cand.sort( lambda x, y: cmp( self.aux_con( cell = y ),  self.aux_con( cell = x ) ))
        for i in range( len( primordium_cand ) ):
            c = primordium_cand[ i ]
            #nL=t.cell_neighbors( cell=c)
            nL=t.nth_layer_from_cell( cell=c, distance=3, smaller_than=True)
            neigh_prim=False
            for n in  nL:
                if t.cell_property( cell=n, property="PrC") > 0:
                    neigh_prim=True
                    break
            if not neigh_prim:
                t.cell_property( cell=c, property="PrC", value=self.nbr_prim)
                t.cell_property( cell=c, property="PrZ", value=self.nbr_prim)
                for n in t.cell_neighbors( c ):
                    t.cell_property( cell=n, property="PrZ", value=self.nbr_prim)
                self.nbr_prim+=1
                prim_created = True
        if prim_created:
            return True
        else:
            return False
    
    
    def degrad_aux(self):
        t = self.system.tissue
        for c in t.cells():
            if self.aux_con(cell= c) > self.aux_max_con:
                self.aux_con(cell= c, con=self.aux_max_con)
                print " #pumped out aux.."
            self.aux_con( cell = c, con = self.aux_deg_NZ_con_coe * self.aux_con(cell = c)  )
            if t.cell_property( c, "PrC"):
                self.aux_con( cell = c, con = self.aux_deg_PrC_con_coe * self.aux_con(cell = c)  )
                for n in t.nth_layer_from_cell( cell = c ):
                    self.aux_con( cell = n, con = self.aux_deg_PrC_nei_con_coe * self.aux_con(cell = n)  )
            #if t.cell_property( c, "IC"):
            #    self.aux_con( cell = c, con = self.aux_deg_IC_con_coe * self.aux_con(cell = c)  )
            #    for n in t.nth_layer_from_cell( cell = c ):
            #        self.aux_con( cell = n, con = self.aux_deg_IC_nei_con_coe * self.aux_con(cell = c)  )
            
    def init_aux(self):
        t = self.system.tissue
        for c in t.cells():
            if t.cell_property(cell= c, property="IC"):
                IC = c
        for i in range( 20 ):
            for c in t.nth_layer_from_cell( cell = IC, distance=i, smaller_than=True):
                self.aux_con(cell= c, con= self.aux_con( cell =c ) + self.aux_ini_NZ_gra_con_exa )
        #for i in range( 10 ):
        #    for c in t.nth_layer_from_cell( cell = IC, distance=i, smaller_than=True):
        #        self.aux_con(cell= c, con= self.aux_con( cell =c ) + self.aux_ini_IZ_con_exa)
        #        
        for c in t.cells():
            self.aux_con(cell= c, con= self.aux_con( cell =c ) + self.aux_ini_NZ_con_exa ) #+random.random()
                       
    def orient_pumps( self ):
        t = self.system.tissue
        for cn in t.cell_edges():
            ( c, n ) = cn
            t.cell_edge_property( cell_edge=cn, property="pump_active", value=False )
        for c in t.cells():
            neighL = t.cell_neighbors( cell = c )
            
            N = neighL[ 0 ]
            Naux_con = self.aux_con( cell = N )
            for n in neighL:
                if Naux_con > self.aux_con( cell = n):
                    N = n
                    Naux_con = self.aux_con( cell = n)
            #print Naux_con, t.cell_property( cell = c, property="auxin_level")
            if Naux_con <  self.aux_con( cell = c):
                t.cell_edge_property( cell_edge=t.cell_edge_id( (c, N)), property="pump_active", value=True )
                t.cell_edge_property( cell_edge=t.cell_edge_id((c, N)), property="pump_direction", value=(c, N))
    
    def simple_aux_diff_step( self ):
        """
        Just to test visu..
        """
        for c in self.system.tissue.cells():
            da = 0
            s = 0
            for n in self.system.tissue.cell_neighbors( cell = c ):
                #0.05
                da = self.aux_dif_coe * max(0, self.aux_con( c ) - self.aux_con( n ) ) * self.tissue_system.tissue.calculate_cell_surface( cell=c )
                self.system.tissue.cell_property( n, "auxin_level_1", da+self.system.tissue.cell_property( n, "auxin_level_1") )
                s += da
            self.system.tissue.cell_property( c, "auxin_level_1", self.system.tissue.cell_property( c, "auxin_level_1")-s)
 

    def simple_aux_pumping_step( self ):
        t = self.system.tissue
        for ce in t.cell_edges():
            if t.cell_edge_property( ce, "pump_active" ):
                direction = t.cell_edge_property( ce, "pump_direction" )
                c = direction[ 0 ]
                n = direction[ 1 ]
                da =  self.aux_act_coe *  t.cell_property( c, "auxin_level" )
                t.cell_property( n, "auxin_level_1", t.cell_property( n, "auxin_level_1") + da)
                t.cell_property( c, "auxin_level_1",  t.cell_property( c, "auxin_level_1") - da)
        
    def aux_update( self ):
        for c in self.system.tissue.cells():
            if self.system.tissue.cell_property( c, "auxin_level")-self.system.tissue.cell_property( c, "auxin_level_1")<0:
                print " #: insufficient aux in cell ", c, "deficit:",  self.system.tissue.cell_property( c, "auxin_level") - self.system.tissue.cell_property( c, "auxin_level_1")
                self.system.tissue.cell_property( c, "auxin_level_1", value=self.system.tissue.cell_property( c, "auxin_level") )  
            self.system.tissue.cell_property( c, "auxin_level",  self.system.tissue.cell_property( c, "auxin_level")+self.system.tissue.cell_property( c, "auxin_level_1") )
            self.system.tissue.cell_property( c, "auxin_level_1", 0)
                
    def aux_injection( self ):
        t = self.system.tissue
        for c in t.cells():
            s = self.aux_pro_exa*t.calculate_cell_surface( cell=c )/self.system.const.cs_surf_max_surface_before_division
            
            #if t.cell_property( c, "IC"):
            #    self.aux_con( cell=c, nbr=s*self.aux_pro_IC_con_coe+t.cell_property( cell=c, property="auxin_level") )
            #    for n in t.nth_layer_from_cell( cell = c ):
            #        self.aux_con( cell=n, nbr=s*self.aux_pro_IC_nei_con_coe+t.cell_property( cell=n, property="auxin_level") )
            if t.cell_property( c, "PrC"):
                t.cell_property( cell=c, property="auxin_level_1", value=s*self.aux_pro_PR_con_coe+t.cell_property( cell=c, property="auxin_level_1") ) 
                for n in t.nth_layer_from_cell( cell = c ):
                    t.cell_property( cell=n, property="auxin_level_1", value=s*self.aux_pro_PR_nei_con_coe+t.cell_property( cell=n, property="auxin_level_1") )
            if t.cell_property( c, "IC"):
                t.cell_property( cell=c, property="auxin_level_1", value=s*self.aux_pro_IC_con_coe+t.cell_property( cell=c, property="auxin_level_1") )
                for n in t.nth_layer_from_cell( cell = c ):
                    t.cell_property( cell=n, property="auxin_level_1", value=s*self.aux_pro_IC_nei_con_coe+t.cell_property( cell=n, property="auxin_level_1") )
            t.cell_property( cell=c, property="auxin_level_1", value=s*self.aux_pro_NZ_con_coe+t.cell_property( cell=c, property="auxin_level_1") )

    def avr_con( self ):
        z = 0
        for i in self.tissue_system.tissue.cells():
            z += self.aux_con( i )
        return z/len(self.tissue_system.tissue.cells())        


class PhysAuxinTransportModel3(PhysAuxinTransportModel):

    def avr_con( self ):
        z = 0
        k=0
        for i in self.tissue_system.tissue.cells():
            z += self.aux_con( i )
            k += self.tissue_system.tissue.cell_property( cell=i, property="auxin_level")
        return (z/len(self.tissue_system.tissue.cells()), k/len(self.tissue_system.tissue.cells()))

    def __init__(self, tissue_system = None):
        PhysAuxinTransportModel.__init__( self, tissue_system=tissue_system)
        self.system = tissue_system
        self.nbr_prim=1

        ###
        self.aux_max_con = 100
        
        self.aux_pro_IC_con_coe = 0.5#5
        self.aux_pro_IC_nei_con_coe = 0.3#25
        self.aux_pro_PR_con_coe = 0.6
        self.aux_pro_PR_nei_con_coe = 0.5#1
        self.aux_pro_NZ_con_coe = 0.3
        #auxin_average
        self.aux_pro_exa = 1500
        
        self.aux_deg_NZ_con_coe = 0.995
        
        #names confusing!
        self.aux_ini_NZ_con_exa = 29.5
        self.aux_ini_NZ_gra_con_exa = 0.1
        self.aux_ini_IZ_con_exa = 0
  
        self.aux_dif_coe = 0.02
        self.aux_act_coe = 0.005
        
        self.aux_prim_trs_con = 30
        
        self.h = 1
        
        """
        auxin_level == nbr of aux particles in a cell
        auxin_level_1 == change in number of particles of aux
        """
    def apply( self ):
        self.step( nbr_step=5, precision=0.5)
         
    def step( self, nbr_step=1, precision=1 ):
        self.h = precision
        print self.avr_con()
        self.search_for_primodium()
        self.degrad_aux()
        self.aux_injection()
        self.aux_update()
        self.orient_pumps()
        for i in range( nbr_step/precision ):
            self.aux_injection()
            self.degrad_aux()
            self.simple_aux_diff_step()
            self.simple_aux_pumping_step()
            self.aux_update()
            #raw_input()
            #self.system.visualisation.update()
            #print " # finishing because of prim creation (step/outOf): ", i, nbr_step    
            #break


    def search_for_primodium( self ):
        t = self.system.tissue
        pc = []
        for c in t.cells():
            if t.cell_property( cell=c, property="PZ"):
                if self.aux_con( cell = c ) > self.aux_prim_trs_con:
                    #nL=t.cell_neighbors( cell=c)
                    nL=t.nth_layer_from_cell( cell=c, distance=6, smaller_than=True)
                    neigh_prim=False
                    for n in  nL:
                        if t.cell_property( cell=n, property="PrC") > 0:
                            neigh_prim=True
                    if not neigh_prim:
                        nL=t.cell_neighbors( cell=c)
                        for n in nL:
                            # for any!!
                            if self.aux_con( cell = n ) > self.aux_prim_trs_con:
                                pc.append( c )
                                break
        return self.create_primordiums( primordium_cand=pc )
        
    def create_primordiums( self, primordium_cand=None):
        t = self.system.tissue
        prim_created = False
        #TODO test sorting
        primordium_cand.sort( lambda x, y: cmp( self.aux_con( cell = y ),  self.aux_con( cell = x ) ))
        for i in range( len( primordium_cand ) ):
            c = primordium_cand[ i ]
            #nL=t.cell_neighbors( cell=c)
            nL=t.nth_layer_from_cell( cell=c, distance=6, smaller_than=True)
            neigh_prim=False
            for n in  nL:
                if t.cell_property( cell=n, property="PrC") > 0:
                    neigh_prim=True
                    break
            if not neigh_prim:
                t.cell_property( cell=c, property="PrC", value=self.nbr_prim)
                t.cell_property( cell=c, property="PrZ", value=self.nbr_prim)
                for n in t.cell_neighbors( c ):
                    t.cell_property( cell=n, property="PrZ", value=self.nbr_prim)
                self.nbr_prim+=1
                prim_created = True
        if prim_created:
            return True
        else:
            return False
    
        
    
    def degrad_aux(self):
        t = self.system.tissue
        for c in t.cells():
            if self.aux_con(cell= c) > self.aux_max_con:
                self.aux_con(cell= c, con=self.aux_max_con)
                print " #! degrad_aux: pumped out aux.."
            #d1 = self.aux_con( cell=c )*t.calculate_cell_surface( cell=c ) 
            #d2 = self.aux_deg_NZ_con_coe * self.aux_con( cell=c ) * t.calculate_cell_surface(cell=c)
            #d = d1 - d2
            d = self.aux_con( cell=c )*t.calculate_cell_surface( cell=c )*( 1 - self.aux_deg_NZ_con_coe )
            if d < 0:
                print " #! degradation do not degradate.."
            self.upd_aux_con_1( cell = c, nbr = -d )
            #t.cell_property(cell= c, property="auxin_level_1", value=t.cell_property(cell= c, property="auxin_level")*self.aux_degradation_coef)
            
    def init_aux(self):
        t = self.system.tissue
        for c in t.cells():
            if t.cell_property(cell= c, property="IC"):
                IC = c
        #for i in range( 20 ):
        #    for c in t.nth_layer_from_cell( cell = IC, distance=i, smaller_than=True):
        #        self.aux_con(cell= c, con= self.aux_con( cell =c ) + self.aux_ini_NZ_gra_con_exa )
        #for i in range( 10 ):
        #    for c in t.nth_layer_from_cell( cell = IC, distance=i, smaller_than=True):
        #        self.aux_con(cell= c, con= self.aux_con( cell =c ) + self.aux_ini_IZ_con_exa)
        #        
        for c in t.cells():
            self.aux_con(cell= c, con= self.aux_con( cell =c ) + self.aux_ini_NZ_con_exa +random.random() )
                       
    def orient_pumps( self ):
        t = self.system.tissue
        for cn in t.cell_edges():
            ( c, n ) = cn
            t.cell_edge_property( cell_edge=cn, property="pump_active", value=False )
        for c in t.cells():
            neighL = t.cell_neighbors( cell = c )
            #d = {}
            N = neighL[ 0 ]
            Naux_con = self.aux_con( cell = N )
            for n in neighL:
                if Naux_con < self.aux_con( cell = n):
                    N = n
                    Naux_con = self.aux_con( cell = n)
            #print Naux_con, t.cell_property( cell = c, property="auxin_level")
            if Naux_con >  self.aux_con( cell = c):
                t.cell_edge_property( cell_edge=t.cell_edge_id( (c, N)), property="pump_active", value=True )
                t.cell_edge_property( cell_edge=t.cell_edge_id((c, N)), property="pump_direction", value=(c, N))
    
    def simple_aux_diff_step( self ):
        """
        Just to test visu..
        """
        for c in self.system.tissue.cells():
            da = 0
            s = 0
            for n in self.system.tissue.cell_neighbors( cell = c ):
                da = self.aux_dif_coe * max(0, self.aux_con( c ) - self.aux_con( n ) ) * self.tissue_system.tissue.calculate_cell_surface( cell=c )
                self.upd_aux_con_1( cell=n, nbr=da )
                s += da
            self.upd_aux_con_1( cell=c,  nbr=-s)
 

    def simple_aux_pumping_step( self ):
        t = self.system.tissue
        for ce in t.cell_edges():
            if t.cell_edge_property( ce, "pump_active" ):
                direction = t.cell_edge_property( ce, "pump_direction" )
                c = direction[ 0 ]
                n = direction[ 1 ]
                da =  self.aux_act_coe *  t.cell_property( c, "auxin_level" )
                self.upd_aux_con_1( cell=n,  nbr=da)
                self.upd_aux_con_1( cell=c, nbr=-da)
        
    def aux_update( self ):
        for c in self.system.tissue.cells():
            if self.system.tissue.cell_property( c, "auxin_level")+self.h*self.system.tissue.cell_property( c, "auxin_level_1")<0:
                print " #: insufficient aux in cell ", c, "deficit:",  self.system.tissue.cell_property( c, "auxin_level") + self.system.tissue.cell_property( c, "auxin_level_1")
                self.system.tissue.cell_property( c, "auxin_level_1", value=-self.system.tissue.cell_property( c, "auxin_level") )  
            self.upd_aux_con( cell=c, nbr= self.h*self.system.tissue.cell_property( c, "auxin_level_1") )
            self.system.tissue.cell_property( c, "auxin_level_1", 0)
                
    def aux_injection( self ):
        t = self.system.tissue
        for c in t.cells():
            s = self.aux_pro_exa*t.calculate_cell_surface( cell=c )/self.system.const.cs_surf_max_surface_before_division
            ###if t.cell_property( c, "IC"):
            ###    self.aux_con( cell=c, nbr=s*self.aux_pro_IC_con_coe+t.cell_property( cell=c, property="auxin_level") )
            ###    for n in t.nth_layer_from_cell( cell = c ):
            ###        self.aux_con( cell=n, nbr=s*self.aux_pro_IC_nei_con_coe+t.cell_property( cell=n, property="auxin_level") )
            ###if t.cell_property( c, "PrC"):
            ###    self.aux_con( cell=c, nbr=s*self.aux_pro_PR_con_coe+t.cell_property( cell=c, property="auxin_level") )
            ###    for n in t.nth_layer_from_cell( cell = c ):
            ###        self.aux_con( cell=n, nbr=s*self.aux_pro_PR_nei_con_coe+t.cell_property( cell=n, property="auxin_level") )
            ##if t.cell_property( c, "IC"):
            ##    self.aux_con( cell=c, nbr=s*self.aux_pro_IC_con_coe+t.cell_property( cell=c, property="auxin_level") )
            ##    for n in t.nth_layer_from_cell( cell = c ):
            ##        self.aux_con( cell=n, nbr=s*self.aux_pro_IC_nei_con_coe+t.cell_property( cell=n, property="auxin_level") )
            self.upd_aux_con_1( cell=c, nbr=s*self.aux_pro_NZ_con_coe )





class PhysAuxinTransportModel4(PhysAuxinTransportModel):
    """Diffusion + destroying in prims
    """
    def avr_con( self ):
        z = 0
        k=0
        for i in self.tissue_system.tissue.cells():
            z += self.aux_con( i )
            k += self.tissue_system.tissue.cell_property( cell=i, property="auxin_level")
        return (z/len(self.tissue_system.tissue.cells()), k/len(self.tissue_system.tissue.cells()))

    def __init__(self, tissue_system = None):
        PhysAuxinTransportModel.__init__( self, tissue_system=tissue_system)
        self.system = tissue_system
        self.nbr_prim=1

        ###
        self.aux_max_con = 100
        
        self.aux_pro_IC_con_coe = 0.5#5
        self.aux_pro_IC_nei_con_coe = 0.3#25
        self.aux_pro_PR_con_coe = -0.5
        self.aux_pro_PR_nei_con_coe = -0.3#1
        self.aux_pro_NZ_con_coe = 0.3
        #auxin_average
        self.aux_pro_exa = 1500
        
        self.aux_deg_NZ_con_coe = 0.996
        
        #names confusing!
        self.aux_ini_NZ_con_exa = 34
        self.aux_ini_NZ_gra_con_exa = 0.1
        self.aux_ini_IZ_con_exa = 0
  
        self.aux_dif_coe = 0.03
        self.aux_act_coe = 0.005
        
        self.aux_prim_trs_con = 35
        
        self.h = 1
        
        """
        auxin_level == nbr of aux particles in a cell
        auxin_level_1 == change in number of particles of aux
        """
    def apply( self ):
        self.step( nbr_step=20, precision=1)
         
    def step( self, nbr_step=1, precision=1 ):
        self.h = precision
        print self.avr_con()
        self.search_for_primodium()
        #self.degrad_aux()
        #self.aux_injection()
        #self.aux_update()
        #self.orient_pumps()
        for i in range( nbr_step/precision ):
            self.aux_injection()
            self.degrad_aux()
            self.simple_aux_diff_step()
            self.simple_aux_pumping_step()
            self.aux_update()
            #raw_input()
            #self.system.visualisation.update()
            #print " # finishing because of prim creation (step/outOf): ", i, nbr_step    
            #break


    def search_for_primodium( self ):
        t = self.system.tissue
        pc = []
        for c in t.cells():
            if t.cell_property( cell=c, property="PZ"):
                if self.aux_con( cell = c ) > self.aux_prim_trs_con:
                    #nL=t.cell_neighbors( cell=c)
                    nL=t.nth_layer_from_cell( cell=c, distance=2, smaller_than=True)
                    neigh_prim=False
                    for n in  nL:
                        if t.cell_property( cell=n, property="PrC") > 0:
                            neigh_prim=True
                    if not neigh_prim:
                        nL=t.cell_neighbors( cell=c)
                        for n in nL:
                            # for any!!
                            if self.aux_con( cell = n ) > self.aux_prim_trs_con:
                                pc.append( c )
                                break
        return self.create_primordiums( primordium_cand=pc )
        
    def create_primordiums( self, primordium_cand=None):
        t = self.system.tissue
        prim_created = False
        #TODO test sorting
        primordium_cand.sort( lambda x, y: cmp( self.aux_con( cell = y ),  self.aux_con( cell = x ) ))
        for i in range( len( primordium_cand ) ):
            c = primordium_cand[ i ]
            #nL=t.cell_neighbors( cell=c)
            nL=t.nth_layer_from_cell( cell=c, distance=2, smaller_than=True)
            neigh_prim=False
            for n in  nL:
                if t.cell_property( cell=n, property="PrC") > 0:
                    neigh_prim=True
                    break
            if not neigh_prim:
                t.cell_property( cell=c, property="PrC", value=self.nbr_prim)
                t.cell_property( cell=c, property="PrZ", value=self.nbr_prim)
                for n in t.cell_neighbors( c ):
                    t.cell_property( cell=n, property="PrZ", value=self.nbr_prim)
                self.nbr_prim+=1
                prim_created = True
        if prim_created:
            return True
        else:
            return False
    
        
    
    def degrad_aux(self):
        t = self.system.tissue
        for c in t.cells():
            if self.aux_con(cell= c) > self.aux_max_con:
                self.aux_con(cell= c, con=self.aux_max_con)
                print " #! degrad_aux: pumped out aux.."
            #d1 = self.aux_con( cell=c )*t.calculate_cell_surface( cell=c ) 
            #d2 = self.aux_deg_NZ_con_coe * self.aux_con( cell=c ) * t.calculate_cell_surface(cell=c)
            #d = d1 - d2
            d = self.aux_con( cell=c )*t.calculate_cell_surface( cell=c )*( 1 - self.aux_deg_NZ_con_coe )
            if d < 0:
                print " #! degradation do not degradate.."
            self.upd_aux_con_1( cell = c, nbr = -d )
            #t.cell_property(cell= c, property="auxin_level_1", value=t.cell_property(cell= c, property="auxin_level")*self.aux_degradation_coef)
            
    def init_aux(self):
        t = self.system.tissue
        for c in t.cells():
            if t.cell_property(cell= c, property="IC"):
                IC = c
        #for i in range( 20 ):
        #    for c in t.nth_layer_from_cell( cell = IC, distance=i, smaller_than=True):
        #        self.aux_con(cell= c, con= self.aux_con( cell =c ) + self.aux_ini_NZ_gra_con_exa )
        #for i in range( 10 ):
        #    for c in t.nth_layer_from_cell( cell = IC, distance=i, smaller_than=True):
        #        self.aux_con(cell= c, con= self.aux_con( cell =c ) + self.aux_ini_IZ_con_exa)
        #        
        for c in t.cells():
            self.aux_con(cell= c, con= self.aux_con( cell =c ) + self.aux_ini_NZ_con_exa) #+random.random() )
                       
    def orient_pumps( self ):
        t = self.system.tissue
        for cn in t.cell_edges():
            ( c, n ) = cn
            t.cell_edge_property( cell_edge=cn, property="pump_active", value=False )
        for c in t.cells():
            neighL = t.cell_neighbors( cell = c )
            #d = {}
            N = neighL[ 0 ]
            Naux_con = self.aux_con( cell = N )
            for n in neighL:
                if Naux_con < self.aux_con( cell = n):
                    N = n
                    Naux_con = self.aux_con( cell = n)
            #print Naux_con, t.cell_property( cell = c, property="auxin_level")
            if Naux_con >  self.aux_con( cell = c):
                t.cell_edge_property( cell_edge=t.cell_edge_id( (c, N)), property="pump_active", value=True )
                t.cell_edge_property( cell_edge=t.cell_edge_id((c, N)), property="pump_direction", value=(c, N))
    
    def simple_aux_diff_step( self ):
        """
        Just to test visu..
        """
        for c in self.system.tissue.cells():
            da = 0
            s = 0
            for n in self.system.tissue.cell_neighbors( cell = c ):
                da = self.aux_dif_coe * max(0, self.aux_con( c ) - self.aux_con( n ) ) * self.tissue_system.tissue.calculate_cell_surface( cell=c )
                self.upd_aux_con_1( cell=n, nbr=da )
                s += da
            self.upd_aux_con_1( cell=c,  nbr=-s)
 

    def simple_aux_pumping_step( self ):
        t = self.system.tissue
        for ce in t.cell_edges():
            if t.cell_edge_property( ce, "pump_active" ):
                direction = t.cell_edge_property( ce, "pump_direction" )
                c = direction[ 0 ]
                n = direction[ 1 ]
                da =  self.aux_act_coe *  t.cell_property( c, "auxin_level" )
                self.upd_aux_con_1( cell=n,  nbr=da)
                self.upd_aux_con_1( cell=c, nbr=-da)
        
    def aux_update( self ):
        for c in self.system.tissue.cells():
            if self.system.tissue.cell_property( c, "auxin_level")+self.h*self.system.tissue.cell_property( c, "auxin_level_1")<0:
                print " #: insufficient aux in cell ", c, "deficit:",  self.system.tissue.cell_property( c, "auxin_level") + self.system.tissue.cell_property( c, "auxin_level_1")
                self.system.tissue.cell_property( c, "auxin_level_1", value=-self.system.tissue.cell_property( c, "auxin_level") )  
            self.upd_aux_con( cell=c, nbr= self.h*self.system.tissue.cell_property( c, "auxin_level_1") )
            self.system.tissue.cell_property( c, "auxin_level_1", 0)
                
    def aux_injection( self ):
        t = self.system.tissue
        for c in t.cells():
            s = self.aux_pro_exa*t.calculate_cell_surface( cell=c )/self.system.const.cs_surf_max_surface_before_division
            if t.cell_property( c, "IC"):
                self.upd_aux_con_1( cell=c, nbr=s*self.aux_pro_IC_con_coe )
                for n in t.nth_layer_from_cell( cell = c ):
                    self.upd_aux_con_1( cell=n, nbr=s*self.aux_pro_IC_nei_con_coe )
            if t.cell_property( c, "PrC"):
                self.upd_aux_con_1( cell=c, nbr=s*self.aux_pro_PR_con_coe )
                for n in t.nth_layer_from_cell( cell = c ):
                    self.upd_aux_con_1( cell=n, nbr=s*self.aux_pro_PR_nei_con_coe )
            self.upd_aux_con_1( cell=c, nbr=s*self.aux_pro_NZ_con_coe )


class PhysAuxinTransportModel5(PhysAuxinTransportModel):
    """Diffusion + destroying in prims&center
    creation in borders
    """
    def avr_con( self ):
        z = 0
        k=0
        for i in self.tissue_system.tissue.cells():
            z += self.aux_con( i )
            k += self.tissue_system.tissue.cell_property( cell=i, property="auxin_level")
        return (z/len(self.tissue_system.tissue.cells()), k/len(self.tissue_system.tissue.cells()))

    def __init__(self, tissue_system = None):
        PhysAuxinTransportModel.__init__( self, tissue_system=tissue_system)
        self.system = tissue_system
        self.nbr_prim=1

        ###
        self.aux_max_con = 100
        
        self.aux_pro_IC_con_coe =-0.05#5
        self.aux_pro_IC_nei_con_coe = -0.01#25
        self.aux_pro_PR_con_coe = -0.05
        self.aux_pro_PR_nei_con_coe = -0.01#1
        self.aux_pro_NZ_con_coe = 0.3
        self.aux_pro_border_con_coe=0.3*84
        #auxin_average
        self.aux_pro_exa = 1500
        
        self.aux_deg_NZ_con_coe = 0.996
        
        #names confusing!
        self.aux_ini_NZ_con_exa = 35
        self.aux_ini_NZ_gra_con_exa = 0.1
        self.aux_ini_IZ_con_exa = 0
  
        self.aux_dif_coe = 0.03
        self.aux_act_coe = 0.005
        
        self.aux_prim_trs_con = 35
        
        self.h = 1
        
        """
        auxin_level == nbr of aux particles in a cell
        auxin_level_1 == change in number of particles of aux
        """
    def apply( self ):
        self.step( nbr_step=10, precision=1)
         
    def step( self, nbr_step=1, precision=1 ):
        self.h = precision
        print self.avr_con()
        self.search_for_primodium()
        #self.degrad_aux()
        #self.aux_injection()
        #self.aux_update()
        #self.orient_pumps()
        for i in range( nbr_step/precision ):
            self.aux_injection()
            self.degrad_aux()
            self.simple_aux_diff_step()
            #self.simple_aux_pumping_step()
            self.aux_update()
            #raw_input()
            #self.system.visualisation.update()
            #print " # finishing because of prim creation (step/outOf): ", i, nbr_step    
            #break

    def pre_step( self, nbr_step=100, precision=0.5 ):
        self.h = precision
        print self.avr_con()
        for i in range( nbr_step/precision ):
            self.aux_injection()
            self.degrad_aux()
            self.simple_aux_diff_step()
            self.aux_update()

    def search_for_primodium( self ):
        t = self.system.tissue
        pc = []
        for c in t.cells():
            if t.cell_property( cell=c, property="PZ"):
                if self.aux_con( cell = c ) > self.aux_prim_trs_con:
                    #nL=t.cell_neighbors( cell=c)
                    nL=t.nth_layer_from_cell( cell=c, distance=1, smaller_than=True)
                    neigh_prim=False
                    for n in  nL:
                        if t.cell_property( cell=n, property="PrC") > 0:
                            neigh_prim=True
                    if not neigh_prim:
                        #nL=t.cell_neighbors( cell=c)
                        #for n in nL:
                        #    # for any!!
                        #    if self.aux_con( cell = n ) > self.aux_prim_trs_con:
                        #        pc.append( c )
                        #        break
                        pc.append( c )
                        
        return self.create_primordiums( primordium_cand=pc )
        
    def create_primordiums( self, primordium_cand=None):
        t = self.system.tissue
        prim_created = False
        #TODO test sorting
        primordium_cand.sort( lambda x, y: cmp( self.aux_con( cell = y ),  self.aux_con( cell = x ) ))
        for i in range( len( primordium_cand ) ):
            c = primordium_cand[ i ]
            #nL=t.cell_neighbors( cell=c)
            nL=t.nth_layer_from_cell( cell=c, distance=1, smaller_than=True)
            neigh_prim=False
            for n in  nL:
                if t.cell_property( cell=n, property="PrC") > 0:
                    neigh_prim=True
                    break
            if not neigh_prim:
                t.cell_property( cell=c, property="PrC", value=self.nbr_prim)
                t.cell_property( cell=c, property="PrZ", value=self.nbr_prim)
                for n in t.cell_neighbors( c ):
                    t.cell_property( cell=n, property="PrZ", value=self.nbr_prim)
                self.nbr_prim+=1
                prim_created = True
        if prim_created:
            return True
        else:
            return False
    
        
    
    def degrad_aux(self):
        t = self.system.tissue
        for c in t.cells():
            if self.aux_con(cell= c) > self.aux_max_con:
                self.aux_con(cell= c, con=self.aux_max_con)
                print " #! degrad_aux: pumped out aux.."
            #d1 = self.aux_con( cell=c )*t.calculate_cell_surface( cell=c ) 
            #d2 = self.aux_deg_NZ_con_coe * self.aux_con( cell=c ) * t.calculate_cell_surface(cell=c)
            #d = d1 - d2
            d = self.aux_con( cell=c )*t.calculate_cell_surface( cell=c )*( 1 - self.aux_deg_NZ_con_coe )
            if d < 0:
                print " #! degradation do not degradate.."
            self.upd_aux_con_1( cell = c, nbr = -d )
            #t.cell_property(cell= c, property="auxin_level_1", value=t.cell_property(cell= c, property="auxin_level")*self.aux_degradation_coef)
            
    def init_aux(self):
        t = self.system.tissue
        #s = self.aux_pro_exa*t.calculate_cell_surface( cell=c )/self.system.const.cs_surf_max_surface_before_division
        #for c in t.cells():
        #    if t.cell_property(cell= c, property="IC"):
        #        IC = c
        #for i in range( 20 ):
        #    for c in t.nth_layer_from_cell( cell = IC, distance=i, smaller_than=True):
        #        self.aux_con(cell= c, con= self.aux_con( cell =c ) + self.aux_ini_NZ_gra_con_exa )
        #for i in range( 10 ):
        #    for c in t.nth_layer_from_cell( cell = IC, distance=i, smaller_than=True):
        #        self.aux_con(cell= c, con= self.aux_con( cell =c ) + self.aux_ini_IZ_con_exa)
        #        
        for c in t.cells():
            self.aux_con(cell= c, con= self.aux_ini_NZ_con_exa) #+random.random() )
                       
    def orient_pumps( self ):
        t = self.system.tissue
        for cn in t.cell_edges():
            ( c, n ) = cn
            t.cell_edge_property( cell_edge=cn, property="pump_active", value=False )
        for c in t.cells():
            neighL = t.cell_neighbors( cell = c )
            #d = {}
            N = neighL[ 0 ]
            Naux_con = self.aux_con( cell = N )
            for n in neighL:
                if Naux_con < self.aux_con( cell = n):
                    N = n
                    Naux_con = self.aux_con( cell = n)
            #print Naux_con, t.cell_property( cell = c, property="auxin_level")
            if Naux_con >  self.aux_con( cell = c):
                t.cell_edge_property( cell_edge=t.cell_edge_id( (c, N)), property="pump_active", value=True )
                t.cell_edge_property( cell_edge=t.cell_edge_id((c, N)), property="pump_direction", value=(c, N))
    
    def simple_aux_diff_step( self ):
        """
        Just to test visu..
        """
        for c in self.system.tissue.cells():
            da = 0
            s = 0
            for n in self.system.tissue.cell_neighbors( cell = c ):
                da = self.aux_dif_coe * max(0, self.aux_con( c ) - self.aux_con( n ) ) * self.tissue_system.tissue.calculate_cell_surface( cell=c )
                self.upd_aux_con_1( cell=n, nbr=da )
                s += da
            self.upd_aux_con_1( cell=c,  nbr=-s)
 

    def simple_aux_pumping_step( self ):
        t = self.system.tissue
        for ce in t.cell_edges():
            if t.cell_edge_property( ce, "pump_active" ):
                direction = t.cell_edge_property( ce, "pump_direction" )
                c = direction[ 0 ]
                n = direction[ 1 ]
                da =  self.aux_act_coe *  t.cell_property( c, "auxin_level" )
                self.upd_aux_con_1( cell=n,  nbr=da)
                self.upd_aux_con_1( cell=c, nbr=-da)
        
    def aux_update( self ):
        for c in self.system.tissue.cells():
            if self.system.tissue.cell_property( c, "auxin_level")+self.h*self.system.tissue.cell_property( c, "auxin_level_1")<0:
                print " #: insufficient aux in cell ", c, "deficit:",  self.system.tissue.cell_property( c, "auxin_level") + self.system.tissue.cell_property( c, "auxin_level_1")
                self.system.tissue.cell_property( c, "auxin_level_1", value=-self.system.tissue.cell_property( c, "auxin_level") )  
            self.upd_aux_con( cell=c, nbr= self.h*self.system.tissue.cell_property( c, "auxin_level_1") )
            self.system.tissue.cell_property( c, "auxin_level_1", 0)
                
    def aux_injection( self ):
        t = self.system.tissue
        for c in t.cells():
            s = self.aux_pro_exa*t.calculate_cell_surface( cell=c )/self.system.const.cs_surf_max_surface_before_division
            if t.cell_property( c, "IC"):
                self.upd_aux_con_1( cell=c, nbr=s*self.aux_pro_IC_con_coe )
                for n in t.nth_layer_from_cell( cell = c ):
                    self.upd_aux_con_1( cell=n, nbr=s*self.aux_pro_IC_nei_con_coe )
            if t.cell_property( c, "PrC"):
                self.upd_aux_con_1( cell=c, nbr=s*self.aux_pro_PR_con_coe )
                for n in t.nth_layer_from_cell( cell = c ):
                    self.upd_aux_con_1( cell=n, nbr=s*self.aux_pro_PR_nei_con_coe )
            if t.cell_property( c, "PrC"):
                self.upd_aux_con_1( cell=c, nbr=s*self.aux_pro_PR_con_coe )
            if t.cell_property( c, "border_cell"):
                self.upd_aux_con_1( cell=c, nbr=s*self.aux_pro_border_con_coe/self.system.tissue.nbr_border_cells() )
            self.upd_aux_con_1( cell=c, nbr=s*self.aux_pro_NZ_con_coe )



class PhysAuxinTransportModel6(PhysAuxinTransportModel):
    """Discret inhibitor field
    """

    def __init__(self, tissue_system = None):
        PhysAuxinTransportModel.__init__( self, tissue_system=tissue_system)
        self.system = tissue_system
        self.nbr_prim=1
        self.min_distance_between_prim=6

    def apply( self ):
        self.step( )
         
    def step( self, nbr_step=1, precision=1 ):
        self.search_for_primodium()
 
    def pre_step( self, nbr_step=100, precision=0.5 ):
        pass
    
    def search_for_primodium( self ):
        t = self.system.tissue
        pc = []
        self.ipr = {}
        self._update_prim_range( ipr=self.ipr)
        for c in t.cells():
            if t.cell_property( cell=c, property="PZ") and not self.ipr.has_key( c ):
                pc.append( c )                        
        return self.create_primordiums( primordium_cand=pc )

    def _update_prim_range( self, ipr=None, cell=None):
        # optimalisation: marking prim range:
        #ipr = {}
        t = self.system.tissue
        if cell == None:
            for c in t.cells():
                if t.cell_property( cell=c, property="PrC") > 0:
                    nL=t.nth_layer_from_cell( cell=c, distance=self.min_distance_between_prim, smaller_than=True)
                    for i in nL:
                        ipr[ i ] = True
            return ipr
        else:
            if t.cell_property( cell=cell, property="PrC") > 0:
                nL=t.nth_layer_from_cell( cell=cell, distance=self.min_distance_between_prim, smaller_than=True)
                for i in nL:
                    ipr[ i ] = True
            return ipr
            
        
    def create_primordiums( self, primordium_cand=None):
        t = self.system.tissue
        prim_created = False
        # TODO crit sensownego rozmieszczenia primordium_cand.sort( lambda x, y: cmp( self.aux_con( cell = y ),  self.aux_con( cell = x ) ))
        for i in range( len( primordium_cand ) ):
            c = primordium_cand[ i ]
            #nL=t.cell_neighbors( cell=c)
            if not self.ipr.has_key( c ):
                t.cell_property( cell=c, property="PrC", value=self.nbr_prim)
                t.cell_property( cell=c, property="PrZ", value=self.nbr_prim)
                for n in t.cell_neighbors( c ):
                    t.cell_property( cell=n, property="PrZ", value=self.nbr_prim)
                self.nbr_prim+=1
                prim_created = True
                self._update_prim_range( ipr=self.ipr, cell=c)
        if prim_created:
            return True
        else:
            return False
    
       
    def init_aux(self):
        pass
    
 



class PhysAuxinTransportModel7(PhysAuxinTransportModel):
    """Discret inhibitor field
    """

    def __init__(self, tissue_system = None):
        PhysAuxinTransportModel.__init__( self, tissue_system=tissue_system)
        self.system = tissue_system
        self.nbr_prim=1
        self.min_distance_between_prim=320

    def apply( self ):
        self.step( )
         
    def step( self, nbr_step=1, precision=1 ):
        self.search_for_primodium()
 
    def pre_step( self, nbr_step=100, precision=0.5 ):
        pass
    
    def search_for_primodium( self ):
        t = self.system.tissue
        pc = []
        self.ipr = {}
        self._update_prim_range( ipr=self.ipr)
        for c in t.cells():
            if t.cell_property( cell=c, property="PZ") and not self.ipr.has_key( c ):
                pc.append( c )                        
        return self.create_primordiums( primordium_cand=pc )

    def _update_prim_range( self, ipr=None, cell=None):
        # optimalisation: marking prim range:
        #ipr = {}
        t = self.system.tissue
        pL=[]
        if cell == None:
            for c in t.cells():
                if t.cell_property( cell=c, property="PrC") > 0:
                    pL.append( c )
            cc = t.cell_centers()
            for i in cc:
                for p in pL:
                    if visual.mag( cc[ p ] - cc[ i ]) < self.min_distance_between_prim:
                        ipr[ i ] = True
            return ipr
        else:
            if t.cell_property( cell=cell, property="PrC") > 0:
               cc = t.cell_centers()
               for i in cc:
                    if visual.mag(cc[ cell ] - cc[ i ]) < self.min_distance_between_prim:
                        ipr[ i ] = True
            return ipr
            
    def sort_prim_cand( self, prim_cand=None):
        if len( prim_cand ) < 2:
            return prim_cand

        t = self.system.tissue        
        pp = {}
        for c in t.cells():
            if t.cell_property( cell=c, property="PrC"):
                pp[  c ] = t.cell_center( cell=c )
        
        ds = {}        
        for i in prim_cand:
            z=0
            for j in pp:
                z += math.pow( visual.mag( pp[ j ] - t.cell_center( i ) ),2 )
            ds[ i ] = z
        prim_cand.sort( lambda x, y: cmp( ds[ y ],  ds[ x ] ))
        return prim_cand
        
    def create_primordiums( self, primordium_cand=None):
        t = self.system.tissue
        prim_created = False
        primordium_cand = self.sort_prim_cand( prim_cand=primordium_cand )
        for i in range( len( primordium_cand ) ):
            c = primordium_cand[ i ]
            #nL=t.cell_neighbors( cell=c)
            if not self.ipr.has_key( c ):
                t.cell_property( cell=c, property="PrC", value=self.nbr_prim)
                t.store_primordium_position( c )
                t.cell_property( cell=c, property="PrZ", value=self.nbr_prim)
                for n in t.cell_neighbors( c ):
                    t.cell_property( cell=n, property="PrZ", value=self.nbr_prim)
                self.nbr_prim+=1
                prim_created = True
                self._update_prim_range( ipr=self.ipr, cell=c)
        if prim_created:
            return True
        else:
            return False
    
       
    def init_aux(self):
        pass

class PhysAuxinTransportModel8(PhysAuxinTransportModel):
    """Inhibitory field besed on potential function for 2D geometry.
    """

    def __init__(self, tissue_system = None):
        PhysAuxinTransportModel.__init__( self, tissue_system=tissue_system)
        self.system = tissue_system
        self.nbr_prim=1
        self.min_distance_between_prim=700
        self.c_prim_stiffness = 8

    def apply( self ):
        self.step( )
         
    def step( self, nbr_step=1, precision=1 ):
        self.search_for_primodium()
      
    
    def pre_step( self, nbr_step=100, precision=0.5 ):
        pass
    
    def _single_prim_inhibition( self, pos, v ):
        d = mag(pos - v)
        try:
            return (self.min_distance_between_prim/d)**self.c_prim_stiffness
        except ZeroDivisionError:
            return float("infinity")
    
    def _prim_inhibition( self, v, prims ):
        r = 0
        for i in prims:
            r += self._single_prim_inhibition( v, i )
        return r
    
    def search_for_primodium( self ):
        t = self.system.tissue
        pc = []
        for c in t.cells():
            if t.cell_property( cell=c, property="PZ"):
                pc.append( c )
        self.create_primordiums( primordium_cand=pc )

            
    def select_prim_cand( self, prim_cand=None, prims=None):
        t = self.system.tissue        
        pcc = {}
        for c in prim_cand:
            pcc[  c ] = t.cell_center( cell=c )
        
        filtered_pc = []
        ds = {}        
        for i in prim_cand:
            ds[ i ] = self._prim_inhibition( t.cell_center( i ), prims ) 
            if ds[ i ] <= 1:
                filtered_pc.append( i )
        filtered_pc.sort( lambda x, y: cmp( ds[ y ],  ds[ x ] ))
        if len( filtered_pc ) >1:
            print " #: more than one candidate: ", len( filtered_pc )
        return filtered_pc
        
    def create_primordiums( self, primordium_cand=None ):
        t = self.system.tissue
        prims_positions=[]
        for c in t.cells():
            if t.cell_property( cell=c, property="PrC") > 0:
                prims_positions.append( t.cell_center( c ) )
        
        z = self.select_prim_cand( prim_cand=primordium_cand, prims=prims_positions )
        while z:
            c = z[ 0 ]
            t.cell_property( cell=c, property="PrC", value=self.nbr_prim)
            t.store_primordium_position( c )
            t.cell_property( cell=c, property="PrZ", value=self.nbr_prim)
            for n in t.cell_neighbors( c ):
                t.cell_property( cell=n, property="PrZ", value=self.nbr_prim)
            self.nbr_prim+=1
            prims_positions.append( t.cell_center( z[ 0 ] ) )
            z = self.select_prim_cand( prim_cand=primordium_cand, prims=prims_positions )
       
    def init_aux(self):
        pass

class PhysAuxinTransportModel10(PhysAuxinTransportModel):
    """Inhibitory field besed on potential function for 2D geometry.
    The primordium is a wv, all cells in which we caould find wv are marked as prims.
    The primordium could be initiated only if three cells are having the inhibition under
    certain trashhold
    """

    def __init__(self, tissue_system = None):
        PhysAuxinTransportModel.__init__( self, tissue_system=tissue_system)
        self.system = tissue_system
        self.nbr_prim=1
        self.min_distance_between_prim=700
        self.c_prim_stiffness = 8

    def apply( self ):
        self.step( )
         
    def step( self, nbr_step=1, precision=1 ):
        self.search_for_primodium()
      
    
    def pre_step( self, nbr_step=100, precision=0.5 ):
        pass
    
    def _single_prim_inhibition( self, pos, v ):
        d = mag(pos - v)
        try:
            return (self.min_distance_between_prim/d)**self.c_prim_stiffness
        except ZeroDivisionError:
            return float("infinity")
    
    def _prim_inhibition( self, v, prims ):
        r = 0
        for i in prims:
            r += self._single_prim_inhibition( v, i )
        return r
    
    def search_for_primodium( self ):
        t = self.system.tissue
        pc = []
        for c in t.cells():
            if t.cell_property( cell=c, property="PZ"):
                pc.append( c )
            pvw=[]
            for i in pc:
                for j in self.system.tissue.cell2wvs( cell = i):
                    pvw.append( j )
            pvw = dict(map(lambda a: (a,1), pvw)).keys()
        self.create_primordiums( primordium_cand=pvw )

            
    def select_prim_cand( self, prim_cand=None, prims=None):
        t = self.system.tissue        
        pcc = {}
        for wv in prim_cand:
            pcc[  wv ] = t.wv_pos( wv=wv )
        
        filtered_pc = []
        ds = {}        
        for i in prim_cand:
            ds[ i ] = self._prim_inhibition( t.wv_pos( wv=i ), prims ) 
            if ds[ i ] <= 1:
                filtered_pc.append( i )
        filtered_pc.sort( lambda x, y: cmp( ds[ y ],  ds[ x ] ))
        refiltered_pc=[]
        for i in filtered_pc:
            if len( self.tissue_system.tissue.wv2cells( wv=i ) )>2:
                refiltered_pc.append( i )
        
        if len( refiltered_pc ) >1:
            print " #: more than one candidate: ", len( refiltered_pc )
        return refiltered_pc
        
    def create_primordiums( self, primordium_cand=None ):
        t = self.system.tissue
        prims_positions=[]
        prims_positions_={}
        for wv in t.wvs():
            for c in t.wv2cells( wv = wv):
                if t.cell_property( cell=c, property="PrC") > 0:
                    prims_positions_[  t.cell_property( cell=c, property="PrC") ] = t.wv_pos( wv ) 
        prims_positions = prims_positions_.values()
        z = self.select_prim_cand( prim_cand=primordium_cand, prims=prims_positions )
        while z:
            wv = z[ 0 ]
            t.wv_property(wv=wv,property="PrC", value=self.nbr_prim)
            t.store_primordium_position_wv( wv, self.nbr_prim )
            print t.wv2cells( wv )
            for c in t.wv2cells( wv ):
                t.cell_property( cell=c, property="PrC", value=self.nbr_prim)
                t.cell_property( cell=c, property="PrZ", value=self.nbr_prim)
            prims_positions.append( t.wv_pos( wv ) )
            self.nbr_prim+=1
            z = self.select_prim_cand( prim_cand=primordium_cand, prims=prims_positions )
       
    def init_aux(self):
        pass

class PhysAuxinTransportModel9(PhysAuxinTransportModel):
    """Inhibitory field besed on potential function for 2D geometry.
    The primordium is a wv, all cells in which we caould find wv are marked as prims.
    """

    def __init__(self, tissue_system = None):
        PhysAuxinTransportModel.__init__( self, tissue_system=tissue_system)
        self.system = tissue_system
        self.nbr_prim=1
        self.min_distance_between_prim=700
        self.c_prim_stiffness = 8

    def apply( self ):
        self.step( )
         
    def step( self, nbr_step=1, precision=1 ):
        self.search_for_primodium()
      
    
    def pre_step( self, nbr_step=100, precision=0.5 ):
        pass
    
    def _single_prim_inhibition( self, pos, v ):
        d = mag(pos - v)
        try:
            return (self.min_distance_between_prim/d)**self.c_prim_stiffness
        except ZeroDivisionError:
            return float("infinity")
    
    def _prim_inhibition( self, v, prims ):
        r = 0
        for i in prims:
            r += self._single_prim_inhibition( v, i )
        return r
    
    def search_for_primodium( self ):
        t = self.system.tissue
        pc = []
        for c in t.cells():
            if t.cell_property( cell=c, property="PZ"):
                pc.append( c )
            pvw=[]
            for i in pc:
                for j in self.system.tissue.cell2wvs( cell = i):
                    pvw.append( j )
            pvw = dict(map(lambda a: (a,1), pvw)).keys()
        self.create_primordiums( primordium_cand=pvw )

            
    def select_prim_cand( self, prim_cand=None, prims=None):
        t = self.system.tissue        
        pcc = {}
        for wv in prim_cand:
            pcc[  wv ] = t.wv_pos( wv=wv )
        
        filtered_pc = []
        ds = {}        
        for i in prim_cand:
            ds[ i ] = self._prim_inhibition( t.wv_pos( wv=i ), prims ) 
            if ds[ i ] <= 1:
                filtered_pc.append( i )
        filtered_pc.sort( lambda x, y: cmp( ds[ y ],  ds[ x ] ))
        if len( filtered_pc ) >1:
            print " #: more than one candidate: ", len( filtered_pc )
        return filtered_pc
        
    def create_primordiums( self, primordium_cand=None ):
        t = self.system.tissue
        prims_positions=[]
        prims_positions_={}
        for wv in t.wvs():
            for c in t.wv2cells( wv = wv):
                if t.cell_property( cell=c, property="PrC") > 0:
                    prims_positions_[  t.cell_property( cell=c, property="PrC") ] = t.wv_pos( wv ) 
        prims_positions = prims_positions_.values()
        z = self.select_prim_cand( prim_cand=primordium_cand, prims=prims_positions )
        while z:
            wv = z[ 0 ]
            t.wv_property(wv=wv,property="PrC", value=self.nbr_prim)
            #t.store_primordium_position_wv( wv, self.nbr_prim )
            print t.wv2cells( wv )
            for c in t.wv2cells( wv ):
                t.cell_property( cell=c, property="PrC", value=self.nbr_prim)
                t.cell_property( cell=c, property="PrZ", value=self.nbr_prim)
            prims_positions.append( t.wv_pos( wv ) )
            self.nbr_prim+=1
            z = self.select_prim_cand( prim_cand=primordium_cand, prims=prims_positions )
       
    def init_aux(self):
        pass

class PhysAuxinTransportModel11(PhysAuxinTransportModel):
    
    """Diffusion + destroying in prims&center
    creation in borders
    """
    def avr_con( self ):
        z = 0
        k=0
        for i in self.tissue_system.tissue.cells():
            z += self.aux_con( i )
            k += self.tissue_system.tissue.cell_property( cell=i, property="auxin_level")
        return (z/len(self.tissue_system.tissue.cells()), k/len(self.tissue_system.tissue.cells()))

    def __init__(self, tissue_system = None):
        PhysAuxinTransportModel.__init__( self, tissue_system=tissue_system)
        self.system = tissue_system
        self.nbr_prim=1

        ###
        self.aux_max_con = 100
        
        self.aux_pro_IC_con_coe =-0.05#5
        self.aux_pro_IC_nei_con_coe = -0.01#25
        self.aux_pro_PR_con_coe = -0.05
        self.aux_pro_PR_nei_con_coe = -0.01#1
        self.aux_pro_NZ_con_coe = 0.3
        self.aux_pro_border_con_coe=0.3*84
        #auxin_average
        self.aux_pro_exa = 1500
        
        self.aux_deg_NZ_con_coe = 0.996
        
        #names confusing!
        self.aux_ini_NZ_con_exa = 35
        self.aux_ini_NZ_gra_con_exa = 0.1
        self.aux_ini_IZ_con_exa = 0
  
        self.aux_dif_coe = 0.03
        self.aux_act_coe = 0.005
        
        self.aux_prim_trs_con = 35
        
        self.h = 1
        
        """
        auxin_level == nbr of aux particles in a cell
        auxin_level_1 == change in number of particles of aux
        """
    def apply( self ):
        self.step( nbr_step=10, precision=1)
         
    def step( self, nbr_step=1, precision=1 ):
        self.h = precision
        print self.avr_con()
        self.search_for_primodium()
        #self.orient_pumps()
        for i in range( nbr_step/precision ):
            self.aux_injection()
            self.degrad_aux()
            self.simple_aux_diff_step()
            #self.simple_aux_pumping_step()
            self.aux_update()
            #raw_input()
            #self.system.visualisation.update()
            #print " # finishing because of prim creation (step/outOf): ", i, nbr_step    
            #break

    def pre_step( self, nbr_step=100, precision=0.5 ):
        self.h = precision
        print self.avr_con()
        for i in range( nbr_step/precision ):
            self.aux_injection()
            self.degrad_aux()
            self.simple_aux_diff_step()
            self.aux_update()

    def search_for_primodium( self ):
        t = self.system.tissue
        pc = []
        for c in t.cells():
            if t.cell_property( cell=c, property="PZ"):
                if self.aux_con( cell = c ) > self.aux_prim_trs_con:
                    #nL=t.cell_neighbors( cell=c)
                    nL=t.nth_layer_from_cell( cell=c, distance=1, smaller_than=True)
                    neigh_prim=False
                    for n in  nL:
                        if t.cell_property( cell=n, property="PrC") > 0:
                            neigh_prim=True
                    if not neigh_prim:
                        #nL=t.cell_neighbors( cell=c)
                        #for n in nL:
                        #    # for any!!
                        #    if self.aux_con( cell = n ) > self.aux_prim_trs_con:
                        #        pc.append( c )
                        #        break
                        pc.append( c )
                        
        return self.create_primordiums( primordium_cand=pc )
        
    def create_primordiums( self, primordium_cand=None):
        t = self.system.tissue
        prim_created = False
        #TODO test sorting
        primordium_cand.sort( lambda x, y: cmp( self.aux_con( cell = y ),  self.aux_con( cell = x ) ))
        for i in range( len( primordium_cand ) ):
            c = primordium_cand[ i ]
            #nL=t.cell_neighbors( cell=c)
            nL=t.nth_layer_from_cell( cell=c, distance=1, smaller_than=True)
            neigh_prim=False
            for n in  nL:
                if t.cell_property( cell=n, property="PrC") > 0:
                    neigh_prim=True
                    break
            if not neigh_prim:
                t.cell_property( cell=c, property="PrC", value=self.nbr_prim)
                t.cell_property( cell=c, property="PrZ", value=self.nbr_prim)
                for n in t.cell_neighbors( c ):
                    t.cell_property( cell=n, property="PrZ", value=self.nbr_prim)
                self.nbr_prim+=1
                prim_created = True
        if prim_created:
            return True
        else:
            return False
    
        
    
    def degrad_aux(self):
        t = self.system.tissue
        for c in t.cells():
            if self.aux_con(cell= c) > self.aux_max_con:
                self.aux_con(cell= c, con=self.aux_max_con)
                print " #! degrad_aux: pumped out aux.."
            #d1 = self.aux_con( cell=c )*t.calculate_cell_surface( cell=c ) 
            #d2 = self.aux_deg_NZ_con_coe * self.aux_con( cell=c ) * t.calculate_cell_surface(cell=c)
            #d = d1 - d2
            d = self.aux_con( cell=c )*t.calculate_cell_surface( cell=c )*( 1 - self.aux_deg_NZ_con_coe )
            if d < 0:
                print " #! degradation do not degradate.."
            self.upd_aux_con_1( cell = c, nbr = -d )
            #t.cell_property(cell= c, property="auxin_level_1", value=t.cell_property(cell= c, property="auxin_level")*self.aux_degradation_coef)
            
    def init_aux(self):
        t = self.system.tissue
        #s = self.aux_pro_exa*t.calculate_cell_surface( cell=c )/self.system.const.cs_surf_max_surface_before_division
        #for c in t.cells():
        #    if t.cell_property(cell= c, property="IC"):
        #        IC = c
        #for i in range( 20 ):
        #    for c in t.nth_layer_from_cell( cell = IC, distance=i, smaller_than=True):
        #        self.aux_con(cell= c, con= self.aux_con( cell =c ) + self.aux_ini_NZ_gra_con_exa )
        #for i in range( 10 ):
        #    for c in t.nth_layer_from_cell( cell = IC, distance=i, smaller_than=True):
        #        self.aux_con(cell= c, con= self.aux_con( cell =c ) + self.aux_ini_IZ_con_exa)
        #        
        for c in t.cells():
            self.aux_con(cell= c, con= self.aux_ini_NZ_con_exa) #+random.random() )
                       
    def orient_pumps( self ):
        t = self.system.tissue
        for cn in t.cell_edges():
            ( c, n ) = cn
            t.cell_edge_property( cell_edge=cn, property="pump_active", value=False )
        for c in t.cells():
            neighL = t.cell_neighbors( cell = c )
            #d = {}
            N = neighL[ 0 ]
            Naux_con = self.aux_con( cell = N )
            for n in neighL:
                if Naux_con < self.aux_con( cell = n):
                    N = n
                    Naux_con = self.aux_con( cell = n)
            #print Naux_con, t.cell_property( cell = c, property="auxin_level")
            if Naux_con >  self.aux_con( cell = c):
                t.cell_edge_property( cell_edge=t.cell_edge_id( (c, N)), property="pump_active", value=True )
                t.cell_edge_property( cell_edge=t.cell_edge_id((c, N)), property="pump_direction", value=(c, N))
    
    def simple_aux_diff_step( self ):
        """
        Just to test visu..
        """
        for c in self.system.tissue.cells():
            da = 0
            s = 0
            for n in self.system.tissue.cell_neighbors( cell = c ):
                da = self.aux_dif_coe * max(0, self.aux_con( c ) - self.aux_con( n ) ) * self.tissue_system.tissue.calculate_cell_surface( cell=c )
                self.upd_aux_con_1( cell=n, nbr=da )
                s += da
            self.upd_aux_con_1( cell=c,  nbr=-s)
 

    def simple_aux_pumping_step( self ):
        t = self.system.tissue
        for ce in t.cell_edges():
            if t.cell_edge_property( ce, "pump_active" ):
                direction = t.cell_edge_property( ce, "pump_direction" )
                c = direction[ 0 ]
                n = direction[ 1 ]
                da =  self.aux_act_coe *  t.cell_property( c, "auxin_level" )
                self.upd_aux_con_1( cell=n,  nbr=da)
                self.upd_aux_con_1( cell=c, nbr=-da)
        
    def aux_update( self ):
        for c in self.system.tissue.cells():
            if self.system.tissue.cell_property( c, "auxin_level")+self.h*self.system.tissue.cell_property( c, "auxin_level_1")<0:
                print " #: insufficient aux in cell ", c, "deficit:",  self.system.tissue.cell_property( c, "auxin_level") + self.system.tissue.cell_property( c, "auxin_level_1")
                self.system.tissue.cell_property( c, "auxin_level_1", value=-self.system.tissue.cell_property( c, "auxin_level") )  
            self.upd_aux_con( cell=c, nbr= self.h*self.system.tissue.cell_property( c, "auxin_level_1") )
            self.system.tissue.cell_property( c, "auxin_level_1", 0)
                
    def aux_injection( self ):
        t = self.system.tissue
        for c in t.cells():
            s = self.aux_pro_exa*t.calculate_cell_surface( cell=c )/self.system.const.cs_surf_max_surface_before_division
            if t.cell_property( c, "IC"):
                self.upd_aux_con_1( cell=c, nbr=s*self.aux_pro_IC_con_coe )
                for n in t.nth_layer_from_cell( cell = c ):
                    self.upd_aux_con_1( cell=n, nbr=s*self.aux_pro_IC_nei_con_coe )
            if t.cell_property( c, "PrC"):
                self.upd_aux_con_1( cell=c, nbr=s*self.aux_pro_PR_con_coe )
                for n in t.nth_layer_from_cell( cell = c ):
                    self.upd_aux_con_1( cell=n, nbr=s*self.aux_pro_PR_nei_con_coe )
            if t.cell_property( c, "PrC"):
                self.upd_aux_con_1( cell=c, nbr=s*self.aux_pro_PR_con_coe )
            if t.cell_property( c, "border_cell"):
                self.upd_aux_con_1( cell=c, nbr=s*self.aux_pro_border_con_coe/self.system.tissue.nbr_border_cells() )
            self.upd_aux_con_1( cell=c, nbr=s*self.aux_pro_NZ_con_coe )


class PhysAuxinTransportModel12(PhysAuxinTransportModel):
    """Model with correct resolution using scipy RK4 method and waiting for
    stabilisation.
    
    It should be canalisation model.
    
    The parameters allow to form a gradient pumping in the area of 2 from the center.
    """

    def __init__(self, tissue_system = None):
        PhysAuxinTransportModel.__init__( self, tissue_system=tissue_system)
        self.system = tissue_system
        self.nbr_prim=1
        self.t = 0
        self.h = 5
        self.c_change = 0.05 #acceptable change could not be smaller to classifie as error.
        
        
        self.c_alpha = 0.0001 #creation
        self.c_beta = 0.0001 #destruction
        self.c_gamma = 0.01 #active flux
        self.c_kappa = 0.05  #diffusion
        
        self.c_lambda = 0.025 # PIN production depanding on flux
        self.c_qmin = 0.005 #min production of PIN
        self.c_theta=0.005 #decay of PIN
        self.c_pin_max=1.4 #this limits the number of pin to c_pin_max*c_qmin
        
        self.c_epsilon=0.3 #prim evacuate
        self.c_delta = 0.3 #center evacuate


        self.aux_prim_trs_con = 0.93
        self.c_initial_aux_value=0.5

        """
        auxin_level == nbr of aux particles in a cell
        auxin_level_1 == change in number of particles of aux
        """
    def apply( self ):
        self.step( )
         
    def step( self, nbr_step=1, precision=1 ):
        t = self.tissue_system.tissue
        self.prepare_sys_map()
        stable=False
        i=0
        while not stable:
            print " #: phys aux trans: loop=", i, " time=",self.t
            i+=1
            res= scipy.integrate.odepack.odeint( self.f, self.prepare_x0(), [self.t, self.t+self.h],rtol=0.01, atol=0.001 )
            self.t += self.h                
            stable = self.rate_error( res[0], res[1])
            self.update( res[1] )
            y=[]
            z = 0
            # quantities
            for j in self.cell2sys:
                y.append(res[1][ self.cell2sys[ j ] ] )
                z +=  res[1][ self.cell2sys[ j ] ]
            print "  #: aux qua avg: ", z/len( self.tissue_system.tissue.cells() ), "aux qua min:", min(y), "aux qua max:", max(y)
            y=[]
            z=0
            for j in self.wall2sys:
                y.append(res[1][ self.wall2sys[ j ] ] )
                z +=  res[1][ self.wall2sys[ j ] ]
            print "  #: pin qua avg: ", z/len( y ), "pin qua min:", min(y), "pin qua max:", max(y)
            #raw_input()
            #concentration
            #for i in self.cell2sys:
            #    y.append(res[1][ self.cell2sys[ i ] ]/t.calculate_cell_surface(cell=i) )
            #    z +=  res[1][ self.cell2sys[ i ] ]/t.calculate_cell_surface(cell=i)
            #print "aux con avg: ", z/len( self.tissue_system.tissue.cells() ), "aux con min:", min(y), "aux con max:", max(y)
        
        self.create_primordiums(self.search_for_primodium())
        ##cc = self.tissue_system.tissue.cell_centers()
        ##for c in self.tissue_system.tissue.cells():
        ##    cc[ c ].z = self.aux( cell=c )
        ##X,Y,Z=[],[],[]
        ##for i in cc:
        ##    X.append(cc[i].x)
        ##    Y.append(cc[i].y)
        ##    Z.append(cc[i].z)
        ##(X,Y,Z)=tools.create_grid_from_discret_values(X,Y,Z)
        ###tools.plot_3d_height_map( X,Y,Z)
        ##tools.test( X,Y,Z)
        ##import pylab
        ##pylab.plot(Y,Z[int(len(X)/2)])
        ##pylab.show()
        
    def update( self, x ):
        t = self.system.tissue
        for i in t.cells():
            t0 = x[ self.cell2sys[ i ] ]
            t0 = max(0,t0)
            self.aux( cell=i, value= t0)
        for i in self.tissue_system.tissue.cell_edges():
            (s,t)=i
            t1=x[ self.wall2sys[ (s,t) ] ]
            t2=x[ self.wall2sys[ (t,s) ] ]
            t1 = max(0, min( t1,self.c_pin_max))
            t2 = max(0, min( t2,self.c_pin_max))
            self.pin( cell_edge=(s,t), value=t1 )
            self.pin( cell_edge=(t,s), value=t2 )        

    def rate_error( self, xn, xnprim ):
        t = True
        max = -float("infinity")
        for i in range( len( self.tissue_system.tissue.cells() )):
            if abs( xn[i] - xnprim[i] ) > max:
                max=abs( xn[i] - xnprim[i] )
            if self.c_change < abs( xn[i] - xnprim[i] ):
                t=False 
                #break
        print " #: errror =  ", max# abs( xn[i] - xnprim[i] )
        return t

    def prepare_x0( self ):
        x0 = []
        t = self.system.tissue
        for x in range( len(t.cells()) + len( 2*t.cell_edges() ) ):
            x0.append(0)
        for i in t.cells():
            x0[ self.cell2sys[ i ] ] = self.aux( i )
        for i in t.cell_edges():
            (s,t)=i
            x0[ self.wall2sys[ (s,t) ] ] = self.pin( cell_edge=(s,t) )
            x0[ self.wall2sys[ (t,s) ] ] = self.pin( cell_edge=(t,s) )
        return x0

    def prepare_sys_map( self ):
        self.cell2sys = {}
        self.wall2sys = {}
        t = self.system.tissue
        ind = 0
        for i in t.cells():
            self.cell2sys[ i ] = ind
            ind += 1
        for i in t.cell_edges():
            (s,t) = i
            self.wall2sys[ (s,t) ] = ind
            ind += 1
            self.wall2sys[ (t,s) ] = ind
            ind += 1

    def f( self, x, t ):
        def Fi( x ):
            if x < 0:
                return 0
            return x*x
        
        def P( wid, t, x):
            return x[ self.wall2sys[ wid ] ] 

        def D( (i, j), t, x):
            return (A(i,t,x)-A(j,t,x))
        
        def J( (i, j), t, x):
            #return self.c_gamma*(-A(j,t,x)*P((j,i),t,x)+A(i,t,x)*P((i,j),t,x))+(A(i,t,x)-A(j,t,x))*self.c_kappa #diff+act
            #return (A(i,t,x)-A(j,t,x))*self.c_kappa #diff OK
            return (-A(j,t,x)*P((j,i),t,x)+A(i,t,x)*P((i,j),t,x))#act OK
            #concentration
            #return self.c_gamma*(-A(j,t,x)*P((j,i),t,x)*t.calculate_cell_surface(cell=j)*t.calculate_cell_surface(cell=j)+A(i,t,x)*P((i,j),t,x)*t.calculate_cell_surface(cell=i)*t.calculate_cell_surface(cell=i))#act OK
        def A( cid, t, x ):
            return x[ self.cell2sys[ cid ] ]
        
        t = self.tissue_system.tissue
        x2 = copy.copy( x )
        for i in t.cells():
            #x2[ self.cell2sys[ i ] ] = 0
            #x2[ self.cell2sys[ i ] ] = - self.c_delta*self.i_center_evacuate( i ) #OK
            x2[ self.cell2sys[ i ] ] = self.c_alpha - A(i,t,x)*(self.c_beta+self.c_delta*self.i_local_evacuate( i )+self.c_epsilon*self.i_center_evacuate( i ))#OK
            for n in t.cell_neighbors( cell=i ):
                x2[ self.cell2sys[ i ] ] += self.c_gamma*J((n,i),t,x)
            #concentration:
            #x2[ self.cell2sys[ i ] ] = t.calculate_cell_surface(cell=i)/t.const.cs_surf_max_surface_before_division*self.c_alpha - self.c_beta*A(i,t,x)/t.calculate_cell_surface(cell=i) #- self.c_delta*self.i_local_evacuate( i ) -self.c_epsilon*self.i_center_evacuate( i )#OK
        for i in t.cell_edges():
            (s1,s2)=i
            x2[ self.wall2sys[(s1,s2)] ] = self.c_lambda*Fi(J((s1,s2),t,x))+self.c_qmin-self.c_theta*P((s1,s2),t,x)
            x2[ self.wall2sys[(s2,s1)] ] = self.c_lambda*Fi(J((s2,s1),t,x))+self.c_qmin-self.c_theta*P((s2,s1),t,x)            
        return x2
            
    def i_local_evacuate( self, cell ):
        t = self.system.tissue
        if t.cell_property( cell=cell, property="PrC") > 0:
            return 1
        else:
            return 0
        
    def i_center_evacuate( self, cell ):
        t = self.system.tissue
        if t.cell_property( cell=cell, property="IC") > 0:
            return 1
        else:
            return 0
        
            
    def init_aux(self):
        t = self.system.tissue
        #s = self.aux_pro_exa*t.calculate_cell_surface( cell=c )/self.system.const.cs_surf_max_surface_before_division
        #for c in t.cells():
        #    if t.cell_property(cell= c, property="IC"):
        #        IC = c
        #for i in range( 20 ):
        #    for c in t.nth_layer_from_cell( cell = IC, distance=i, smaller_than=True):
        #        self.aux_con(cell= c, con= self.aux_con( cell =c ) + self.aux_ini_NZ_gra_con_exa )
        #for i in range( 10 ):
        #    for c in t.nth_layer_from_cell( cell = IC, distance=i, smaller_than=True):
        #        self.aux_con(cell= c, con= self.aux_con( cell =c ) + self.aux_ini_IZ_con_exa)
        #        
        for c in t.cells():
            self.aux(cell= c, value= self.c_initial_aux_value ) #+random.random() )
        #for i in t.cell_edges():
        #    (s,t)=i
        #    self.pin( cell_edge=(s,t), value=self.c_qmin)
        #    self.pin( cell_edge=(t,s), value=self.c_qmin)
          
    def search_for_primodium( self ):
        t = self.system.tissue
        pc = []
        for c in t.cells():
            if t.cell_property( cell=c, property="PZ"):
                if self.aux( cell = c ) > self.aux_prim_trs_con:
                    pc.append( c )
        return pc
        
    def create_primordiums( self, primordium_cand=None):
        t = self.system.tissue
        if len(primordium_cand)>0:
            primordium_cand.sort( lambda x, y: cmp( self.aux( cell = y ),  self.aux( cell = x ) ))
            c = primordium_cand[ 0 ]
            t.cell_property( cell=c, property="PrC", value=self.nbr_prim)
            t.cell_property( cell=c, property="PrZ", value=self.nbr_prim)
            for n in t.cell_neighbors( c ):
                t.cell_property( cell=n, property="PrZ", value=self.nbr_prim)
            self.nbr_prim+=1
  
        
class PhysAuxinTransportModel13(PhysAuxinTransportModel):
    """Model with correct resolution using scipy RK4 method and waiting for
    stabilisation.
    
    The parameters form almost perfect spiral.
    """

    def __init__(self, tissue_system = None):
        PhysAuxinTransportModel.__init__( self, tissue_system=tissue_system)
        self.system = tissue_system
        self.nbr_prim=1
        self.t = 0
        self.h = 5
        self.c_change = 0.0005 #acceptable change could not be smaller to classifie as error.
        
        
        self.c_alpha = 0.0005 #creation
        self.c_beta = 0.0005 #destruction
        self.c_gamma = 0.04#25 #active flux
        self.c_kappa = 0.05  #diffusion
        
        self.c_lambda = 0.03 # PIN production depanding on flux
        self.c_qmin = 0.005 #min production of PIN
        self.c_theta=0.005 #decay of PIN
        self.c_pin_max=1.2 #this limits the number of pin to c_pin_max*c_qmin
        
        self.c_epsilon=0.03 #centre evacuate
        self.c_delta = 0.09 #prim evacuate


        self.aux_prim_trs_con = 0.4#0.62
        self.c_initial_aux_value=0.5

        """
        auxin_level == nbr of aux particles in a cell
        auxin_level_1 == change in number of particles of aux
        """
    def apply( self ):
        self.step( )
         
    def step( self, nbr_step=1, precision=1 ):
        t = self.tissue_system.tissue
        self.prepare_sys_map()
        stable=False
        i=0
        while not stable:
            print " #: phys aux trans: loop=", i, " time=",self.t
            i+=1
            res= scipy.integrate.odepack.odeint( self.f, self.prepare_x0(), [self.t, self.t+self.h],rtol=0.01, atol=0.001 )
            self.t += self.h                
            stable = self.rate_error( res[0], res[1])
            self.update( res[1] )
            y=[]
            z = 0
            # quantities
            for j in self.cell2sys:
                y.append(res[1][ self.cell2sys[ j ] ] )
                z +=  res[1][ self.cell2sys[ j ] ]
            print "  #: aux qua avg: ", z/len( self.tissue_system.tissue.cells() ), "aux qua min:", min(y), "aux qua max:", max(y)
            y2=[]
            z2=0
            for j in self.wall2sys:
                y2.append(res[1][ self.wall2sys[ j ] ] )
                z2 +=  res[1][ self.wall2sys[ j ] ]
            #print y
            print "  #: pin qua avg: ", z2/len( y2 ), "pin qua min:", min(y2), "pin qua max:", max(y2)
            #concentration
            #for i in self.cell2sys:
            #    y.append(res[1][ self.cell2sys[ i ] ]/t.calculate_cell_surface(cell=i) )
            #    z +=  res[1][ self.cell2sys[ i ] ]/t.calculate_cell_surface(cell=i)
            #print "aux con avg: ", z/len( self.tissue_system.tissue.cells() ), "aux con min:", min(y), "aux con max:", max(y)

        self.create_primordiums(self.search_for_primodium())
        ##cc = self.tissue_system.tissue.cell_centers()
        ##for c in self.tissue_system.tissue.cells():
        ##    cc[ c ].z = self.aux( cell=c )
        ##X,Y,Z=[],[],[]
        ##for i in cc:
        ##    X.append(cc[i].x)
        ##    Y.append(cc[i].y)
        ##    Z.append(cc[i].z)
        ##(X,Y,Z)=tools.create_grid_from_discret_values(X,Y,Z)
        ###tools.plot_3d_height_map( X,Y,Z)
        ##tools.test( X,Y,Z)
        ##import pylab
        ##pylab.plot(Y,Z[int(len(X)/2)])
        ##pylab.show()
        
    def update( self, x ):
        t = self.system.tissue
        for i in t.cells():
            t0 = x[ self.cell2sys[ i ] ]
            t0 = max(0,t0)
            self.aux( cell=i, value= t0)
        for i in t.cell_edges():
            (c1,c2)=i
            t1=x[ self.wall2sys[ (c1,c2) ] ]
            t2=x[ self.wall2sys[ (c2,c1) ] ]
            t1 = max(0, min( t1,self.c_pin_max))
            t2 = max(0, min( t2,self.c_pin_max))
            self.pin( cell_edge=(c1,c2), value=t1 )
            self.pin( cell_edge=(c2,c1), value=t2 )        
    

    def rate_error( self, xn, xnprim ):
        t = True
        max = -float("infinity")
        for i in range( len( self.tissue_system.tissue.cells() )):
            if abs( xn[i] - xnprim[i] ) > max:
                max=abs( xn[i] - xnprim[i] )
            if self.c_change < abs( xn[i] - xnprim[i] ):
                t=False 
                #break
        print " #: errror =  ", max# abs( xn[i] - xnprim[i] )
        return t

    def prepare_x0( self ):
        x0 = []
        t = self.system.tissue
        for x in range( len(t.cells()) + len( 2*t.cell_edges() ) ):
            x0.append(0)
        for i in t.cells():
            x0[ self.cell2sys[ i ] ] = self.aux( i )
        for i in t.cell_edges():
            (s,t)=i
            x0[ self.wall2sys[ (s,t) ] ] = self.pin( cell_edge=(s,t) )
            x0[ self.wall2sys[ (t,s) ] ] = self.pin( cell_edge=(t,s) )
        return x0

    def prepare_sys_map( self ):
        self.cell2sys = {}
        self.wall2sys = {}
        t = self.system.tissue
        ind = 0
        for i in t.cells():
            self.cell2sys[ i ] = ind
            ind += 1
        for i in t.cell_edges():
            (s,t) = i
            self.wall2sys[ (s,t) ] = ind
            ind += 1
            self.wall2sys[ (t,s) ] = ind
            ind += 1

    def f( self, x, t ):
        def Fi( x ):
            if x < 0:
                return 0
            return x*x
        
        def P( wid, t, x):
            return x[ self.wall2sys[ wid ] ] 

        def D( (i, j), t, x):
            return (A(i,t,x)-A(j,t,x))
        
        def J( (i, j), t, x):
            #return self.c_gamma*(-A(j,t,x)*P((j,i),t,x)+A(i,t,x)*P((i,j),t,x))+(A(i,t,x)-A(j,t,x))*self.c_kappa #diff+act
            #return (A(i,t,x)-A(j,t,x))*self.c_kappa #diff OK
            return (-A(j,t,x)*P((j,i),t,x)+A(i,t,x)*P((i,j),t,x))#act OK
            #concentration
            #return self.c_gamma*(-A(j,t,x)*P((j,i),t,x)*t.calculate_cell_surface(cell=j)*t.calculate_cell_surface(cell=j)+A(i,t,x)*P((i,j),t,x)*t.calculate_cell_surface(cell=i)*t.calculate_cell_surface(cell=i))#act OK
        def A( cid, t, x ):
            return x[ self.cell2sys[ cid ] ]
        
        t = self.tissue_system.tissue
        x2 = copy.copy( x )
        for i in t.cells():
            #x2[ self.cell2sys[ i ] ] = 0
            #x2[ self.cell2sys[ i ] ] = - self.c_delta*self.i_center_evacuate( i ) #OK
            x2[ self.cell2sys[ i ] ] = self.c_alpha - A(i,t,x)*(self.c_beta+self.c_epsilon*self.i_center_evacuate( i ))#OK
            if self.i_local_evacuate( i ):
                x2[ self.cell2sys[ i ] ] -= self.c_delta*self.prim_distance_mod( i )*A(i,t,x)
            for n in t.cell_neighbors( cell=i ):
                x2[ self.cell2sys[ i ] ] += self.c_gamma*J((n,i),t,x)
            #concentration:
            #x2[ self.cell2sys[ i ] ] = t.calculate_cell_surface(cell=i)/t.const.cs_surf_max_surface_before_division*self.c_alpha - self.c_beta*A(i,t,x)/t.calculate_cell_surface(cell=i) #- self.c_delta*self.i_local_evacuate( i ) -self.c_epsilon*self.i_center_evacuate( i )#OK
        for i in t.cell_edges():
            (s1,s2)=i
            x2[ self.wall2sys[(s1,s2)] ] = self.c_lambda*Fi(J((s1,s2),t,x))+self.c_qmin-self.c_theta*P((s1,s2),t,x)
            x2[ self.wall2sys[(s2,s1)] ] = self.c_lambda*Fi(J((s2,s1),t,x))+self.c_qmin-self.c_theta*P((s2,s1),t,x)            
        return x2
            
    def i_local_evacuate( self, cell ):
        t = self.system.tissue
        if t.cell_property( cell=cell, property="PrC") > 0:
            return 1
        else:
            return 0
        
    def i_center_evacuate( self, cell ):
        t = self.system.tissue
        if t.cell_property( cell=cell, property="IC") > 0:
            return 1
        else:
            return 0
        
    def prim_distance_mod(self, cell_id ):
        t = self.system.tissue
        center_pos = self.system.simulation_remove_cell_strategy.center
        PrC_pos = t.cell_center( cell_id )
        d = visual.mag( PrC_pos-center_pos )
        x = (self.system.simulation_remove_cell_strategy.remove_2d_radius - d)/self.system.simulation_remove_cell_strategy.remove_2d_radius
        if x <0 or x>1:
            raise Exception("Wrong value for a modificator [0,1]: "+str(x))
        return x
        
    def init_aux(self):
        t = self.system.tissue
        #s = self.aux_pro_exa*t.calculate_cell_surface( cell=c )/self.system.const.cs_surf_max_surface_before_division
        #for c in t.cells():
        #    if t.cell_property(cell= c, property="IC"):
        #        IC = c
        #for i in range( 20 ):
        #    for c in t.nth_layer_from_cell( cell = IC, distance=i, smaller_than=True):
        #        self.aux_con(cell= c, con= self.aux_con( cell =c ) + self.aux_ini_NZ_gra_con_exa )
        #for i in range( 10 ):
        #    for c in t.nth_layer_from_cell( cell = IC, distance=i, smaller_than=True):
        #        self.aux_con(cell= c, con= self.aux_con( cell =c ) + self.aux_ini_IZ_con_exa)
        #        
        for c in t.cells():
            self.aux(cell= c, value= self.c_initial_aux_value ) #+random.random() )
        #for i in t.cell_edges():
        #    (s,t)=i
        #    self.pin( cell_edge=(s,t), value=self.c_qmin)
        #    self.pin( cell_edge=(t,s), value=self.c_qmin)
          
    def search_for_primodium( self ):
        t = self.system.tissue
        pc = []
        for c in t.cells():
            if t.cell_property( cell=c, property="PZ"):
                if self.aux( cell = c ) > self.aux_prim_trs_con:
                    pc.append( c )
        return pc
        
    def create_primordiums( self, primordium_cand=None):
        t = self.system.tissue
        if len(primordium_cand)>0:
            primordium_cand.sort( lambda x, y: cmp( self.aux( cell = y ),  self.aux( cell = x ) ))
            c = primordium_cand[ 0 ]
            t.cell_property( cell=c, property="PrC", value=self.nbr_prim)
            t.cell_property( cell=c, property="PrZ", value=self.nbr_prim)
            for n in t.cell_neighbors( c ):
                t.cell_property( cell=n, property="PrZ", value=self.nbr_prim)
            self.nbr_prim+=1

class PhysAuxinTransportModel14(PhysAuxinTransportModel):
    """Model with correct resolution using scipy RK4 method and waiting for
    stabilisation.
    
    The parameters form ?
    """

    def __init__(self, tissue_system = None):
        PhysAuxinTransportModel.__init__( self, tissue_system=tissue_system)
        self.system = tissue_system
        self.nbr_prim=1
        self.t = 0
        self.h = 5
        self.c_change = 0.0005 #acceptable change could not be smaller to classifie as error.
        
        
        self.c_alpha = 0.0005 #creation
        self.c_beta = 0.0005 #destruction
        self.c_gamma = 0.0075#25 #active flux
        self.c_kappa = 0.05  #diffusion
        
        self.c_lambda = 0.03 # PIN production depanding on flux
        self.c_qmin = 0.005 #min production of PIN
        self.c_theta=0.005 #decay of PIN
        self.c_pin_max=1.2 #this limits the number of pin to c_pin_max*c_qmin
        
        self.c_epsilon=0.03 #centre evacuate
        self.c_delta = 0.09 #prim evacuate


        self.aux_prim_trs_con = 0.4#0.62
        self.c_initial_aux_value=0.5

        """
        auxin_level == nbr of aux particles in a cell
        auxin_level_1 == change in number of particles of aux
        """
    def apply( self ):
        self.step( )
         
    def step( self, nbr_step=1, precision=1 ):
        t = self.tissue_system.tissue
        self.prepare_sys_map()
        stable=False
        i=0
        while not stable:
            print " #: phys aux trans: loop=", i, " time=",self.t
            i+=1
            res= scipy.integrate.odepack.odeint( self.f, self.prepare_x0(), [self.t, self.t+self.h],rtol=0.01, atol=0.001 )
            self.t += self.h                
            stable = self.rate_error( res[0], res[1])
            self.update( res[1] )
            y=[]
            z = 0
            # quantities
            for j in self.cell2sys:
                y.append(res[1][ self.cell2sys[ j ] ] )
                z +=  res[1][ self.cell2sys[ j ] ]
            print "  #: aux qua avg: ", z/len( self.tissue_system.tissue.cells() ), "aux qua min:", min(y), "aux qua max:", max(y)
            y2=[]
            z2=0
            for j in self.wall2sys:
                y2.append(res[1][ self.wall2sys[ j ] ] )
                z2 +=  res[1][ self.wall2sys[ j ] ]
            #print y
            print "  #: pin qua avg: ", z2/len( y2 ), "pin qua min:", min(y2), "pin qua max:", max(y2)
            #concentration
            #for i in self.cell2sys:
            #    y.append(res[1][ self.cell2sys[ i ] ]/t.calculate_cell_surface(cell=i) )
            #    z +=  res[1][ self.cell2sys[ i ] ]/t.calculate_cell_surface(cell=i)
            #print "aux con avg: ", z/len( self.tissue_system.tissue.cells() ), "aux con min:", min(y), "aux con max:", max(y)

        self.create_primordiums(self.search_for_primodium())
        ##cc = self.tissue_system.tissue.cell_centers()
        ##for c in self.tissue_system.tissue.cells():
        ##    cc[ c ].z = self.aux( cell=c )
        ##X,Y,Z=[],[],[]
        ##for i in cc:
        ##    X.append(cc[i].x)
        ##    Y.append(cc[i].y)
        ##    Z.append(cc[i].z)
        ##(X,Y,Z)=tools.create_grid_from_discret_values(X,Y,Z)
        ###tools.plot_3d_height_map( X,Y,Z)
        ##tools.test( X,Y,Z)
        ##import pylab
        ##pylab.plot(Y,Z[int(len(X)/2)])
        ##pylab.show()
        
    def update( self, x ):
        t = self.system.tissue
        for i in t.cells():
            t0 = x[ self.cell2sys[ i ] ]
            t0 = max(0,t0)
            self.aux( cell=i, value= t0)
        for i in t.cell_edges():
            (c1,c2)=i
            t1=x[ self.wall2sys[ (c1,c2) ] ]
            t2=x[ self.wall2sys[ (c2,c1) ] ]
            t1 = max(0, min( t1,self.c_pin_max))
            t2 = max(0, min( t2,self.c_pin_max))
            self.pin( cell_edge=(c1,c2), value=t1 )
            self.pin( cell_edge=(c2,c1), value=t2 )        
    

    def rate_error( self, xn, xnprim ):
        t = True
        max = -float("infinity")
        for i in range( len( self.tissue_system.tissue.cells() )):
            if abs( xn[i] - xnprim[i] ) > max:
                max=abs( xn[i] - xnprim[i] )
            if self.c_change < abs( xn[i] - xnprim[i] ):
                t=False 
                #break
        print " #: errror =  ", max# abs( xn[i] - xnprim[i] )
        return t

    def prepare_x0( self ):
        x0 = []
        t = self.system.tissue
        for x in range( len(t.cells()) + len( 2*t.cell_edges() ) ):
            x0.append(0)
        for i in t.cells():
            x0[ self.cell2sys[ i ] ] = self.aux( i )
        for i in t.cell_edges():
            (s,t)=i
            x0[ self.wall2sys[ (s,t) ] ] = self.pin( cell_edge=(s,t) )
            x0[ self.wall2sys[ (t,s) ] ] = self.pin( cell_edge=(t,s) )
        return x0

    def prepare_sys_map( self ):
        self.cell2sys = {}
        self.wall2sys = {}
        t = self.system.tissue
        ind = 0
        for i in t.cells():
            self.cell2sys[ i ] = ind
            ind += 1
        for i in t.cell_edges():
            (s,t) = i
            self.wall2sys[ (s,t) ] = ind
            ind += 1
            self.wall2sys[ (t,s) ] = ind
            ind += 1

    def f( self, x, t ):
        def Fi( x ):
            if x < 0:
                return 0
            return x*x
        
        def P( wid, t, x):
            return x[ self.wall2sys[ wid ] ] 

        def D( (i, j), t, x):
            return (A(i,t,x)-A(j,t,x))
        
        def J( (i, j), t, x):
            #return self.c_gamma*(-A(j,t,x)*P((j,i),t,x)+A(i,t,x)*P((i,j),t,x))+(A(i,t,x)-A(j,t,x))*self.c_kappa #diff+act
            #return (A(i,t,x)-A(j,t,x))*self.c_kappa #diff OK
            return (-A(j,t,x)*P((j,i),t,x)+A(i,t,x)*P((i,j),t,x))#act OK
            #concentration
            #return self.c_gamma*(-A(j,t,x)*P((j,i),t,x)*t.calculate_cell_surface(cell=j)*t.calculate_cell_surface(cell=j)+A(i,t,x)*P((i,j),t,x)*t.calculate_cell_surface(cell=i)*t.calculate_cell_surface(cell=i))#act OK
        def A( cid, t, x ):
            return x[ self.cell2sys[ cid ] ]
        
        t = self.tissue_system.tissue
        x2 = copy.copy( x )
        for i in t.cells():
            #x2[ self.cell2sys[ i ] ] = 0
            #x2[ self.cell2sys[ i ] ] = - self.c_delta*self.i_center_evacuate( i ) #OK
            x2[ self.cell2sys[ i ] ] = self.c_alpha - A(i,t,x)*(self.c_beta+self.c_epsilon*self.i_center_evacuate( i ))#OK
            if self.i_local_evacuate( i ):
                x2[ self.cell2sys[ i ] ] -= self.c_delta*self.prim_distance_mod( i )*A(i,t,x)
            for n in t.cell_neighbors( cell=i ):
                x2[ self.cell2sys[ i ] ] += self.c_gamma*J((n,i),t,x)
            #concentration:
            #x2[ self.cell2sys[ i ] ] = t.calculate_cell_surface(cell=i)/t.const.cs_surf_max_surface_before_division*self.c_alpha - self.c_beta*A(i,t,x)/t.calculate_cell_surface(cell=i) #- self.c_delta*self.i_local_evacuate( i ) -self.c_epsilon*self.i_center_evacuate( i )#OK
        for i in t.cell_edges():
            (s1,s2)=i
            x2[ self.wall2sys[(s1,s2)] ] = self.c_lambda*Fi(J((s1,s2),t,x))+self.c_qmin-self.c_theta*P((s1,s2),t,x)
            x2[ self.wall2sys[(s2,s1)] ] = self.c_lambda*Fi(J((s2,s1),t,x))+self.c_qmin-self.c_theta*P((s2,s1),t,x)            
        return x2
            
    def i_local_evacuate( self, cell ):
        t = self.system.tissue
        if t.cell_property( cell=cell, property="PrC") > 0:
            return 1
        else:
            return 0
        
    def i_center_evacuate( self, cell ):
        t = self.system.tissue
        if t.cell_property( cell=cell, property="IC") > 0:
            return 1
        else:
            return 0
        
    def prim_distance_mod(self, cell_id ):
        t = self.system.tissue
        center_pos = self.system.simulation_remove_cell_strategy.center
        PrC_pos = t.cell_center( cell_id )
        d = visual.mag( PrC_pos-center_pos )
        x = (self.system.simulation_remove_cell_strategy.remove_2d_radius - d)/self.system.simulation_remove_cell_strategy.remove_2d_radius
        if x <0 or x>1:
            raise Exception("Wrong value for a modificator [0,1]: "+str(x))
        return x
        
    def init_aux(self):
        t = self.system.tissue
        #s = self.aux_pro_exa*t.calculate_cell_surface( cell=c )/self.system.const.cs_surf_max_surface_before_division
        #for c in t.cells():
        #    if t.cell_property(cell= c, property="IC"):
        #        IC = c
        #for i in range( 20 ):
        #    for c in t.nth_layer_from_cell( cell = IC, distance=i, smaller_than=True):
        #        self.aux_con(cell= c, con= self.aux_con( cell =c ) + self.aux_ini_NZ_gra_con_exa )
        #for i in range( 10 ):
        #    for c in t.nth_layer_from_cell( cell = IC, distance=i, smaller_than=True):
        #        self.aux_con(cell= c, con= self.aux_con( cell =c ) + self.aux_ini_IZ_con_exa)
        #        
        for c in t.cells():
            self.aux(cell= c, value= self.c_initial_aux_value ) #+random.random() )
        #for i in t.cell_edges():
        #    (s,t)=i
        #    self.pin( cell_edge=(s,t), value=self.c_qmin)
        #    self.pin( cell_edge=(t,s), value=self.c_qmin)
          
    def search_for_primodium( self ):
        t = self.system.tissue
        pc = []
        for c in t.cells():
            if t.cell_property( cell=c, property="PZ"):
                if self.aux( cell = c ) > self.aux_prim_trs_con:
                    pc.append( c )
        return pc
        
    def create_primordiums( self, primordium_cand=None):
        t = self.system.tissue
        if len(primordium_cand)>0:
            primordium_cand.sort( lambda x, y: cmp( self.aux( cell = y ),  self.aux( cell = x ) ))
            c = primordium_cand[ 0 ]
            t.cell_property( cell=c, property="PrC", value=self.nbr_prim)
            t.cell_property( cell=c, property="PrZ", value=self.nbr_prim)
            for n in t.cell_neighbors( c ):
                t.cell_property( cell=n, property="PrZ", value=self.nbr_prim)
            self.nbr_prim+=1


#------------------------------------------------------------------------------- main 

if __name__ == "__main__":
    st = TissueSystem( const = HoneySlice2DConst() ) 
    st.mainloop()
