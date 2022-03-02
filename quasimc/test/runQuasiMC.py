from vplants.quasimc.quasimc import QuasiMC

from openalea.plantgl.all import *

import numpy as np

#qmc_withfiles = QuasiMC(inputfile="quasimc.in",optfile="quasimc.cfg",envirofile="enviro.e")


qmc = QuasiMC()

scene=Scene()
#scene += Shape(TriangleSet([(1,0,0),(-1,0,0),(0,1,0)],[(0,1,2)]))
scene += Shape(Sphere(1.0))
tessel = Tesselator()
for shape in scene:
    qmc.add_shape(shape,tessel)
      
# light source format: weight,x_dir,y_dir,z_dir, with +z on zenith
lights = [(1.0,0.0,0.0,-1.0)]
qmc.add_light_sources(lights)

qmc.run()

print qmc.get_flux_density()

print qmc.get_sunlit_leaf_area()

