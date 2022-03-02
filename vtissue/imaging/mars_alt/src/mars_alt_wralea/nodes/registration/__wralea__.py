from openalea.core import *


__name__ = 'vplants.mars_alt.nodes.registration'

__editable__ = True
__description__ = 'Nodes that compute transforms between images and compute resampled images'
__license__ = 'CECILL-C'
__url__ = 'http://openalea.gforge.inria.fr/doc/openalea/pylab/doc/_build/html/contents.html'
__alias__ = []
__version__ = '0.9.0'
__authors__ = 'Daniel BARBEAU'
__institutes__ = 'INRIA/CIRAD'
#__icon__ = 'icon.png'


# -- This is what is used by the package manager to identify what to load --
__all__ = []


#############################
# ORIGINAL FUSION ALGORITHM #
#############################

mars_wra_fusion = Factory(name='fusion_v1',
                          authors='Eric Moscardi',
                          category='vtissue',
                          nodemodule='reconstruction',
                          nodeclass='original_fusion',
                          inputs=({'interface': "IImage", 'name': 'im_ref'},
                                  {'interface': "IImage", 'name': 'def_ref'},
                                  {'interface': None, 'name': 'images'},
                                  {'interface': None, 'name': 'matrices'},
                                  {'interface': None, 'name': 'deformations'}),
                          outputs=({'interface': "IImage", 'name': 'fused image'},),
                          widgetmodule=None,
                          widgetclass=None,
                          )

__all__.append('mars_wra_fusion')

##########################################
# TASK-BASED RECONSTRUCTION VISUALEA API #
##########################################

reconstruct = Factory(name='reconstruction',
                authors='Daniel BARBEAU',
                category='vtissue',
                nodemodule='reconstruction',
                nodeclass='reconstruct',
                inputs=({'interface': "ISequence", 'name': 'task_list'},
                        {'interface': "IDict", 'name': 'fuse_kwargs'},
                        {'interface': None, 'name': 'mean_reg_init', "value":None},
                        {'interface': None, 'name': 'mean_reg_lin', "value":None},
                        {'interface': None, 'name': 'mean_reg_non_lin', "value":None},
                        {'interface': None, 'name': 'mean_reg_init_field', "value":None},                
                        ),
                outputs=({'interface': "ISequence", 'name': 'task_list'},
                         {'interface': "ISequence", 'name': 'reconstruction_results'}),
                widgetmodule=None,
                widgetclass=None,
               )
__all__.append("reconstruct")

fuse_reconstruction = Factory(name='fuse_reconstruction',
                authors='Daniel BARBEAU',
                category='vtissue',
                nodemodule='reconstruction',
                nodeclass='fuse_reconstruction',
                inputs=({'interface': "ISequence", 'name': 'task_list'},
                        {'interface': "ISequence", 'name': 'reconstruction_results'},
                        {'interface': "ITuple3", 'name':'min_vs', 'value':None},
                        {'interface': None, 'name':'cast', 'value':"auto"},
                        {'interface': "IBool", 'name': 'interm', 'value':False},
                        {'interface': "IFunction", 'name': 'z_att_f', 'value':None},
                        {'interface': IEnumStr(["linear", "nearest"]), 'name': 'interpolation', 'value':"linear"},
                        {'interface': "IBool", 'name': 'use_ref_canvas', 'value':True},                        
                        ),
                outputs=({'interface': "IImage", 'name': 'fused_image'},
                         {'interface': "ISequence", 'name': 'interm'},
                         ),
                widgetmodule=None,
                widgetclass=None,
               )
__all__.append("fuse_reconstruction")

ldmark_params = Factory(name='register_landmarks',
                authors='Daniel BARBEAU',
                category='vtissue',
                nodemodule='reconstruction',
                nodeclass='surface_landmark_matching_parameters',
                inputs=({'interface': "ISequence", 'name': 'ref_pts'},
                        {'interface': "ISequence", 'name': 'flo_pts'},
                        {'interface': "IBool", 'name': 'spatialise_points', 'value':False},
                        {'interface': "IFloat", 'name': 'threshold', 'value':45},
                        ),
                outputs=({'interface': None, 'name': 'landmark_params'},),
                widgetmodule=None,
                widgetclass=None,
               )
__all__.append("ldmark_params")

linear_params = Factory(name='register_auto_linear',
                        authors='Daniel BARBEAU',
                        category='vtissue',
                        nodemodule='reconstruction',
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

non_linear_params = Factory(name='register_auto_non_linear',
                            authors='Daniel BARBEAU',
                            category='vtissue',
                            nodemodule='reconstruction',
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
                              category='vtissue',
                              nodemodule='reconstruction',
                              nodeclass='reconstruction_task',
                              inputs=({'interface': "IImage", 'name': 'ref_image'},
                                      {'interface': "IImage", 'name': 'flo_image'},
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

fuse_tasks = Factory(name='fusion',
                authors='Daniel BARBEAU',
                category='vtissue',
                nodemodule='reconstruction',
                nodeclass='fusion',
                inputs=({'interface': "ISequence", 'name': 'task_list'},
                        {'interface': "IBool", 'name': "care_for_memory", 'value' : True},
                        {'interface': None, 'name':'cast', 'value':"auto"},
                        {'interface': 'IFloat', 'name':'min_vs', "value":None},
                        {'interface': "IBool", 'name': 'interm', 'value':False},
                        {'interface': "IFunction", 'name': 'z_att_f', 'value':None},
                        {'interface': IEnumStr(["linear", "nearest"]), 'name': 'interpolation', 'value':"linear"},
                        {'interface': "IBool", 'name': 'use_ref_canvas', 'value':True}),
                outputs=({'interface': "IImage", 'name': 'fused_image'},
                         {'interface': "ISequence", 'name': 'interm'},
                         ),
                widgetmodule=None,
                widgetclass=None,
               )
__all__.append("fuse_tasks")


fusion_task = Factory(name='fusion_task',
                authors='Daniel BARBEAU',
                category='vtissue',
                nodemodule='reconstruction',
                nodeclass='fusion_task',
                inputs=({'interface': "IImage", 'name': 'image'},
                        {'interface': ISequence, 'name': 'matrices'},
                        {'interface': "IImage", 'name': 'deformation_field'}),
                outputs=({'interface': None, 'name': 'reconstruction_task'},),
                widgetmodule=None,
                widgetclass=None,
               )
__all__.append("fusion_task")
