# -- To load the previoulys saved PropertyGraphs :
import pickle
import gzip
f = gzip.open('p58_TemporalPropertyGraphs.pklz','r')
g = pickle.load(f)
f.close()

#~ # -- We want to show the volumes.
#~ from openalea.image.all import display3D, rainbow_blue2red
#~ display3D( analysis1, dictionary = g.translate_from_graph_at_time(g.vertex_property('volume'),0), lut = rainbow_blue2red )
#~ 
#~ # -- Compute the correlation between main axis of curvature and shape
#~ analysis1.compute_principal_curvatures(verbose=True)
#~ axis = analysis1.inertia_axis()
#~ axis_vec = axis[0]
#~ 
#~ from openalea.image.algo.analysis import vector_correlation
#~ coor_curv_main_axis = {}
#~ for n,c in enumerate(analysis1.principal_curvatures_directions):
    #~ coor_curv_main_axis[c] = abs(vector_correlation(analysis1.principal_curvatures_directions[c][0],axis_vec[n][0]))
#~ 
#~ 
#~ from openalea.image.all import display3D, rainbow_blue2green
#~ display3D( analysis1.image, list(set(analysis1.labels())-set(analysis1.L1())), coor_curv_main_axis, rainbow_blue2green, verbose = True, fixed_lut_range=[0,1] )


from openalea.container.temporal_graph_analysis import relative_temporal_change
from openalea.image.all import display3D, rainbow_blue2red
## -- Relative Temporal Change -VOLUME- rank = 1 (t_n -> t_n+1)

# -- Compute and display on the t_n image
VG12 = g.translate_from_graph_at_time(relative_temporal_change(g, 'volume'), 0 )
display3D( analysis1, dictionary = VG12, lut = rainbow_blue2red, verbose = True )
# -- Compute and display on the t_n+1 image
VG21 = g.translate_from_graph_at_time(relative_temporal_change(g, 'volume',labels_at_t_n = False), 1)
display3D( analysis2, dictionary = VG21, lut = rainbow_blue2red, verbose = True )
