from openalea.core import *


__name__ = 'vplants.mars_alt.nodes.lineaging.alt'

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




##################
# ALL-MIGHTY ALT #
##################
alt_preparation = Factory(name='alt_preparation',
                          authors='Daniel BARBEAU',
                          category='cell lineaging',
                          nodemodule='alt',
                          nodeclass='alt_preparation',
                          inputs=[{'interface': 'IDict',     'name': 'expert_map', 'value': None, 'desc': 'Expert mapping to initialise process.'},
                                  {'interface': "IImage",    'name': 'imgSeg0',    'value': None, 'desc': 'Image of segmented organ at t0.'},
                                  {'interface': "IImage",    'name': 'imgSeg1',    'value': None, 'desc': 'Image of segmented organ at t1.'},
                                  {'interface': 'IBool',     'name': 'resampled',  'value': False,'desc': 'Compute resample t0 [fused] image and segmented image.'},
                                  {'interface': "IImage",    'name': 'imgFus0',    'value': None, 'desc': '[Fused] image of organ at t0 (in its original space).'},],
                          outputs=[{'interface': "IImage",    'name': 'imgResampled0',    'desc': '[Fused] image of organ at t0 (in t1 space) if resampled is True.'},
                                   {'interface': "IImage",    'name': 'imgResampled1',    'desc': '[Fused] image of organ at t1 (in its original space)  if resampled is True.'},
                                   {'interface': None,        'name': 'tissue0',          'desc': 'Tissue of t0 segmented image'},
                                   {'interface': None,        'name': 'tissue1',          'desc': 'Tissue of t1 segmented image'},
                                   {'interface': "ISequence", 'name': 'T_vox',            'desc': 'Resampling matrix to put t0 images in t1 space'},],
                          widgetmodule=None,
                          widgetclass=None,
                          )


__all__.append("alt_preparation")

lineaging_full_alt_loop = Factory(name='alt_lineage_loop',
                                  authors='Daniel BARBEAU',
                                  category='cell lineaging',
                                  nodemodule='alt',
                                  nodeclass='full_alt_loop',
                                  inputs=[
                                          {'interface': "IImage",    'name': 'imgSeg0',    'value': None, 'desc': 'Image of segmented organ at t0.'},
                                          {'interface': "IImage",    'name': 'imgSeg1',    'value': None, 'desc': 'Image of segmented organ at t1.'},
                                          {'interface': 'IDict',     'name': 'expert_map', 'value': None, 'desc': 'Expert mapping to initialise process.'},
                                          {'interface': None,        'name': 'tissue0',    'value': None, 'desc': 'Tissue of t0 segmented image'},
                                          {'interface': None,        'name': 'tissue1',    'value': None, 'desc': 'Tissue of t1 segmented image'},
                                          {'interface': "IImage",    'name': 'imgFus0',    'value': None, 'desc': '[Fused] image of organ at t0 (in its original space).'},
                                          {'interface': "IImage",    'name': 'imgFus1',    'value': None, 'desc': '[Fused] image of organ at t1 (in its original space).'},
                                          {'interface': 'ISequence', 'name': 'mat_init',   'value': False,'desc': 'A resampling voxel-to-voxel matrix to put image at t0 in space of image at t1'},
                                          {'interface': "IInt",      'name': 'max_iter',   'value': 20,   'desc': 'Maximum number of iterations (-1 is infinity).'},
                                          {'interface': "IFloat",    'name': 'field_sigma','value': 5.0,  'desc': 'Sigma for gaussian smoothing of initial vector field.'},
                                          {'interface': None,        'name': 'non_linear_registration_params', 'value': None, 'desc': "Parameters to operate a nonlinear registration on t0"},
                                          {'interface': "IFloat",    'name': 'mapping_dist', 'value': 3, 'desc': 'Euclidean distance between mother and child cells beyond which child is discarded.'},
                                          {'interface': "IInt",      'name': 'mapping_ndiv', 'value': 8, 'desc': 'Max number of divisions between the two images.'},
                                          {'interface': IEnumStr(enum=['cell_shape', 'cell_as_box']), 'name': 'candidate_method', 'value': 'cell_shape', 'desc': 'The method to use to estimate candidates.'},
                                          {'interface': IEnumStr(enum=['rf_flow','nx_simplex']), 'name': 'flow_method', 'value': 'rf_flow', 'desc': 'The method to use to solve the flow graph'},
                                          {'interface': "ISequence", 'name': 'filter_params', 'value': None, 'desc': 'list of filters (given as their parameters) to cleanup the candidate lineage.'},
                                          ],
                                  outputs=[{'interface': IDict, 'name': 'lineages', 'desc': 'Filtered dictionnary mapping mother labels to a list of child.'},
                                           {'interface': IStr , 'name': 'stop_reason', 'desc': 'Reason that the algorithm stopped (if identifiable).'},
                                           {'interface': IDict, 'name': 'scores', 'desc': 'Dictionnary of dictionnaries. The top level key is the iteration, the second level key is the parent and the values the scores of the parent for each filter.'},
                                           ],
                                  widgetmodule=None,
                                  widgetclass=None,
                            )


__all__.append("lineaging_full_alt_loop")

