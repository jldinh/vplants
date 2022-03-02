from springTissueModel import *
from const import *
import visual

class ShapeSystem( System ):
    def __init__(self, const):
        """String simulation using the mass-spring system.
        """
        viscosity = Const.max_system_viscosity
        System.__init__(self, const = const)
        
        self._fixed_border = 0. #: all points which z is lower than this value will be threat as fixed
        self._dropped_border = 0. #: all points which z is lower than this value will be dropped from simulation

        
        self.turn_on = True
        display.lights = [visual.vector(-0.2,  0.5,  0.5), visual.vector(-0.2,  0.5, -0.3), visual.vector( 0.2, -0.5,  0.3)]
        self.display.autoscale = 0
        self.display.autocenter = 1
        self.display.autocenter = 0
        self.display.up = visual.vector(0, 0.001, 1)
        #self.display.ambient= 0.6
        #self.create_controls()
        self.create_shape()
        self.run = True
        self.mainloop()

    def create_shape( self ):
        P = []
        P.append( visual.vector(0, 2, 0 ) )
        P.append( visual.vector(0, 4, 0 ) )
        P.append( visual.vector(2, 6, 0 ) )
        P.append( visual.vector(4, 6, 0 ) )
        P.append( visual.vector(6, 4, 0 ) )
        P.append( visual.vector(6, 2, 0 ) )
        P.append( visual.vector(4, 0, 0 ) )
        P.append( visual.vector(2, 0, 0 ) )
        M = []
        for v in P:
            m = Mass( m = 1., pos = v, fixed = 0 )
            M.append( m )
            self.insert_mass( m )
        
        for i in range( len( self.masses ) ):
            self.insert_spring( CylinderSpring( self.masses[ i ], self.masses[ (i+1)%len( self.masses ) ], k = 0.5, damping = True ) )

        for i in range( 1,len( self.masses )+1 ):
            self.insert_spring( CylinderSpring( self.masses[ i-1 ], self.masses[ (i+1)%len( self.masses ) ], k = 0.5, damping = True ) )

        #M[2].set_fixed( 1 )
        M[0].set_fixed( 1 )
        M[5].sphere.pos = visual.vector(0, 5, 0 ) 


s = ShapeSystem( ShapeConst() )
