#!/usr/bin/env python
"""System for phys. based simulation.

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
__revision__="$Id: system.py 7875 2010-02-08 18:24:36Z cokelaer $"


import visual
import math
import sets
import random
import pickle



import openalea.plantgl.all as pgl
from merrysim import *
import openalea.mersim.tissue.walled_tissue as w
from openalea.mersim.const.const import *
from openalea.mersim.gui.tissue import *
import simulationRemoveCellStrategy
import tools
import 

#-------------------------------------------------------------------------------System
class System:
    """The system. should be two routines of adding springs and masses (this is ruled by spring2mass_tag):
    -- without any relation, so one can delate mass and spring any time,
    -- with relation, when removing spring removes also disconnected masses.
    TODO: 
    * update_simulation is sth. which should be removed..
    * drop copying values from conf. better to use them directly
    * prepare for changing the time in the simulation to adjust the time step
    """

    def __init__(self, const = "!SetCorrectConstants!", time=0., **keywords):
        """Construct a system.
        """
        self.const = const 
        """#: constants containing parameters necessary for simulations"""
        
        self.timestep = self.const.sim_timestep
        self.run = self.const.system_run #: simulation control state
            
        self.time = time         
        self.masses = []
        self.forces = {}
        
        self._pov_title = 0
        self.spring2mass_tag = self.const.system_spring2mass_tag
        
        if self.const.system_forces_spring: self.forces["spring_force"] = SpringForce( self )
        if self.const.system_forces_visco: self.forces["visco_force"]  = ViscoForce( self, self.const.max_system_viscosity )
        if self.const.system_forces_gravity: self.forces["gravity_force"] = GravityForce( self, self.const.gravity_const )
        if self.const.system_forces_uniform_up: self.forces["uniform_up"] = UniformUpForce( self, self.const.max_up_force )
        if self.const.system_forces_radial_move: self.forces[ "radial_move" ] = RadialMoveForce( self )
        
    def insert_mass(self, mass):
        """Insert mass into the system.
        """
        self.masses.append(mass)
    

    def find_mass_with_coords(self, vector):
        """Finds mass which has the same coords
        """
        for m in self.masses:
          if (m.pos.x == vector.x) and (m.pos.y == vector.y) and (m.pos.z == vector.z):
            return self.masses.index(m)
        return None

    def insert_spring(self, spring):
        """Insert spring into the system.
        """
        self.forces["spring_force"].springs.append(spring)
        if self.spring2mass_tag == "connected":
            spring.m0.connect( spring )
            spring.m1.connect( spring )

    def remove_spring(self, spring, leave_visible=False):
        """Removes spring from the system.
        """
        #Vspring.vspring.visible = 0
        self.visualisation.remove_vspring( spring, leave_visible=leave_visible )

        self.forces["spring_force"].springs.remove( spring )
        if self.spring2mass_tag == "connected":
            spring.m0.disconnect( spring )
            spring.m1.disconnect( spring )
        del spring
        

    def remove_mass(self, m, leave_visible=False):
        """Removes mass from the system.
        """
        self.visualisation.remove_vmass( m, leave_visible=leave_visible  )
        self.masses.remove( m )

    def spring_growth( self ):
        for s in self.forces[ "spring_force" ].springs:
            s.spring_growth( factor=self.const.spring_growth_rate )
    
    def spring_growth_if_under_tension( self ):
        for s in self.forces[ "spring_force" ].springs:
            s.spring_growth_if_under_tension( factor=self.const.spring_growth_rate )
    

    def step(self):
        """Perform one Iteration of the system by advancing one timestep.
        """
        for mass in self.masses:
            mass.clear_force()
        self.oversample = 1.
        microstep = self.timestep / self.oversample
        self.time += self.timestep
        
        for i in range(self.oversample):
            for f in self.forces.values():
                f.apply()
        
        for mass in self.masses:
            if not mass.fixed:
                mass.calc_new_location(microstep)



            
    def mainloop(self):
        """Start the mainloop, which means that step() is
        called in an infinite loop if self.run == True.
        """
        print "System:mainloop"

        while True:
            if self.run: self.step()
            self.visualisation.update()
            self.clear_forces()



    def clear_forces( self ):
        for m in self.masses:
            m.clear_force()

    def find_springs_conected_with_mass(self, mass):
        l = []
        for s in self.forces["spring_force"].springs:
            if s.m0 == mass:
                l.append(s)
            elif s.m1 == mass:
                l.append(s)
        return l

 

#------------------------------------------------------------------------------- TissueSystem
class TissueSystem( System ):
    def __init__(self, const="!SetCorrectConstants!", file_name="!setCorrectMeristemDataFilename!", tissue=None ):
        """Spring based meristem simulation using the mass-spring system.
        """
        if tissue:
            System.__init__(self, const=const, time=tissue.time) 
        else:
            System.__init__(self, const=const) 
            
        self.tissue_system_forces_cell_pressure = self.const.tissue_system_forces_cell_pressure
        
        # finding the meristem data
        if file_name == "!setCorrectMeristemDataFilename!":
            file_name = self.const.meristem_data


        self.frame_nbr = property( fget=self._get_frame_nbr, fset=self._set_frame_nbr )
        self.frame_nbr = 0 #: used to store frame numbers to grab/output
        self.turn_on = True
        self.file_name = file_name
        self._mass2id = {}
        self._spring2id = {}
        self._id2mass = {}
        self._id2spring = {}
        self.visualisation = None
        
        self.phys = {}
        #: to store physiologial processes
        
        if self.const.visualisation_system == "frame":
            self.visualisation = FrameTissueSystemVisualisationVisual( self )
        elif  self.const.visualisation_system == "surface":
            self.visualisation = SurfaceTissueSystemVisualisationVisual( self )
        elif  self.const.visualisation_system == "sphereCells":
            self.visualisation = SphereTissueSystemVisualisationVisual( self )
        elif self.const.visualisation_system == "empty":
            self.visualisation = TissueSystemVisualisation( self )
        
        # initialising tissue
        self.tissue = w.WalledTissue( const = self.const)            
        #self.tissue.create(
        #    wv2pos = {
        #        1: visual.vector(-0.1,-0.1,99),
        #        2: visual.vector(-0.1,0.1,99),
        #        3: visual.vector(0.1,0.1,99),
        #        4: visual.vector(0.1,-0.1,99),
        #        5: visual.vector(0.3,0.1,99),
        #        6: visual.vector(0.3,-0.1,99)
        #    },
        #    cell2wv_list = {
        #        1: [1,2,3,4],
        #        2: [4,3,5,6]
        #    }
        #)
        #self.load_pickled_WalledTissue_data( filename="2007-01-27-start.pickle")
        #self.load_pickled_WalledTissue_data( filename="07-03-07-notManyCells,canalisationTests.pickle")
        self.load_pickled_WalledTissue_data( filename="07-03-08-canalisationWithGradientDistribution.pickle")
        # create mss from tissue
        self.load_meristem_surface(tissue=self.tissue)
        # clear old properties
        self.tissue.clear_properties()
        # adds cells and all post-visualisation
        #self.visualisation.init_after_meristem_creation()

        # choosing division strategy
        if self.const.division_strategy == "dscs_shortest_wall_with_equal_surface":
            self.division_strategy = w.WalledTissue.dscs_shortest_wall_with_equal_surface
        if self.const.division_strategy == "dscs_shortest_wall":
            self.division_strategy = w.WalledTissue.dscs_shortest_wall
        if self.const.division_strategy == "dscs_shortest_wall_with_geometric_shrinking":
            self.division_strategy = w.WalledTissue.dscs_shortest_wall_with_geometric_shrinking
        
        # active tissue forces
        if self.const.tissue_system_forces_cell_pressure: self.forces["cell_pressure_force"] = CellPressureForce( self, self.tissue, self.const.cell_pressure_const )
        if self.const.tissue_system_forces_simple_pressure: self.forces["simple_pressure_force"] = SimplePressureForce( self, self.const.simple_pressure_const )
        #TODO add all forces
        #if self.tissue_system_forces_simple_pressure_under_primordium: self.forces["simple_pressure_force_under_primordium"] = SimplePressureForceUnderPrimordium( self, self.const.simple_pressure_under_primordium_const )
        #self.forces["simple_pressure_force_under_primordium"] = SimplePressureForceUnderPrimordium( self, self.const.simple_pressure_under_primordium_const )
        
        # active physiologicall processes
        #if self.const.tissue_sy#if self.tissue_system_forces_simple_pressure_under_primordium: stem_phys_mark_cell_identities: self.phys["mark_cell_identities" ] = PhysMarkCellIdentitiesWithTopIC( self )
        if self.const.tissue_system_phys_mark_cell_identities: self.phys["mark_cell_identities" ] = PhysMarkCellIdentitiesWithFixedRegionsIn2D_1( self ) #PhysMarkCellIdentitiesWithCentralIC( self )
        if self.const.tissue_system_phys_aux_flow: self.phys["auxin_transport_model" ] = PhysAuxinTransportModel14( self )
        
        #setting up cell removing/fixing
        self.update_tissue()
        self.simulation_remove_cell_strategy = simulationRemoveCellStrategy.SimulationRemoveCellStrategy2D_1( system=self )
        self.fix_cells( self.simulation_remove_cell_strategy.cells_to_fix() )

        self.visualisation.adjust_display()

            
    def fix_cells( self, cells_to_fix=None ):
        for c in cells_to_fix:
            for n in self.tissue.cell_neighbors( cell = c ):
                self.tissue.cell_property( cell = n, property="border_cell", value = True )

            for wv in self.tissue.cell2wvs( c ):
                self._id2mass[ wv ].set_fixed( fixed=True )
                self.visualisation.set_vmass_fixed( self._id2mass[ wv ], fixed=True )
                
    def remove_cells( self, cells_to_remove=None, leave_visible=False ):
        for c in cells_to_remove:
            if not self.tissue._cells.has_node( c ):
                print " !asked to remove non existing cell.."
                return
            r = self.tissue.remove_cell( cell=c )
            for i in r[ "removed_wv_edges" ]:
                self.remove_wall( i, leave_visible=leave_visible )
            for i in r[ "removed_wv" ]:
                self.remove_wv( i, leave_visible=leave_visible )    
            self.visualisation.remove_vcell( cell=c, leave_visible=leave_visible)
            self.visualisation.remove_vmt( cell=c )

    
    def _set_frame_nbr( self, frame_nbr):
        """For setting the property
        """
        self._frame_nbr=frame_nbr

    def _get_frame_nbr( self ):
        """For getting the property
        """
        return self._frame_nbr

    def id2spring( self, id, s = None ):
        """Returns/sets spring s identified by id. """

        w1, w2 = self.tissue.wv_edge_id( id )
        if s == None:
            return self._id2spring[ (w1, w2) ]
        else:
            self._id2spring[ (w1, w2) ] = s

    def spring2id( self, s, id = None ):
        """Returns/sets id for a spring s """
        if id == None:
                return self._spring2id[ s ]
        else:
            w1, w2 = self.tissue.wv_edge_id( id )
            self._spring2id[ s ] = (w1, w2)



    def insert_wall( self, id, l0 = None, color= Color.spring, update_color=False, **kwd ):
        """Inserts wall into simulation. If wall already exist -- does nothing."""
        v1d, v2d = id
        if not self._id2mass.has_key( v1d ) or not self._id2mass.has_key( v2d ):
            raise Exception("Wall vertex of created spring doesn't exist.")
        #if self._id2spring.has_key( id ):
        #    return
        m0 = self._id2mass[ v1d ]
        m1 = self._id2mass[ v2d ]
        spring = Spring(
            m0= m0, 
            m1= m1, 
            k=self.const.spring_standart_k,
            l0 = l0,
            damping=self.const.spring_standart_damping, 
            radius=self.const.spring_standart_radius, 
            color=color,
            system=self
            )
        self.insert_spring( spring )
        self.spring2id( spring, (v1d, v2d) )
        self.id2spring( (v1d, v2d), spring)
        


    def insert_wall_vertex( self, id, pos, velocity = visual.vector(), **kwd ):
        """Inserts wall vertex into simulation. If wall vertex already exist -- does nothing."""
        v1 = pos 
        m1 = Mass(
            m=self.const.mass_standart_mass, 
            pos=pos, #TODO TEST visual.vector( v1.x, v1.y, v1.z ),
            v = velocity,
            r=self.const.mass_standart_radius, fixed=False, 
            color=Color.normal_point,
            system=self)
        self.insert_mass( m1 )
        self._mass2id[ m1 ] = id
        self._id2mass[ id ] = m1

    def load_meristem_surface( self, tissue=None ):
        """Creates meristem surface in SSM from WalledTissue or other tissue data.
        """
        self.tissue = tissue            
        t = self.tissue
        for wv in t.wvs():
            self.insert_wall_vertex(id = wv, pos = t.wv_pos( wv ))
            m = self._id2mass[ wv ]
            m.m = self.tissue.wv_property( wv = wv, property="m")
            m.v = self.tissue.wv_property( wv = wv, property="v")
            m.F = self.tissue.wv_property( wv = wv, property="F")
            m.fixed = self.tissue.wv_property( wv = wv, property="fixed")

        for e in t.wv_edges():
            self.insert_wall( id = e )
            s = self.id2spring( e )
            s.k = self.tissue.wv_edge_property( wv_edge= e, property="k")
            s.l0 = self.tissue.wv_edge_property( wv_edge= e, property="l0")

    def create_meristem_surface( self ):
        """Creates meristem surface in SSM from WalledTissue or other tissue data.
        """
        t = self.tissue
        for wv in t.wvs():
            self.insert_wall_vertex(id = wv, pos = t.wv_pos( wv ))

        for e in t.wv_edges():
            self.insert_wall( id = e )
        try:
            self.un_pickle_fixed()
        except Exception:
            print "Fixed not loaded -- file doesn't exit."


    def dispatch_physiology( self ):
        """Runs every physiological process for current experiment.
        """
        if self.const.tissue_system_phys_mark_cell_identities: self.phys["mark_cell_identities" ].apply()
        if self.const.tissue_system_phys_aux_flow: self.phys["auxin_transport_model" ].apply()



    def mainloop(self):
        """Start the mainloop, which means that step() is
        called in an infinite loop if self.run == True.
        """
        self.dispatch_physiology()
        while self.turn_on: #and self.frame_nbr<600:
            if self.run:
                self.visualisation.gui_events()
                self.step()#_until_stable()
                self.update_tissue()
                #self.divide_cells()
                #self.dispatch_physiology()

                if self.const.remove_cells:
                    self.simulation_remove_cell_strategy._update_df_limits()
                    self.fix_cells( self.simulation_remove_cell_strategy.cells_to_fix() )
                    self.remove_cells( self.simulation_remove_cell_strategy.cells_to_remove() )
                if self.const.spring_growth: self.spring_growth_if_under_tension()
                if self.const.save_simulation:
                    self.save_pickled_WalledTissue_data()
                self.divide_cells()
                self.dispatch_physiology()
                
                if not(self.frame_nbr % self.const.visualisation_update_frequency):
                    self.visualisation.update()
                    if self.const.system_grab_scene:
                        self.visualisation.grab_scene_to_pov()

                self.frame_nbr = self.frame_nbr+1
                print "@ step nbr: ", self.frame_nbr, "time:", self.tissue.time, "cells:", len( self.tissue.cells() )#,"pressure:", self.forces["simple_pressure"].pressure
            else:
                self.visualisation.gui_events()
                if self.const.system_grab_scene:
                    self.visualisation.grab_scene_to_pov()
                self.frame_nbr = self.frame_nbr+1
        self.turn_on = True

    def play_simulation(self):
        """Plays recorded simulation.
        """
        while self.turn_on:
            self.visualisation.clean()
            self.load_pickled_WalledTissue_data()
            self.load_meristem_surface(tissue=self.tissue)
            #self.tissue.clear_properties()
            # adds cells and all post-visualisation
            self.visualisation.init_after_meristem_creation()
            if self.const.system_grab_scene:
                self.visualisation.grab_scene_to_pov()
            #raw_input()
            self.visualisation.gui_events()

            self.frame_nbr = self.frame_nbr+1
            print "@ step nbr: ", self.frame_nbr, "time:", self.tissue.time, "cells:", len( self.tissue.cells() )#,"pressure:", self.forces["simple_pressure"].pressure
        self.turn_on = True


    def step_until_stable(self, step_number=None):
        """Perform one Iteration of the system by advancing to reach stable state.
        """
        #TODO testing: moved to cleaning step. visualisation is using this values
        try:
            max_force = self.const.max_trashhold_stable_state_force
            max_force_prev = self.const.max_trashhold_stable_state_force+1
            if step_number==None:
                step_number = 0
            current_step = 0
            real_step=0
            while math.fabs( max_force - max_force_prev) >= self.const.max_trashhold_stable_state_force and current_step <= step_number:
                if step_number == 0: max_force_prev = max_force
                self.update_tissue()
                for mass in self.masses:
                    mass.clear_force()
                microstep = self.timestep / self.oversample
                self.time += self.timestep
                
                for i in range(self.oversample):
                    for f in self.forces.values():
                        f.apply()
                
                for mass in self.masses:
                    if not mass.fixed:
                        mass.calc_new_location(microstep)
                
                if step_number == 0:
                    max_force = 0.        
                    for mass in self.masses:
                        if not mass.fixed:
                            if visual.mag( mass.v ) >  max_force:
                                max_force = visual.mag( mass.v )
                
                
                self.divide_cells()

                if step_number != 0: current_step += 1
                real_step += 1
                if not(real_step % self.const.visualisation_update_frequency):
                    pass#self.visualisation.update()
                self.frame_nbr +=1
                print "substep", real_step, ": max F=", max_force, "f_k - f_(k-1)=", math.fabs(max_force - max_force_prev)
        except Exception:
            pass


    def clear_simulation( self ):
        """Clears the simulation registers to prepare to load new tissue.
        Also clears the display.
        """
        self.visualisation.clean()
        self._mass2id.clear()
        self._id2mass.clear()
        self.masses = []
        self.springs = []

    def load_pickled_WalledTissue_data( self, filename=None, masses_filename=None, springs_filename=None ):
        if filename == None:
            filename = self.const.pickled_WalledTissue_data_folder+str( self.frame_nbr )+"_WalledTissue.pickle"
        self.tissue = pickle.load( open( filename ) )        
        print "loaded: ", filename#, masses_filename, springs_filename 
        self.time = self.tissue.time
        #self.const = self.tissue.const
        #self.__init__( file_name=None, const=self.const, tissue=self.tissue )
    
    
    def save_pickled_WalledTissue_data( self, filename=None, masses_filename=None, springs_filename=None ):
        #TODO protocol
        if filename == None:
            filename = self.const.pickled_WalledTissue_data_folder+str( self.frame_nbr )+"_WalledTissue.pickle"
        # preparing the the mechanical data to export
        for s in self.forces["spring_force"].springs:
            sid = self.spring2id( s )
            self.tissue.wv_edge_property( wv_edge= sid, property="k", value=s.k)
            self.tissue.wv_edge_property( wv_edge= sid, property="l0", value=s.l0)

        for m in self.masses:
            mid = self._mass2id[ m ]
            self.tissue.wv_property( wv= mid, property="m", value=m.m)
            self.tissue.wv_property( wv= mid, property="v", value=m.v)
            self.tissue.wv_property( wv= mid, property="F", value=m.F)
            self.tissue.wv_property( wv= mid, property="fixed", value=m.fixed)
        
        # const is also already pickled
        pickle.dump( self.tissue, open( filename, "w") )
        print "pickled: ", filename#, masses_filename, springs_filename 
        
    def divide_cells( self ):
        """Triggers the divide cell from tissue
        """
        if self.const.cells_divide:
            for i in self.tissue.ds_surface( self.division_strategy ):
                ( ( ( v1d, p1 ), (v2d, p2) ), ( ( v1d, s1 ), ( v1d, t1 ),( v2d, s2 ),( v2d, t2 ),( v1d, v2d ) ), dict ) = i
                self.insert_wall_vertex( v1d, p1, (self._id2mass[ s1 ].v + self._id2mass[ t1 ].v)/2 )
                self.insert_wall_vertex( v2d, p2, (self._id2mass[ s2 ].v + self._id2mass[ t2 ].v)/2 )
                spr1 = self.id2spring( ( s1, t1 ) )
                k1 = mag(self._id2mass[ s1 ].pos - p1)/mag(self._id2mass[ s1 ].pos - self._id2mass[ t1 ].pos )
                self.insert_wall( ( v1d, s1 ), k1*spr1.l0, Color.spring )
                self.tissue.wv_edge_property( wv_edge=self.tissue.wv_edge_id( (v1d,s1) ), property="old_wall_successor",value=True) 
                self.insert_wall( ( v1d, t1 ), (1-k1)*spr1.l0, Color.spring )
                self.tissue.wv_edge_property( wv_edge=self.tissue.wv_edge_id( (v1d,t1) ), property="old_wall_successor",value=True) 
                spr2 = self.id2spring( ( s2, t2 ) )
                k2 = mag(self._id2mass[ s2 ].pos - p2)/mag(self._id2mass[ s2 ].pos - self._id2mass[ t2 ].pos )
                self.insert_wall( ( v2d, s2 ), k2*spr2.l0, Color.spring )
                self.tissue.wv_edge_property( wv_edge=self.tissue.wv_edge_id( (v2d,s2) ), property="old_wall_successor",value=True) 
                self.insert_wall( ( v2d, t2 ), (1-k2)*spr2.l0, Color.spring )
                self.tissue.wv_edge_property( wv_edge=self.tissue.wv_edge_id( (v2d,t2) ), property="old_wall_successor",value=True) 
                self.insert_wall( ( v1d, v2d ), mag(p1-p2)*self.const.dividing_cell_walls_shrinking_factor, Color.added_spring, True )
                #if the vertex is created in fixed region it should be also fixed
                if self._id2mass[ s1 ].fixed and self._id2mass[ t1 ].fixed: self._id2mass[ v1d ].set_fixed( True )
                if self._id2mass[ s2 ].fixed and self._id2mass[ t2 ].fixed: self._id2mass[ v2d ].set_fixed( True )
                self.remove_wall( ( s1, t1 ) )
                self.remove_wall( ( s2, t2 ) )
                self.visualisation.remove_vcell( dict[ "removed_cell" ] )
                self.visualisation.remove_vmt( dict[ "removed_cell" ] )
                self.visualisation.add_vcell( dict[ "added_cell1" ] )
                self.visualisation.add_vmt( dict[ "added_cell1" ] )
                self.visualisation.add_vcell( dict[ "added_cell2" ] )
                self.visualisation.add_vmt( dict[ "added_cell2" ] )

    def remove_wall( self, wv_edge, leave_visible=False ):
        """Removes wall identified by w from simulation.
        """
        w = self.tissue.wv_edge_id( wv_edge )
        spr = self.id2spring( w )
        self._id2spring.pop( w )
        self._spring2id.pop( spr )
        self.remove_spring( spr, leave_visible=leave_visible )

    def remove_wv( self, wv, leave_visible=False ):
        """Removes wv identified by wv from simulation.
        """
        m = self._id2mass[ wv ]
        self._id2mass.pop( wv )
        self._mass2id.pop( m )
        self.remove_mass( m, leave_visible=leave_visible )


    def update_tissue( self ):
        self.tissue.time = self.time
        for m in self.masses:
            self.tissue.wv_pos( self._mass2id[ m ], m.pos ) 
    
    def pickle_fixed( self ):
        id2fixed = {}
        for m in self._mass2id:
            id2fixed[ self._mass2id[ m ] ] = m.fixed
        pickle.dump(id2fixed, open(self.file_name+'.pickled_fixed', 'w'))

    def un_pickle_fixed( self ):
        id2fixed = pickle.load(open(self.file_name+'.pickled_fixed'))
        print "Unpicklickling fixed ok.."
        for m in self._mass2id:
            m.fixed = id2fixed[ self._mass2id[ m ] ]
            self.visualisation.set_vmass_fixed( mass=m, fixed=m.fixed )