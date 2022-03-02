from PlantGL import * 
from math import *
from random import *

nbr_of_sph = 1000
speed = 100.
sph = []
k = {}
sphere = Sphere(radius=0.5,slices=4,stacks=4)
s = Scene()
x = 0

for i in range( nbr_of_sph ):
    t = Shape( Translated( Vector3(0, 0 , i), sphere), Material(), i )
    sph.append( t )
    s += t
    k[ t ] = random()

v = Viewer()
v.animation(True)
v.add( s )

def update():
    global x
    x += 1/speed
    for s in sph:
       tr = s.geometry.translation
       tr.y = 100*sin( x*k[ s ] )
       s.geometry.translation = tr

running = True
while running:
    sel = v.selection()
    if sel:
        print sel
    update()
    v.update()
    if sel:
        v.setSelection( sel )
    running = not v.wait(40)
