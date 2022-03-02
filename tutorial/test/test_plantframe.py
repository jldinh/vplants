import vplants.tutorial
from openalea.deploy.shared_data import shared_data
import openalea.mtg
from openalea.mtg import *

data = shared_data(openalea.mtg)
g = MTG(data/'noylum2.mtg')
drf = data/'walnut.drf'
dressing_data = dresser.dressing_data_from_file(drf)
pf = plantframe.PlantFrame(g, 
                           TopDiameter='TopDia',
                           DressingData = dressing_data)
pf.run()
diams = pf.compute_diameter()
pf.plot(gc=True)
pf.plot_property('diameter')





data = shared_data(vplants.tutorial)/'PlantFrame'

g = MTG(data/'monopodial_plant.mtg')

# Compute the PlantFrame

pf = plantframe.PlantFrame(g, 
                           TopDiameter='diam')
pf.run()
g.properties()['diameter'] = diameters

# Extract the sequences
diam = g.property('diam')
for order in pf.axes:
    for seq in pf.axes[order]:
        print seq
        print range(len(seq))
        print [diam.get(v) for v in seq]
        print '===='



