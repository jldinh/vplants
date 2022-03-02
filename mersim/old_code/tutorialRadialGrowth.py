#!/usr/bin/env python
"""tutorialRadialGrowth.py

Desc.

:version: 2006-05-15 15:21:06CEST
:author:  szymon stoma
"""

from springTissueModel import *
from const import *
import visual

s = TissueSystem( const =   RadialGrowth() ) #aux smallPressureAllMeristemGrowthWallShrink() )
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
s.phys["auxin_transport_model" ].apply()

###s.visualisation.update()
###s.visualisation.display.forward=visual.vector(1,0,0)
###s.visualisation.display.up=visual.vector(0,0,1)
###s.visualisation.rotate(grab_scene=True, angle=3.1415/2, rotation=visual.vector(0,1,0),steps=15)
s.tissue._tissue_properties[ "primordiums" ] = {}
s.mainloop()
