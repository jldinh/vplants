#!/usr/bin/env python
"""simulationRemoveCellStrategy.py

Contains different strategies used to decrease nbr of points in the simulation. Strategies *are* using
WalledTissue DS.


:version: 2006-07-15 15:21:06CEST
:author: szymon stoma
"""
import visual

class SimulationRemoveCellStrategy:
    """Interface
    """
    #TODO change on tissue system
    def __init__( self, system=None ):
        self.system = system
        
    def cells_to_remove( self ):
        print " ! SimulationRemoveCellStrategy::cells_to_remove not defined.."

    def cells_to_fix( self ):
        print " ! SimulationRemoveCellStrategy::cells_to_fix not defined.."

    def _update_df_limits(self):
        """Updates the limits for dropped and fixed.
        """
        return
    
class SimulationRemoveCellStrategy2D_1(SimulationRemoveCellStrategy):
    """Strategy to remove points from 2D simulation basing on the center of grwoth field
    """
    
    def __init__( self, system=None):
        """Inits cells to remove. Returns a list  filled with
        ids of cells which are observed to remove.
        """
        SimulationRemoveCellStrategy.__init__( self, system=system)
        v =  visual.vector()
        masses=self.system.masses
        for i in masses:
            v += i.pos
        self.center = v / len(masses)
        self.remove_2d_radius=450
        
    def cells_to_remove(self):
        """Returns cells  to remove acording to curtent strategy.
        """
        l = []
        cc=self.system.tissue.cell_centers()
        for c in self.system.tissue.cells():
            if visual.mag( cc[ c ] - self.center) > self.remove_2d_radius:
                l.append( c )
        return l
    
    def cells_to_fix( self ):
        return []

class SimulationRemoveCellStrategy2D_2(SimulationRemoveCellStrategy):
    """Strategy to remove points from 2D simulation basing on the center of grwoth field
    """
    
    def __init__( self, system=None):
        """Inits cells to remove. Returns a list  filled with
        ids of cells which are observed to remove.
        """
        SimulationRemoveCellStrategy.__init__( self, system=system)
        v =  visual.vector()
        masses=self.system.masses
        for i in masses:
            v += i.pos
        self.center = v / len(masses)
        
    def cells_to_remove(self):
        """Returns cells  to remove acording to curtent strategy.
        """
        l = []
        cc=self.system.tissue.cell_centers()
        for c in self.system.tissue.cells():
            if visual.mag( cc[ c ] - self.center) > 2000:
                l.append( c )
            #if visual.mag( cc[ c ] - self.center) > 200:
            if self.system.tissue.cell_property( c, "PrC" )==0 and not self.system.tissue.cell_property( c, "PZ" ) and not self.system.tissue.cell_property( c, "CZ" ):
                l.append( c )
        return l
    
    def cells_to_fix( self ):
        return []

class SimulationRemoveCellStrategy3D1_1(SimulationRemoveCellStrategy):
    """Strategy to remove cells from 3D simulation
    1/ lowest from z point of view,
    """
    
    def __init__( self, system=None):
        """Inits cells to remove. Returns a list  filled with
        ids of cells which are observed to remove.
        """
        SimulationRemoveCellStrategy.__init__( self, system=system)
        self._fixed_border = 0.
        self._dropped_border = 0.
        self._update_df_limits()
        self._cells_to_remove = self._init_cells_to_remove()
        self._cells_to_fix = self._init_cells_to_fix()
        
    def _init_cells_to_remove( self ):
        """Inits SimulationRemoveCellStrategy3D1_1 cell to remove list
        """
        CR = []
        for c in self.system.tissue.cells():
            #if self.check_cell_remove_from_simulation( cell = c )
            CR.append( c )
        return CR
 
    def _init_cells_to_fix( self ):
        """Inits SimulationRemoveCellStrategy3D1_1 cell to remove list
        """
        CR = []
        for c in self.system.tissue.cells():
            #if self.check_cell_remove_from_simulation( cell = c )
            CR.append( c )
        return CR
 

    def _check_wv_remove_from_simulation( self, wv=None ):
        """Strategy for removing cell from simulation.
        """
        return self.system.tissue.wv_pos( wv=wv ).z < self._dropped_border

    def _check_wv_fix_in_simulation( self, wv=None ):
        """Strategy for removing cell from simulation.
        """
        return self.system.tissue.wv_pos( wv=wv ).z < self._fixed_border

    def check_cell_remove_from_simulation(self, cell=None):
        """Returns True iff cell should be removed from simulation
        """
        for wv in self.system.tissue.cell2wvs( cell ):
            if self._check_wv_remove_from_simulation( wv = wv): 
                return True
        return False

    def check_cell_fix_in_simulation(self, cell=None):
        """Returns True iff cell should be removed from simulation
        """
        for wv in self.system.tissue.cell2wvs( cell ):
            if self._check_wv_fix_in_simulation( wv = wv): 
                return True
        return False

            
    def _update_df_limits(self):
        """Updates the limits for dropped and fixed.
        """
        max = -1*float("infinity")
        for m in self.system.masses:
            if m.pos.z > max:
                max = m.pos.z
        self._fixed_border = max - self.system.const.fixed_border
        self._dropped_border = max - self.system.const.dropped_border
        
    def cells_to_remove(self):
        """Returns cells  to remove acording to curtent strategy.
        """
        l = []
        for c in self.system.tissue.cells():
            if self.check_cell_remove_from_simulation( c ):
                l.append( c )
        return l
    
    def cells_to_fix( self ):
        l = []
        for c in self.system.tissue.cells():
            if self.check_cell_fix_in_simulation( c ):
                l.append( c )
        return l


