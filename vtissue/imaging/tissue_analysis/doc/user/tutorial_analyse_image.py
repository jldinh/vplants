import openalea.container
from openalea.deploy.shared_data import shared_data
data_filepath = shared_data(openalea.container, 'p58-t1_imgSeg_cleaned.inr.gz')
data_files = shared_data(openalea.container, pattern='*.inr.gz') # return a list

from openalea.image.serial.basics import imread
t1 = imread(data_filepath)

from openalea.image.all import display
display( t1 )

from openalea.image.all import SpatialImage
im = SpatialImage(t1[:,:,115])

from openalea.image.algo.analysis import SpatialImageAnalysis
analysis = SpatialImageAnalysis(im)

from openalea.image.all import display
display( im )

analysis.remove_margins_cells( verbose = True )

from openalea.image.all import display
display( analysis.image )

analysis.inertia_axis( self, labels = None, center_of_mass = None, real = True )
analysis.center_of_mass( self, labels = None, real = True )
analysis.neighbors( self, labels = None  )
analysis.L1( self, background = 1)


from openalea.image.algo.graph_from_image import graph_from_image
# ~ graph_from_image(image, labels = None, background = 1, default_properties = default_properties, default_real_property = True, bbox_as_real = False)

# -- If you want every cells for your graph analysis:
graph = graph_from_image( im )
# -- If you want to get rid of the margin cells for your graph analysis:
graph = graph_from_image( analysis.image )
# -- or:
graph = graph_from_image( im, set(analysis.labels())-set(analysis.border_cells()) )
# -- If you want to keep only cells belonging to the first layer for your graph analysis:
graph = graph_from_image( im, analysis.L1() )

list( graph.vertex_property_names() )
#~ ['label',
 #~ 'volume',
 #~ 'barycenter',
 #~ 'inertia_axis',
 #~ 'L1',
 #~ 'boundingbox',
 #~ 'epidermis_surface',
 #~ 'border']


graph.vertex_property('volume')[8]
#~ 287.0

graph.vertex_property('volume')
#~ {4: 624.0,
 #~ 5: 946.0,
 #~ 8: 287.0,
 #~ 34: 642.0,
 #~ 40: 331.0,
 #~ 43: 179.0,
 #~ ...


list( graph.vertices() )

list( graph.edge_property_names() )
#~ ['wall_surface']

graph.edge_property('wall_surface')
#~ {0: 4.0,
 #~ 1: 25.0,
 #~ 2: 15.0,
 #~ 3: 26.0,
 #~ 4: 19.0,
 #~ ...

import matplotlib.pyplot as plt
fig = plt.figure()
plt.hist(graph.vertex_property('volume').values(), bins=20, normed=False)
plt.title("Distribution function of L1 cell volumes for p58", fontsize=22)
plt.xlabel('Volumes'+ r' ($\mu m^3$)',fontsize=18)
plt.ylabel('Frequency',fontsize=18)
plt.legend(loc=1)
plt.show()


from openalea.image.algo.graph_from_image import ( add_vertex_property_from_label_and_value,
                                                 add_vertex_property_from_label_property,
                                                 add_vertex_property_from_dictionary,
                                                 add_edge_property_from_label_and_value,
                                                 add_edge_property_from_label_property )

graph.neighbors(5)
#~ set([4, 65, 158, 390, 501, 857, 884, 985, 998])

graph.edges(5)
#~ set([5, 6, 7, 8, 9, 10, 11, 12, 13])

graph.neighborhood(5,1)
#~ set([4, 5, 65, 158, 390, 501, 857, 884, 985, 998])

graph.neighborhood(5,2)
#~ set([4, 5, 63, 65, 142, 158, 190, 244, 298, 337, 373, 390, 500, 501, 723, 759, 857, 884, 901, 912, 985, 990, 998])
# -- Note that if you ask for a rank >= 2, lower ranks neighbors will be returned too !!!


