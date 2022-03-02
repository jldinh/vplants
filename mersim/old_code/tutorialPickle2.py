import visual
import cPickle as pickle
from cStringIO import StringIO

class A:
    def __init__(self):
        self._a = []
        
    def add( self, n ):
        self._a.append( n )


src = open("test.pickle3","w")
p = pickle.Pickler(src)
def persistent_id(obj):
    if isinstance( obj, visual.vector):
        return str( obj.x )+" "+str( obj.y )+" "+str( obj.z )
    else:
        return None
p.persistent_id = persistent_id 

def persistent_load(persid):
        return visual.vector(float( persid.split()[0] ), float( persid.split()[1] ), float( persid.split()[2] ))

   
v=visual.vector(1,2,3)
a = A()
a.add( v )
p.dump( a )
src.close()
# END of pickling


src = open("test.pickle3","r")
up = pickle.Unpickler(src)
up.persistent_load = persistent_load
b = up.load( )

print b._a