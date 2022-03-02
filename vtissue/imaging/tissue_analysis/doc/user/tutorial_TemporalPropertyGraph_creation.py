import openalea.container
from openalea.deploy.shared_data import shared_data
#~ data_files = shared_data(openalea.container, pattern='*.inr.gz') # return a list

# -- We load the images corresponding to the different time points
from openalea.image.serial.basics import imread
t1 = imread(shared_data(openalea.container, 'p58-t1_imgSeg_cleaned.inr.gz'))
t2 = imread(shared_data(openalea.container, 'p58-t2_imgSeg_cleaned.inr.gz'))
t3 = imread(shared_data(openalea.container, 'p58-t3_imgSeg_cleaned.inr.gz'))

# -- We create the corresponding SpatialImageAnalysis objets
from openalea.image.algo.analysis import SpatialImageAnalysis, DICT
analysis1 = SpatialImageAnalysis(t1, ignoredlabels = [0,1], return_type = DICT)
analysis2 = SpatialImageAnalysis(t2, ignoredlabels = [0,1], return_type = DICT)
analysis3 = SpatialImageAnalysis(t3, ignoredlabels = [0,1], return_type = DICT)

# -- We don't want to compute values (in `graph_from_image()`) for cells at the margins of the stack.
analysis1.add2ignoredlabels( analysis1.cells_in_image_margins() )
analysis2.add2ignoredlabels( analysis2.cells_in_image_margins() )
analysis3.add2ignoredlabels( analysis3.cells_in_image_margins() )

# -- We now create the PropertyGraphs:
# - Note:
#    - labels added to the 'ignoredlabels' list are automatically excluded from list creation.
#    - you can specify a list of labels to work with for each graph to create.
from openalea.image.algo.graph_from_image import graph_from_image
graph_1 = graph_from_image( analysis1 )
graph_2 = graph_from_image( analysis2 )
graph_3 = graph_from_image( analysis3 )
# - The PropertyGraphs will contains these properties by default:
#~ default_properties2D = ['barycenter','boundingbox','border','L1','epidermis_surface','inertia_axis']
#~ default_properties3D = ['volume','barycenter','boundingbox','border','L1','epidermis_surface','wall_surface','inertia_axis']

# -- Now you need the lineage information:
from vplants.mars_alt.alt.mapping import lineage_from_file

lin_12=lineage_from_file(shared_data(openalea.container, 'suiviExpertEntier58-12.txt'))
l12=lin_12
lin_23=lineage_from_file(shared_data(openalea.container, 'suiviExpertEntier58-23.txt'))
l23=lin_23

# --Finally you can create a TemporalPropertyGraph by temporaly linking PropertyGraph:
from openalea.container import TemporalPropertyGraph
g = TemporalPropertyGraph()
g.extend([graph_1,graph_2,graph_3],[l12,l23], [0,24,48])

# -- If you want to save this TemporalPropertyGraph:
import pickle
import gzip
f = gzip.open('p58_TemporalPropertyGraphs.pklz','w')
pickle.dump( g, f)
f.close()

