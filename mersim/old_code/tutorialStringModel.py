#!/usr/bin/env python

"""tutorialString.py

Contains experiment with string on gravity behaviour. 


:version: 2006-07-28 12:01:15CEST
:author: szymon stoma
"""

from springTissueModel import *
from const import *
import visual

class StringSystem( System ):
    def __init__(self):
        """String simulation using the mass-spring system.
        """
        viscosity = Const.max_system_viscosity
        System.__init__(self, timestep=1./10, 
            gravity=1.,
            viscosity= 0 , #0.6
            uniform_up = 0, #2,
            width=800,
            height=600,
            fov=visual.pi/3.,
            background= (Color.background[0]*viscosity,Color.background[1]*viscosity,Color.background[2]*viscosity),
            name = "StringModel v0.1"
        )
        
        #self._fixed_border = 0. #: all points which z is lower than this value will be threat as fixed
        #self._dropped_border = 0. #: all points which z is lower than this value will be dropped from simulation

        
        self.turn_on = True
        display.lights = [visual.vector(-0.2,  0.5,  0.5), visual.vector(-0.2,  0.5, -0.3), visual.vector( 0.2, -0.5,  0.3)]
        self.display.autoscale = 0
        self.display.autocenter = 1
        self.display.autocenter = 0
        self.display.up = visual.vector(0, 0.001, 1)
        #self.display.ambient= 0.6
        #self.create_controls()
        self.create_string()
        self.run = True
        self.mainloop()

    def create_string( self ):
        P = []
        for i in range( 10 ):
            P.append( visual.vector(0, 0, -i ) )

        for v in P:
            self.insert_mass( Mass( m = 1., pos = v, fixed = 0 ) )
        
        self.masses[ 0 ].set_fixed( True )
        for i in range( len( self.masses )-1 ):
            j = ((len( self.masses )-1) - i)/float(len( self.masses )-1)
            print j
            self.insert_spring( CylinderSpring( self.masses[ i ], self.masses[ i+1 ], k = j, damping = True ) )

s = StringSystem()

