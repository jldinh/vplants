import openalea.container
from openalea.deploy.shared_data import shared_data
data_filepath = shared_data(openalea.container, 'p58-t1_imgSeg_cleaned.inr.gz')

from openalea.image.serial.basics import imread
t1 = imread(data_filepath)

from openalea.image.spatial_image import SpatialImage
im = SpatialImage(t1[:,:,115])

from openalea.image.algo.analysis import SpatialImageAnalysis
analysis = SpatialImageAnalysis(im)
analysis.remove_margins_cells( verbose = True )

from openalea.image.algo.graph_from_image import graph_from_image
# -- If you want to get rid of the margin cells for your graph analysis:
graph = graph_from_image( analysis.image )

import matplotlib.pyplot as plt
plt.figure(figsize=(7,5))
plt.hist(graph.edge_property('wall_surface').values(), bins=40, normed=False)
plt.title("Distribution function of cell contact surfaces for p58", fontsize=16)
plt.xlabel('Contact surfaces'+ r' ($\mu m^2$)',fontsize=12)
plt.ylabel('Frequency',fontsize=12)
plt.legend(loc=1)
plt.show()
