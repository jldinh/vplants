#!/usr/bin/env python
"""filename.py

Desc.

:version: 2006-05-15 15:21:06CEST
:author:  szymon stoma
"""


from springTissueModel import *
from const import *
import PlantGL as pgl
import merrysim as m
import visual

const = PlantGLTissueTest()
s = TissueSystem( const = const  )
s.tissue._create_TissueTopologyFromSimulation()
