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

#------------------------------------------------------------------------------- Force
class _Force:
    """Force interface. Force is an object which acts on other objects in the system
    (the most important are *points*). Each force in the system is aplied in each timestep
    to influance the object. This is done using _Force.apply() method.
    """
    def __init__(self, system):
        """It is used to initialize force object.

        :param system: System class instance to be able to access different system objects.
        :type system: System
        :note: Abstract. Don't use.
        """
        self.system = system
        """#:Use to access System instance."""
        pass

    def apply(self):
        """It is used to apply the force in each timestep. 
        
        :note: Should be optimal, because it is called frequently.
        :note: Abstract. Don't use.
        """
        print "_Force::apply() -- abstract method"


#------------------------------------------------------------------------------- Forces
class SpringForce (_Force):
    """Spring force implementation.

    :todo: Add real computations here..
    """

    def __init__(self, system):
        """SpringForce constructor.

        :param system: reference to System object
        :type system: System
        """
        _Force.__init__( self, system )
        self.springs = []
        """Springs are kept in the list, to be fast-accessible."""

    def apply(self):
        """For each spring in self.springs we calculate spring force acting
        on 2 points connected with the spring. If dumping of the spring is
        *ON* we take it in account. 
        """
        return 
        for spring in self.springs:
            spring.calc_spring_force()
            if spring.damping:
                spring.calc_damping_force()




class CellPressureForce (_Force):
    """Cell pressure in 2d force implementation. Cell pressure works in 2d. It finds the center of the cell and
    pushes all walls with *equal* force perpendicular to the wall.
    """
    
    def __init__(self, system, tissue, pressure_const = 1.):
        """CellPressureForce constructor.

        :param system: reference to System object
        :param pressure_const: pressure constant
        :param init_pressure: pressure is set initially in each cell to this value 
        :param tissue: link to WalledTissue
        :type system: System
        :type pressure_const: Float
        :type init_pressure: Float
        :type tissue: WalledTissue
        """
        _Force.__init__( self, system )
        self.pressure_const = {} 
        self.tissue = tissue
        self.init_pressure_const = pressure_const

    def apply(self):
        """Applies the cell pressure  force. Cell pressure force acts on each point in the System,
        except the *fixed* points.
        """
        cell2baricenter = self.tissue.cell_centers()
        for c in self.tissue.cells():
            shape = self.tissue.cell2wvs( c )            
            surface = self.tissue.calculate_cell_surface( c )
            baricenter = cell2baricenter[ c ]
            if not self.pressure_const.has_key( c ):
                self.pressure_const[ c ] = self.init_pressure_const
            pressure_const = self.pressure_const[ c ]


            for i in range( len( shape ) ):
                m0_id = shape[ i ]
                m1_id = shape[ (i+1)%len( shape ) ]
                m0 = self.system._id2mass[ m0_id ]
                m1 = self.system._id2mass[ m1_id ]
                force = pressure_const/surface
                normal = visual.rotate( m0.pos - m1.pos, visual.pi/2)
                if visual.mag( (m0.pos+normal)  - baricenter ) > visual.mag( (m0.pos-normal) -  baricenter ):
                    m0.F += norm( normal ) * force
                    m1.F += norm( normal ) * force
                else:
                    m0.F += norm( -normal ) * force
                    m1.F += norm( -normal ) * force
                    
        

class GravityForce (_Force):
    """Gravity force implementation.
    """
    
    def __init__(self, system, gravity):
        """GravityForce constructor.

        :param system: reference to System object
        :param gravity: gravity constant
        :type system: System
        :type gravity: Float
        """
        _Force.__init__( self, system )
        self.gravity = gravity

    def apply(self):
        """Applies the gravity force. Gravity force acts on each point in the System,
        except the *fixed* points.
        """
        for mass in self.system.masses:
            if not mass.fixed: mass.calc_gravity_force(self.gravity)


class UniformUpForce (_Force):
    """UniformUpForce implementation. This force acts oposite to the gravity force,
    but doesn't take an account on *mass* of the points. It prevents collapsing effect.
    """
    
    def __init__(self, system, uniform_up):
        """UniformUpForce constructor.

        :param system: reference to System object
        :param uniform_up: uniform_up constant
        :type system: System
        :type uniform_up: Float
        """
        _Force.__init__( self, system )
        self.uniform_up = uniform_up

    def apply(self):
        """Applies the uniform up force. The force doesn't apply on fixed points.
        """
        for mass in self.system.masses:
            if not mass.fixed: mass.calcuniform_up_force(self.uniform_up)


class ViscoForce (_Force):
    """Viscosity force implementation. This force acts as a fraction of the environment.
    """

    def __init__(self, system, visco):
        """ViscosityForce constructor.

        :param system: reference to System object
        :param visco: visco constant
        :type system: System
        :type visco: Float
        """
        _Force.__init__( self, system )
        self.visco = visco 

    def apply(self):
        """Applies to each point except *fixed* ones.
        """
        for mass in self.system.masses:
            if not mass.fixed: mass.calc_viscosity_force(self.visco)


class SimplePressureForce (_Force):
    """Simple pressure force implementation. The simple pressure works by finding the normals to the
    cell wvs and adding the force in the direction of normals. The "arrow direction" is selected according to
    the structure initialisation (L or R) and is kept constant in all the model.
    """
    
    def __init__(self, system, pressure = 1.):
        """SimplePressureForce constructor.

        :param system: reference to System object
        :param pressure: pressure constant
        :type system: System
        :type pressure: Float
        """
        _Force.__init__( self, system )
        self.pressure = pressure
        self.wv2normal={}
        self.normals_update_time = 0
        
    def get_wv2normals( self ):
        if self.system.time != self.normals_update_time:
            self.normals_update_time = self.system.time
            self.create_normals()
        return self.wv2normal
    
    def create_normals( self ):
        self.wv2normal={}
        t = self.system.tissue
        for c in t.cells():   
            wvs = t.cell2wvs( cell = c )
            lwvs = len( wvs )
            for i in range( lwvs ):
                x   = t.wv_pos( wvs[ i ] )
                xp = t.wv_pos( wvs[ (i+1)%lwvs ] )
                px = t.wv_pos( wvs[ i-1 ] )
                if self.wv2normal.has_key( wvs[ i ] ):
                    self.wv2normal[ wvs[ i ] ] += visual.cross( x-px, xp-x)
                else:
                        self.wv2normal[ wvs[ i ] ] = visual.cross( x-px, xp-x)
        for v in self.wv2normal:
            self.wv2normal[ v ] = self.wv2normal[ v ].norm()
            
            
            
    def apply(self):
        """Applies the pressure  force. Simple pressure force acts on each point in the System,
        except the *fixed* points.
        """
        normals = self.get_wv2normals() 
        for i in self.system.masses:
            i.F += normals[ self.system._mass2id[ i ] ]* self.pressure

class SimplePressureForceUnderPrimordium (_Force):
    """Simple pressure force implementation. The simple pressure works by finding the normals to the
    cell wvs and adding the force in the direction of normals. The "arrow direction" is selected according to
    the structure initialisation (L or R) and is kept constant in all the model.
    """
    
    def __init__(self, system, pressure = 1.):
        """SimplePressureForce constructor.

        :param system: reference to System object
        :param pressure: pressure constant
        :type system: System
        :type pressure: Float
        """
        _Force.__init__( self, system )
        self.pressure = pressure

    def apply(self):
        """Applies the pressure  force. Simple pressure force acts on each point in the System,
        except the *fixed* points.
        """
        normals = self.system.forces["simple_pressure_force"].get_wv2normals()
        pl = []
        for i in self.system.tissue.cells():
            if self.system.tissue.cell_property(cell=i, property="PrC") > 0:
                pl.append( i )
        vw = []
        for i in pl:
            for j in self.system.tissue.cell_neighbors( i ):
                cs = self.system.tissue.cell2wvs( j )
                for k in cs:
                    vw.append(k)
        vw = dict(map(lambda a: (a,1), vw)).keys()
            
        for i in vw:
            self.system._id2mass[ i ].F += normals[ i ]* self.pressure

class RadialMoveForce( _Force ):
    def __init__(self, system, center = visual.vector()):
        """SimplePressureForce constructor.

        :param system: reference to System object
        :param pressure: center of the simulation
        :type system: System
        :type pressure: Float
        """
        _Force.__init__( self, system )
        self.center = center
        self.c_czone = 1
        self.c_v0 = 0.01
    
    def apply( self ):
        for m in self.system.masses:
            m.F += (-self.center + m.pos )*self.c_v0/self.c_czone


class SphereMoveForce( _Force ):
    def __init__(self, system, center = visual.vector()):
        """SimplePressureForce constructor.

        :param system: reference to System object
        :param pressure: center of the simulation
        :type system: System
        :type pressure: Float
        """
        _Force.__init__( self, system )
        self.center = center
        self.c_czone = 1
        self.c_v0 = 0.0001
        self.r = 100
    
    def apply( self ):
        for m in self.system.masses:
            # cal spherical coords
            sig = math.sqrt( m.pos.x^2 + m.pos.y^2 + m.pos.z^2 )
            fi = math.acos( m.pos.x / sig )
            theta = math.atan2( m.pos.y, m.pos.x )
            # update spherical coords
            theta += theta - 0.01
            # update cartesian coords
            m.pos.x = sig * math.sin( fi ) * math.cos( theta )
            m.pos.y = sig * math.sin( fi ) * math.sin( theta )
            m.pos.z = sig * math.cos( fi )
            
           # m.F += (-self.center + m.pos )*self.c_v0/self.c_czone

#------------------------------------------------------------------------------- Mass
class Mass:
    """Physical model and visual representation of a mass.
    """

    def __init__(self, m, pos, r=0.3, fixed=False, pickable=True, v=visual.vector(0., 0., 0.), color=Color.normal_point,  system=None, **keywords):
        """Construct a mass.

        :param m: Mass of the point.        print "for@!"

        :param pos: Position of the point.
        :param fixed: True for *fixed* points. If point is fixed, it is uneffected by certain forces.
        :param v: Velocity of the point

        :param color: (V)Color of the point.
        :param r: (V)Radius of the *visualized* point.
        :param pickable: (V)True if mass point can be 'drag and drop'.

        :type m: Float
        :type pos: visual.vector
        :type r: Float 
        :type fixed: True|False 
        :type pickable: True|False 
        :type v: visual.vector 
        :type color: Const.Color.X 

        :note: Params marked with (V) are important only for *visualisation*.
        """

        self.m = float(m)
        self.fixed = fixed
        #self.auxin = 0
        self.v = visual.vector(v)
        self.F = visual.vector(0., 0., 0.)
        self.springs = []
        self.pos = pos 
        self._in_simulation = True  # True iff point is in simulation
        self.in_simulation = property( fget= self._get_in_simulation, fset=self._set_in_simulation, doc="True iff point is in simulation" )



        if system.const.visualisation:
            system.visualisation.add_vmass( self )

    def set_fixed( self, fixed = True):
        # TODO play with visualisation
        if fixed:
            self.fixed = True
        else:
            self.fixed = False
    
    def _set_in_simulation( self, state ):
        """For setting a property
        """
        self._in_simulation = state 

    def _get_in_simulation( self ):
        """For getting a property
        """
        return self._in_simulation  

    def connect( self, spring ):
        """Connects mass with a spring.
        """
        if spring not in self.springs:
            self.springs.append( spring )

    def disconnect( self, spring ):
        """Disconnects mass with a spring.
        """
        self.springs.remove( spring )
    

    def calcuniform_up_force(self, c):
        """Calculate the uniform force acting up with the coeficient c.
        The force *doesn't* depand on mass (like gravity).
        """
        #self.F += visual.vector(0,  0, c)
        self.F.z += c 

    def calc_gravity_force(self, g):
        """Calculate the gravity force.
        """
        #self.F -= visual.vector(0, 0, self.m * g)
        self.F.z -= self.m * g

    def calc_viscosity_force(self, viscosity):
        """Calculate the viscosity force.
        """
        # Fviscosity = - v * viscosity_factor
        self.F -= self.v * viscosity

    def calc_new_location(self, dt):
        """Calculate the new location of the mass using Euler solver.
        
        :return: velocity of mass point
        :rtype: velocity vector
        """
        # very basic idea -- Euler: switching to ODE solver may be needed.
        # F = m * a = m * dv / dt  =>  dv = F * dt / m
        dv = self.F * dt / self.m
        self.v += dv
        # v = dx / dt  =>  dx = v * dt
        self.pos += self.v * dt
        return self.F

    def clear_force(self):
        """Clear the Force.
        """
        #self.F = visual.vector(0., 0., 0.)
        self.F.x = 0.
        self.F.y = 0.
        self.F.z = 0.



#-------------------------------------------------------------------------------Spring
class Spring:
    """Physical model of a spring.
    """


    def __init__(self, m0, m1, k, l0=None, damping=None, color=Color.spring, system=None, **keywords):
        """Construct a spring.
        """
        self.m0 = m0
        self.m1 = m1
        self.k = k
        if l0:
            self.l0 = l0
        else:
            self.l0 = visual.mag(self.m1.pos - self.m0.pos)
        self.damping = damping
        self.e = visual.vector(0., 0., 0.)

        if system.const.visualisation:
            system.visualisation.add_vspring( self )


    def calc_spring_force(self):
        """Calculate the spring force.
        """
        delta = self.m1.pos - self.m0.pos
        l = visual.mag( delta )
        self.e = visual.norm( delta )
        # Fspring = (l - l0) * k
        Fspring = (l - self.l0) * self.e * self.k
        #print l, self.k, self.e, Fspring
        self.m0.F += Fspring
        self.m1.F -= Fspring


    def calc_damping_force(self):
        """Calculate the damping force.
        """
        # Fdamping = v in e * damping_factor
        Fdamping = visual.dot((self.m1.v - self.m0.v), self.e) * self.damping * self.e
        self.m0.F += Fdamping
        self.m1.F -= Fdamping

    def multiply_l(self, m):
        self.l0 *= m

    def spring_growth( self, factor ):
        self.l0 += math.fabs( self.l0*factor )

    def spring_growth_if_under_tension( self, factor=0.001 ):
        """Increase the l0 of spring but only if the spring is under tension
        """
        delta = self.m1.pos - self.m0.pos
        l = visual.mag( delta )
        diff = l - self.l0
        if diff > 0:
            self.l0 += factor*diff
            if  l - self.l0 < 0:
                self.l0 = l
        

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
