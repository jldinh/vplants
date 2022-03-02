from openalea.aml import *

mtg = MTG("agraf.mtg")
dr1 = DressingData("agraf.drf")
f1 = PlantFrame(0, Scale = 3, DressingData = dr1)
Plot(f1)