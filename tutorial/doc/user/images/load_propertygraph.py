#~ import numpy as np
#~ from scipy import ndimage
#~ 
#~ from openalea.image.spatial_image import SpatialImage
from openalea.image.serial.basics import imread
#~ from openalea.container import PropertyGraph

t1 = imread('p194-t1-L1-segExp_corr.inr.gz')
t2 = imread('p194-t2-L1-segExp_corr.inr.gz')
t3 = imread('p194-t3-L1-segExp_corr.inr.gz')
t4 = imread('p194-t4-L1-segExp_corr.inr.gz')
t5 = imread('p194-t5-v1Seg_corrLeo_corrVince.inr.gz')

from openalea.image.algo.analysis import SpatialImageAnalysis
analysis1 = SpatialImageAnalysis(t1)
analysis2 = SpatialImageAnalysis(t2)
analysis3 = SpatialImageAnalysis(t3)
analysis4 = SpatialImageAnalysis(t4)
analysis5 = SpatialImageAnalysis(t5)

# -- We don't want to compute values (in `graph_from_image()`) for cells at the margins of the stack.
analysis1.remove_margins_cells(verbose=True)
analysis2.remove_margins_cells(verbose=True)
analysis3.remove_margins_cells(verbose=True)
analysis3.remove_cells(826)
analysis4.remove_margins_cells(verbose=True)
analysis5.remove_margins_cells(verbose=True)
not_L1 = [932,1004,1240,894,291,280,362,49,357,1430,2044]
analysis5.remove_cells(not_L1, True)


# -- Attributes `labels` are updated after removing margin cells:
from openalea.image.algo.graph_from_image import graph_from_image
graph_1 = graph_from_image( analysis1.image, labels = list(set(analysis1.labels())-set(read_cell_list_txt("p194-t1-border+SAM.txt"))) )
graph_2 = graph_from_image( analysis2.image, labels = list(set(analysis2.labels())-set(read_cell_list_txt("p194-t2-border+SAM.txt"))) )
graph_3 = graph_from_image( analysis3.image, labels = list(set(analysis3.labels())-set(read_cell_list_txt("p194-t3-border+SAM.txt"))) )
graph_4 = graph_from_image( analysis4.image, labels = list(set(analysis4.labels())-set(read_cell_list_txt("p194-t4-border+SAM.txt"))) )
graph_5 = graph_from_image( analysis5.image, labels = list(set(analysis5.labels())-set(read_cell_list_txt("p194-t5-border+SAM.txt"))) )

# -- Save PropertyGraphs :
import pickle
import gzip
f = gzip.open('p194_PropertyGraphs_FM.pklz','w')
pickle.dump( [graph_1,graph_2,graph_3,graph_4,graph_5], f)
f.close()

#~ # -- load PropertyGraphs :
#~ import pickle
#~ import gzip
#~ f = gzip.open('p194_PropertyGraphs.pklz','r')
#~ graph_1,graph_2,graph_3,graph_4,graph_5 = pickle.load(f)
#~ f.close()

# -- load PropertyGraphs :
import pickle
import gzip
f = gzip.open('p194_PropertyGraphs_FM.pklz','r')
graph_1,graph_2,graph_3,graph_4,graph_5 = pickle.load(f)
f.close()

from vplants.tissue_analysis import LienTissuTXT
lin_12=LienTissuTXT.LienTissuTXT("suiviExpert_t1-t2_260412.txt")
l12=lin_12.cellT1_cellT2
lin_23=LienTissuTXT.LienTissuTXT("suiviExpert_t2-t3_270412.txt")
l23=lin_23.cellT1_cellT2
lin_34=LienTissuTXT.LienTissuTXT("suiviExpert_t3-t4_030512.txt")
l34=lin_34.cellT1_cellT2
lin_45=LienTissuTXT.LienTissuTXT("suiviExpert_t4-t5_030512.txt")
l45=lin_45.cellT1_cellT2

from openalea.container import TemporalPropertyGraph
g = TemporalPropertyGraph()
g.extend([graph_1,graph_2,graph_3, graph_4, graph_5],[l12,l23,l34,l45])

