#!/usr/bin/env python
"""tutorialCanalisationModel.py

Desc.

:version: pon lut 19 16:13:00 CET 2007

:author:  szymon stoma
"""

from springTissueModel import *
from const import *
import visual

##
#import tools
#import numpy
#import random
#x=[]
#y=[]
#z=[]
#for i in range(1000):
#    xr=random.random()
#    yr=random.random()
#    zr = sin(xr)+cos(yr)
#    x.append(xr)
#    y.append(yr)
#    z.append(zr)
#X,Y,Z=tools.create_grid_from_discret_values(x,y,z, sizeX=100, sizeY=100)
#tools.test( X, Y, Z )
#raw_input()
##

const = RadialGrowthCanalisationHypo()
s = TissueSystem( const = const  ) #aux smallPressureAllMeristemGrowthWallShrink() )
#s.const=const
v = visual.vector()
for i in s.masses:
    v += i.pos
    i.fixed=False
v = v/ len(s.masses )
s.forces["radial_move"].center=v
s.tissue.tissue_center_=v
visual.sphere(pos=visual.vector(v.x,v.y,30), radius=3)
for i in s.tissue.wvs():
    s.tissue.wv_property(wv=i, property="PrC", value=-1)
#for i in s.tissue.cell_edges():
#    s.tissue.cell_edge_property(cell_edge=i, property="pin_level", value=[1,1])
#s.phys["auxin_transport_model"].init_aux()
#s.phys["auxin_transport_model" ].apply()

###s.visualisation.update()
###s.visualisation.display.forward=visual.vector(1,0,0)
###s.visualisation.display.up=visual.vector(0,0,1)
s.visualisation.init_after_meristem_creation()
###s.visualisation.rotate(grab_scene=True, angle=3.1415/2, rotation=visual.vector(0,1,0),steps=15)
s.tissue._tissue_properties[ "primordiums" ] = {}
s.tissue.const=const
s.mainloop()
#s.frame_nbr=16
#s.play_simulation()
