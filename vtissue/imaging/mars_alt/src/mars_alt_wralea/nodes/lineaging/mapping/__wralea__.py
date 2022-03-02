from openalea.core import *


__name__ = 'vplants.mars_alt.nodes.lineaging.mapping'

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



######################
# MAPPING ALL_IN_ONE #
######################

lineaging_mapping = Factory(name='full_mapping',
                            authors='Daniel BARBEAU',
                            category='cell lineaging',
                            nodemodule='lineaging',
                            nodeclass='mapping',
                            inputs=[{'interface': None, 'name': 'im_0', 'value': None, 'desc': 'Image of segmented organ at t0.'},
                                    {'interface': None, 'name': 'im_1', 'value': None, 'desc': 'Image of sefmented organ at t1 in im0 space.'},
                                    {'interface': 'IFloat', 'name': 'dist', 'value': 3, 'desc': 'Euclidean distance between mother and child cells beyond which child is discarded.'},
                                    {'interface': 'IDict', 'name': 'expert_lineage', 'value': None, 'desc': 'Dictionnary containing expert lineaging used to fix cells'},
                                    {'interface': 'IInt', 'name': 'ndiv', 'value': 8, 'desc': 'Max number of divisions between the two images.'},
                                    {'interface': 'IBool', 'name': 'use_binary', 'value': False, 'desc': 'If the original MAPPING executable is available, setting this to True will try to call it'},
                                    {'interface': IEnumStr(enum=['cell_shape', 'cell_as_box']), 'name': 'candidate_method', 'value': 'cell_shape', 'desc': 'The method to use to estimate candidates.'},
                                    {'interface': IEnumStr(enum=['rf_flow']), 'name': 'flow_method', 'value': 'rf_flow', 'desc': 'The method to use to solve the flow graph'}],
                            outputs=[{'interface': IDict, 'name': 'lineages', 'desc': 'Dictionnary mapping mother labels to a list of child.'},
                                     {'interface': IDict, 'name': 'candidates', 'desc': 'Dictionnary mapping mother labels to a list of (child, distance-to-mother).'}],
                            widgetmodule=None,
                            widgetclass=None,
                            )


__all__.append("lineaging_mapping")




lineaging_optimal_lineage = Factory(name='optimal_lineage',
                               authors='Daniel BARBEAU',
                               category='cell lineaging',
                               nodemodule='lineaging',
                               nodeclass='optimal_lineage',
                               inputs=[{'interface': 'IInt', 'name': 'maxLabel0', 'value': None, 'desc': 'Highest label for mothers.'},
                                       {'interface': 'IInt', 'name': 'maxLabel1', 'value': None, 'desc': 'Highest label for children.'},
                                       {'interface': 'IDict', 'name': 'candidates', 'value': None, 'desc': 'A dictionnary mapping mother labels to a list of (child, distance-to-mother).'},
                                       {'interface': 'IDict', 'name': 'expert_lineage', 'value': None, 'desc': 'a dictionnary containing expert lineaging used to fix cells'},
                                       {'interface': 'IInt', 'name': 'ndiv', 'value': 8, 'desc': 'Max number of childs between the two images.'},
                                       {'interface': IEnumStr(enum=['rf_flow', 'nx_simplex']), 'name': 'flow_method', 'value': 'rf_flow', 'desc': 'The method to use to solve the flow graph'}],
                outputs=[{'interface': IDict, 'name': 'lineages', 'desc': 'A dictionnary mapping mother labels to a list of child.'}],
                widgetmodule=None,
                widgetclass=None,
               )

__all__.append("lineaging_optimal_lineage")


lineaging_candidate_lineaging = Factory(name='candidates',
                authors='Daniel BARBEAU',
                category='cell lineaging',
                nodemodule='lineaging',
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

__all__.append("lineaging_candidate_lineaging")
