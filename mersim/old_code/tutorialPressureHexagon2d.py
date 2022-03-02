from springTissueModel import *
from const import *
import visual

class PressureHexagonsSystem( TissueSystem ):
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


s = PressureHexagonsSystem( "/home/stymek/mdata/pressureHexagons2d/pressureHexagons2d.dat", PressureHexagonsConst() )
#s = PressureHexagonsSystem( "/home/stymek/mdata/pressureHexagons2d/pressureHexagons2d.dat", GrowthHexagonsConst() )

s.mainloop()
