#!/usr/bin/env python
"""Basic forces implementation. 

:note:
Previousle forces were closly related to TissueSystem.

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
__revision__="$Id: forces.py 7875 2010-02-08 18:24:36Z cokelaer $"


import visual
import math



import openalea.plantgl.all as pgl
import openalea.mersim.const.const as const 
import openalea.mersim.tools.misc as tools

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
    def __init__(self, system, center = visual.vector(), c_v0=0.01, c_zone=1):
        """SimplePressureForce constructor.

        :param system: reference to System object
        :param pressure: center of the simulation
        :type system: System
        :type pressure: Float
        """
        _Force.__init__( self, system )
        self.center = center
        self.c_czone = c_zone
        self.c_v0 = c_v0
    
    def apply( self ):
        for m in self.system.masses:
            m.F += (-self.center + m.pos )*self.c_v0/self.c_czone


class SphereMoveForce( _Force ):
    def __init__(self, system, center = visual.vector(), c_v0=0.0001, c_czone=1, c_r=100):
        """SimplePressureForce constructor.

        :param system: reference to System object
        :param pressure: center of the simulation
        :type system: System
        :type pressure: Float
        """
        _Force.__init__( self, system )
        self.center = center
        self.c_czone = 1
        self.c_v0 = c_v0
        self.r = c_r
    
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

