
# This file has been generated at Tue May 31 17:52:52 2011

from openalea.core import *


__name__ = 'vplants.mars_alt.nodes'

__editable__ = True
__description__ = 'vtissue nodes'
__license__ = 'CECILL-C'
__url__ = 'http://openalea.gforge.inria.fr/doc/openalea/pylab/doc/_build/html/contents.html'
__alias__ = []
__version__ = '0.8.0'
__authors__ = 'Eric Moscardi'
__institutes__ = 'INRIA/CIRAD'
__icon__ = 'icon.png'


__all__ = ['mars_wra_seed_extraction', 'wra_analysis_neighbors', 'mars_wra_mask_surface', 'mars_mostRepresentative_filter', 'wra_analysis_wra_extract_L1', 'wra_lineaging_lineage_from_file', 'mars_wra_mask_coordinates', 'alt_deformation_field', 'wra_lineaging_mapping', 'wra_lineaging_flow_graph', 'wra_analysis_volume', 'wra_analysis_surface_area', 'init_alt_node_init_alt', 'mars_wra_filtering', 'alt_alt_preparation', 'wra_structural_analysis_wra_draw_walls', 'wra_analysis_center_of_mass', 'wra_lineaging_candidate_lineaging', 'wra_analysis_nlabels', 'mars_wra_remove_small_cells', 'mars_wra_fusion', 'wra_structural_analysis_wra_draw_L1', 'spatialise_matrix_points']



mars_wra_seed_extraction = Factory(name='seed extraction',
                authors='Eric Moscardi (wralea authors)',
                description='',
                category='vtissue',
                nodemodule='mars',
                nodeclass='wra_seed_extraction',
                inputs=({'interface': None, 'name': 'image'}, {'interface': IInt, 'name': 'h minima'}),
                outputs=({'interface': None, 'name': 'seeds'},),
                widgetmodule=None,
                widgetclass=None,
               )




wra_analysis_neighbors = Factory(name='neighbors',
                authors='Eric Moscardi (wralea authors)',
                description='Return the list of neighbors of a label',
                category='vtissue',
                nodemodule='wra_analysis',
                nodeclass='neighbors',
                inputs=({'interface': None, 'name': 'image'}, {'interface': ISequence, 'name': 'labels', 'value': None}),
                outputs=({'interface': ISequence, 'name': 'centers'},),
                widgetmodule=None,
                widgetclass=None,
               )




mars_wra_mask_surface = Factory(name='im2surface',
                authors='Eric Moscardi (wralea authors)',
                description='It computes a surfacic view of the meristem, according to a revisited version of the method described in Barbier de Reuille and al. in Plant Journal.',
                category='vtissue',
                nodemodule='mars',
                nodeclass='wra_mask_surface',
                inputs=({'interface': None, 'name': 'image'},
                        {'interface':IFloat,'name': 'threshold_value', 'value':45.},),
                outputs=({'interface': None, 'name': 'maximum intensity projection'}, {'interface': None, 'name': 'altitude'}),
                widgetmodule=None,
                widgetclass=None,
               )




mars_mostRepresentative_filter = Factory(name='mostRepresentative filter',
                authors='Eric Moscardi (wralea authors)',
                description='Return the most representated value in a neighborhood',
                category='vtissue',
                nodemodule='mars',
                nodeclass='mostRepresentative_filter',
                inputs=({'interface': None, 'name': 'image'}, {'interface': IInt, 'name': 'size'}),
                outputs=({'interface': None, 'name': 'denoised image'},),
                widgetmodule=None,
                widgetclass=None,
               )




wra_analysis_wra_extract_L1 = Factory(name='extract_L1',
                authors='Eric Moscardi (wralea authors)',
                description='Extract cells in the layer 1 from a segmented image',
                category='vtissue',
                nodemodule='wra_analysis',
                nodeclass='wra_extract_L1',
                inputs=({'interface': None, 'name': 'image'},),
                outputs=({'interface': ISequence, 'name': 'imL1'},),
                widgetmodule=None,
                widgetclass=None,
               )




wra_lineaging_lineage_from_file = Factory(name='read_lineage',
                authors='Daniel BARBEAU',
                description='Reads a lineage definition file and outputs a dict',
                category='cell lineaging',
                nodemodule='wra_lineaging',
                nodeclass='lineage_from_file',
                inputs=[{'interface': IFileStr, 'name': 'lineage_file', 'value': None, 'desc': 'Image of segmented organ at t0.'}],
                outputs=[{'interface': IDict, 'name': 'expert_lineages', 'desc': 'A dictionnary mapping mother labels to a list of child.'}],
                widgetmodule=None,
                widgetclass=None,
               )




mars_wra_mask_coordinates = Factory(name='surface2im',
                authors='Eric Moscardi (wralea authors)',
                description='',
                category='vtissue',
                nodemodule='mars',
                nodeclass='wra_mask_coordinates',
                inputs=({'interface': None, 'name': 'points'}, {'interface': None, 'name': 'altitude'}),
                outputs=({'interface': None, 'name': 'mask coordinates'},),
                widgetmodule=None,
                widgetclass=None,
               )




alt_deformation_field = Factory(name='deformation field',
                authors='Eric Moscardi (wralea authors)',
                description='Computation of a deformation field based on a set of lineages',
                category='vtissue',
                nodemodule='alt',
                nodeclass='deformation_field',
                inputs=({'interface': None, 'name': 'parent cells segmented image '}, {'interface': None, 'name': 'daugther cells segmented image '}, {'interface': IDict, 'name': 'mapping initialisation'}, {'interface': IFloat, 'name': 'sigma'}),
                outputs=({'interface': None, 'name': 'vector field'},),
                widgetmodule=None,
                widgetclass=None,
               )




wra_lineaging_mapping = Factory(name='mapping',
                authors='Daniel BARBEAU',
                description='Given two images of an organ at t0 and t1, finds cell lineages.',
                category='cell lineaging',
                nodemodule='wra_lineaging',
                nodeclass='mapping',
                inputs=[{'interface': None, 'name': 'im_0', 'value': None, 'desc': 'Image of segmented organ at t0.'},
                        {'interface': None, 'name': 'im_1', 'value': None, 'desc': 'Image of sefmented organ at t1 in im0 space.'},
                        {'interface': 'IFloat', 'name': 'dist', 'value': 3, 'desc': 'Euclidean distance between mother and child cells beyond which child is discarded.'},
                        {'interface': 'IDict', 'name': 'expert_lineage', 'value': None, 'desc': 'Dictionnary containing expert lineaging used to fix cells'},
                        {'interface': 'IInt', 'name': 'ndiv', 'value': 8, 'desc': 'Max number of childs between the two images.'},
                        {'interface': 'IBool', 'name': 'use_binary', 'value': False, 'desc': 'If the original MAPPING executable is available, setting this to True will try to call it'},
                        {'interface': IEnumStr(enum=['cell_shape', 'cell_as_sphere']), 'name': 'candidate_method', 'value': 'cell_shape', 'desc': 'The method to use to estimate candidates.'},
                        {'interface': IEnumStr(enum=['rf_flow']), 'name': 'flow_method', 'value': 'rf_flow', 'desc': 'The method to use to solve the flow graph'}],
                outputs=[{'interface': IDict, 'name': 'lineages', 'desc': 'Dictionnary mapping mother labels to a list of child.'},
                         {'interface': IDict, 'name': 'candidates', 'desc': 'Dictionnary mapping mother labels to a list of (child, distance-to-mother).'}],
                widgetmodule=None,
                widgetclass=None,
               )




wra_lineaging_flow_graph = Factory(name='lineage_flow_graph',
                authors='Daniel BARBEAU',
                description='',
                category='cell lineaging',
                nodemodule='wra_lineaging',
                nodeclass='flow_graph',
                inputs=[{'interface': 'IInt', 'name': 'maxLabel0', 'value': None, 'desc': 'Highest label for mothers.'}, {'interface': 'IInt', 'name': 'maxLabel1', 'value': None, 'desc': 'Highest label for children.'}, {'interface': 'IDict', 'name': 'candidates', 'value': None, 'desc': 'A dictionnary mapping mother labels to a list of (child, distance-to-mother).'}, {'interface': 'IDict', 'name': 'expert_lineage', 'value': None, 'desc': 'a dictionnary containing expert lineaging used to fix cells'}, {'interface': 'IInt', 'name': 'ndiv', 'value': 8, 'desc': 'Max number of childs between the two images.'}, {'interface': IEnumStr(enum=['rf_flow', 'nx_simplex']), 'name': 'flow_method', 'value': 'rf_flow', 'desc': 'The method to use to solve the flow graph'}],
                outputs=[{'interface': IDict, 'name': 'lineages', 'desc': 'A dictionnary mapping mother labels to a list of child.'}],
                widgetmodule=None,
                widgetclass=None,
               )




wra_analysis_volume = Factory(name='volume',
                authors='Eric Moscardi (wralea authors)',
                description='Return the volume of the labels',
                category='vtissue',
                nodemodule='wra_analysis',
                nodeclass='volume',
                inputs=({'interface': None, 'name': 'image'}, {'interface': ISequence, 'name': 'labels', 'value': None}, {'interface': IBool, 'name': 'real', 'value': True}),
                outputs=({'interface': ISequence, 'name': 'centers'},),
                widgetmodule=None,
                widgetclass=None,
               )




wra_analysis_surface_area = Factory(name='surface_area',
                authors='Eric Moscardi (wralea authors)',
                description='Return the surface of contact between two labels',
                category='vtissue',
                nodemodule='wra_analysis',
                nodeclass='surface_area',
                inputs=({'interface': None, 'name': 'image'}, {'interface': IInt, 'name': 'label1'}, {'interface': IInt, 'name': 'label2'}),
                outputs=({'interface': IFloat, 'name': 'centers'},),
                widgetmodule=None,
                widgetclass=None,
               )




init_alt_node_init_alt = Factory(name='ALT initialization',
                authors='Eric Moscardi (wralea authors)',
                description='initialization of alt',
                category='vtissue',
                nodemodule='init_alt_node',
                nodeclass='init_alt',
                inputs=({'interface': None, 'name': 'image1'}, {'interface': None, 'name': 'image2'}, {'interface': None, 'name': 'points1'}, {'interface': None, 'name': 'points2'}, {'interface': None, 'hide': True, 'name': 'new_points1'}, {'interface': None, 'hide': True, 'name': 'new_points2'}),
                outputs=({'interface': None, 'name': 'image1'}, {'interface': None, 'name': 'image2'}, {'interface': None, 'name': 'points1'}, {'interface': None, 'name': 'points2'}),
                widgetmodule='init_alt_widget',
                widgetclass='InitALTWidget',
               )




mars_wra_filtering = Factory(name='filtering',
                authors='Eric Moscardi (wralea authors)',
                description='',
                category='vtissue',
                nodemodule='mars',
                nodeclass='wra_filtering',
                inputs=({'interface': None, 'name': 'image'}, {'interface': IEnumStr(enum=['gaussian', 'alternate sequential filter']), 'name': 'filter type', 'value': 'gaussian'}, {'interface': IFloat, 'name': 'filter value', 'value': 0.5}),
                outputs=({'interface': None, 'name': 'filtered image'},),
                widgetmodule=None,
                widgetclass=None,
               )




alt_alt_preparation = Factory(name='alt preparation',
                authors='Eric Moscardi (wralea authors)',
                description='Prepare the alt by doing the registration of the segmented and fused images using the initial mapping',
                category='vtissue',
                nodemodule='alt',
                nodeclass='alt_preparation',
                inputs=({'interface': IDict, 'name': 'mapping'}, {'interface': None, 'name': 'imageFusion0'}, {'interface': None, 'name': 'imageFusion1'}, {'interface': None, 'name': 'imageSegmentation0'}, {'interface': None, 'name': 'imageSegmentation1'}),
                outputs=({'interface': None, 'name': 'imageFusionResampled'}, {'interface': None, 'name': 'imageSegmentationResampled'}),
                widgetmodule=None,
                widgetclass=None,
               )




wra_structural_analysis_wra_draw_walls = Factory(name='draw_walls',
                authors='Eric Moscardi (wralea authors)',
                description='Draw walls from a segmented image',
                category='vtissue',
                nodemodule='wra_structural_analysis',
                nodeclass='wra_draw_walls',
                inputs=({'interface': None, 'name': 'image'}, {'interface': IBool, 'name': 'dilation', 'value': False}),
                outputs=({'interface': None, 'name': 'walls'},),
                widgetmodule=None,
                widgetclass=None,
               )




wra_analysis_center_of_mass = Factory(name='center_of_mass',
                authors='Eric Moscardi (wralea authors)',
                description='Return the center of mass of the labels',
                category='vtissue',
                nodemodule='wra_analysis',
                nodeclass='center_of_mass',
                inputs=({'interface': None, 'name': 'image'}, {'interface': ISequence, 'name': 'labels', 'value': None}, {'interface': IBool, 'name': 'real', 'value': True}),
                outputs=({'interface': ISequence, 'name': 'centers'},),
                widgetmodule=None,
                widgetclass=None,
               )




wra_lineaging_candidate_lineaging = Factory(name='lineage_candidates',
                authors='Daniel BARBEAU',
                description='Given two images of an organ at t0 and t1, finds possible lineages (one cell in t1 can be found to be a possible child of two different cells in t0)',
                category='cell lineaging',
                nodemodule='wra_lineaging',
                nodeclass='candidate_lineaging',
                inputs=[{'interface': None, 'name': 'im_0', 'value': None, 'desc': 'Image of segmented organ at t0.'},
                        {'interface': None, 'name': 'im_1', 'value': None, 'desc': 'Image of sefmented organ at t1 in im0 space.'},
                        {'interface': 'IFloat', 'name': 'dist', 'value': 3, 'desc': 'Euclidean distance between mother and child cells beyond which child is discarded.'},
                        {'interface': 'IInt', 'name': 'ndiv', 'value': 8, 'desc': 'Max number of childs between the two images.'},
                        {'interface': 'IInt', 'name': 'bkgdLabel', 'value': 1, 'desc': 'Value of the background label'},
                        {'interface': 'IBool', 'name': 'rfernandezCompatible', 'value': True, 'desc': 'Output mapping labels start at 2, 1 being the background'},
                        {'interface': IEnumStr(enum=['cell_shape', 'cell_as_box']), 'name': 'candidate_method', 'value': 'cell_shape', 'desc': 'The method to use to estimate candidates.'}],
                outputs=[{'interface': IDict, 'name': 'candidates', 'desc': 'A dictionnary mapping mother labels to a list of (child, distance-to-mother).'}],
                widgetmodule=None,
                widgetclass=None,
               )




wra_analysis_nlabels = Factory(name='nlabels',
                authors='Eric Moscardi (wralea authors)',
                description='Return the number of labels',
                category='vtissue',
                nodemodule='wra_analysis',
                nodeclass='nlabels',
                inputs=({'interface': None, 'name': 'image'},),
                outputs=({'interface': IInt, 'name': 'num_labels'},),
                widgetmodule=None,
                widgetclass=None,
               )




mars_wra_remove_small_cells = Factory(name='remove small cells',
                authors='Eric Moscardi (wralea authors)',
                description='',
                category='vtissue',
                nodemodule='mars',
                nodeclass='wra_remove_small_cells',
                inputs=({'interface': None, 'name': 'segmented image'}, {'interface': None, 'name': 'labeled markers image'}, {'interface': IFloat, 'name': 'minima volume'}, {'interface': IBool, 'name': 'real-world units', 'value': False}),
                outputs=({'interface': None, 'name': 'seeds'},),
                widgetmodule=None,
                widgetclass=None,
               )


mars_wra_fusion = Factory(name='fusion',
                authors='Eric Moscardi (wralea authors)',
                description='',
                category='vtissue',
                nodemodule='mars',
                nodeclass='wra_fusion',
                inputs=({'interface': None, 'name': 'im_ref'}, {'interface': None, 'name': 'def_ref'}, {'interface': None, 'name': 'images'}, {'interface': None, 'name': 'matrices'}, {'interface': None, 'name': 'deformations'}),
                outputs=({'interface': None, 'name': 'fused image'},),
                widgetmodule=None,
                widgetclass=None,
               )


wra_structural_analysis_wra_draw_L1 = Factory(name='draw_L1',
                authors='Eric Moscardi (wralea authors)',
                description='Draw cells in the layer 1 from a segmented image',
                category='vtissue',
                nodemodule='wra_structural_analysis',
                nodeclass='wra_draw_L1',
                inputs=({'interface': None, 'name': 'image'},),
                outputs=({'interface': None, 'name': 'imL1'},),
                widgetmodule=None,
                widgetclass=None,
               )


spatialise_matrix_points = Factory(name="spatialise_matrix_points",
                                   authors="Daniel Barbeau",
                                   category='vtissue',
                                   nodemodule="mars",
                                   nodeclass="spatialise_matrix_points",
                                   inputs=[dict(name="points", interface="ISequence"),
                                           dict(name="image")],
                                   outputs=[dict(name="points", interface="ISequence")]
                                   )



##########################################
# TASK-BASED RECONSTRUCTION VISUALEA API #
##########################################

reconstruct = Factory(name='reconstruct',
                authors='Daniel BARBEAU',
                description='',
                category='vtissue',
                nodemodule='mars',
                nodeclass='reconstruct',
                inputs=({'interface': "ISequence", 'name': 'task_list'},),
                outputs=({'interface': "ISequence", 'name': 'task_list'},
                         {'interface': "ISequence", 'name': 'reconstruction_results'}),
                widgetmodule=None,
                widgetclass=None,
               )
__all__.append("reconstruct")

fuse_reconstruction = Factory(name='fuse_reconstruction',
                authors='Daniel BARBEAU',
                description='',
                category='vtissue',
                nodemodule='mars',
                nodeclass='fuse_reconstruction',
                inputs=({'interface': "ISequence", 'name': 'task_list'},
                         {'interface': "ISequence", 'name': 'reconstruction_results'}),
                outputs=({'interface': None, 'name': 'fused_image'},),
                widgetmodule=None,
                widgetclass=None,
               )
__all__.append("fuse_reconstruction")

ldmark_params = Factory(name='landmark_registration_params',
                authors='Daniel BARBEAU',
                description='',
                category='vtissue',
                nodemodule='mars',
                nodeclass='surface_landmark_matching_parameters',
                inputs=({'interface': "ISequence", 'name': 'ref_pts'},
                        {'interface': "ISequence", 'name': 'flo_pts'},
                        {'interface': "IBool", 'name': 'spatialise_points', 'value':False},
                        ),
                outputs=({'interface': None, 'name': 'landmark_params'},),
                widgetmodule=None,
                widgetclass=None,
               )
__all__.append("ldmark_params")

linear_params = Factory(name='automatic_linear_registration_params',
                        authors='Daniel BARBEAU',
                        description='',
                        category='vtissue',
                        nodemodule='mars',
                        nodeclass='automatic_linear_parameters',
                        inputs=({'interface': IEnumStr(["rigid","simi","affi"]), 'name': 'transfo_type', 'value':"rigid"},
                                {'interface': IEnumStr(["ltsw","lts","lsw","ls"]), 'name': 'estimator', 'value':"ltsw"},
                                {'interface': IInt, 'name': 'pyramid_levels', 'value': 6},
                                {'interface': IInt, 'name': 'finest_level', 'value': 0},
                                {'interface': IFloat, 'name': 'lts_cut', 'value': 0.55},
                                {'interface': IFloat, 'name': 'variance_fraction', 'value': 1.0},
                                ),
                                outputs=({'interface': None, 'name': 'auto_lin_params'},),
                                widgetmodule=None,
                                widgetclass=None,
                                )
__all__.append("linear_params")

non_linear_params = Factory(name='automatic_non_linear_registration_params',
                            authors='Daniel BARBEAU',
                            description='',
                            category='vtissue',
                            nodemodule='mars',
                            nodeclass='automatic_non_linear_parameters',
                            inputs=({'interface': IInt, 'name': 'start_level', 'value': 3},
                                    {'interface': IInt, 'name': 'end_level', 'value': 1},
                                    {'interface': IInt, 'name': 'max_iterations', 'value': 10},
                                    {'interface': IFloat, 'name': 'highest_fraction', 'value': 0.5},
                                    {'interface': IFloat, 'name': 'minimal_variance', 'value': 0.0},
                                    {'interface': ITuple3, 'name': 'blockSize', 'value': None},
                                    {'interface': ITuple3, 'name': 'neighborhood', 'value': None},
                                    {'interface': IEnumStr(["cc"]), 'name': 'similarity', 'value': "cc"},
                                    {'interface': IInt, 'name': 'outlier_sigma', 'value': 3},
                                    {'interface': IInt, 'name': 'threads', 'value': 1},
                                    ),
                            outputs=({'interface': None, 'name': 'auto_non_lin_params'},),
                            widgetmodule=None,
                            widgetclass=None,
                            )
__all__.append("non_linear_params")


reconstruction_task = Factory(name='reconstruction_task',
                              authors='Daniel BARBEAU',
                              description='',
                              category='vtissue',
                              nodemodule='mars',
                              nodeclass='reconstruction_task',
                              inputs=({'interface': None, 'name': 'ref_image'},
                                      {'interface': None, 'name': 'flo_image'},
                                      {'interface': None, 'name': 'landmark_params'},
                                      {'interface': None, 'name': 'auto_lin_params'},
                                      {'interface': None, 'name': 'auto_non_lin_params'},
                                      ),
                              outputs=({'interface': None, 'name': 'reconstruction_task'},),
                              widgetmodule=None,
                              widgetclass=None,
                                )
__all__.append("reconstruction_task")


##################################
# TASK-BASED FUSION VISUALEA API #
##################################

fuse_tasks = Factory(name='fuse_tasks',
                authors='Daniel BARBEAU',
                description='',
                category='vtissue',
                nodemodule='mars',
                nodeclass='fusion',
                inputs=({'interface': "ISequence", 'name': 'task_list'},
                        {'interface': "IBool", 'name': "care_for_memory", 'value' : True} ),
                outputs=({'interface': None, 'name': 'fused_image'},),
                widgetmodule=None,
                widgetclass=None,
               )
__all__.append("fuse_tasks")


fusion_task = Factory(name='fusion_task',
                authors='Daniel BARBEAU',
                description='',
                category='vtissue',
                nodemodule='mars',
                nodeclass='fusion_task',
                inputs=({'interface': None, 'name': 'image'},
                        {'interface': ISequence, 'name': 'matrices'},
                        {'interface': None, 'name': 'deformation_field'}),
                outputs=({'interface': None, 'name': 'reconstruction_task'},),
                widgetmodule=None,
                widgetclass=None,
               )
__all__.append("fusion_task")
