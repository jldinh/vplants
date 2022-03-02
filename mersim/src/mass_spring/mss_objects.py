#!/usr/bin/env python
"""Contains basic mass-spring system components: Mass&Spring.

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
__revision__="$Id: mss_objects.py 7875 2010-02-08 18:24:36Z cokelaer $"



import visual

#import PlantGL as pgl 
import openalea.plantgl.all as pgl
import tools

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
