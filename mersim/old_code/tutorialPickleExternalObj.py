import cPickle as pickle
import copy_reg as cr
import visual

class A:
    def __init__(self):
        self._a = []
        
    def add( self, n ):
        self._a.append( n )

def f( a ):
    return (visual.vector, ( a.x,a.y,a.z ) )


av  = A()
av.add( visual.vector() )
av.add( [1,2] )

cr.pickle(visual.vector, f)

pickle.dump( av, open("test2.pickle", "w") )
bv = pickle.load( open("test2.pickle", "r") )
print bv._a