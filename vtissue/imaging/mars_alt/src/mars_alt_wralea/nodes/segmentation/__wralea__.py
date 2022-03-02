from openalea.core import *


__name__ = 'vplants.mars_alt.nodes.segmentation'

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



cell_segmentation = Factory(name='cell segmentation',
                            authors='Eric Moscardi',
                            category='vtissue',
                            nodemodule='segmentation',
                            nodeclass='cell_segmentation',
                            inputs=({'interface': None, 'name': 'image'},
                                    {'interface': IInt, 'name': 'h minima'},
                                    {'interface': IFloat, 'name': 'volume'},
                                    {'interface': IBool,  'name' : 'real_vol', 'value':False},
                                    {'interface': IBool,  'name' : 'pre_filter', 'value':True},
                                    {'interface': IEnumStr(["gaussian","asf","mr"]),  'name' : 'filter_type', 'value': "gaussian"},
                                    {'interface': IFloat,  'name' : 'filter_value', 'value': 0.5},),
                            outputs=({'interface': None, 'name': 'segmented image'},
                                     {'interface': None, 'name': 'filtered_image'},
                                     {'interface': None, 'name': 'first_watershed'},
                                     {'interface': None, 'name': 'first_seeds'},
                                     {'interface': None, 'name': 'new_seeds'},
                                     ),
                            widgetmodule=None,
                            widgetclass=None,
                            )
__all__.append("cell_segmentation")


mars_wra_seed_extraction = Factory(name='seed extraction',
                                   authors='Eric Moscardi',
                                   category='vtissue',
                                   nodemodule='segmentation',
                                   nodeclass='seed_extraction',
                                   inputs=({'interface': None, 'name': 'image'},
                                           {'interface': IInt, 'name': 'h minima'}),
                                   outputs=({'interface': None, 'name': 'seeds'},),
                                   widgetmodule=None,
                                   widgetclass=None,
                                   )

__all__.append("mars_wra_seed_extraction")

mars_wra_remove_small_cells = Factory(name='remove small cells',
                                      authors='Eric Moscardi',
                                      category='vtissue',
                                      nodemodule='segmentation',
                                      nodeclass='remove_small_cells',
                                      inputs=({'interface': None, 'name': 'segmented image'},
                                              {'interface': None, 'name': 'labeled markers image'},
                                              {'interface': IFloat, 'name': 'minima volume'},
                                              {'interface': IBool, 'name': 'real-world units', 'value': False}),
                                      outputs=({'interface': None, 'name': 'seeds'},),
                                      widgetmodule=None,
                                      widgetclass=None,
                                      )

__all__.append("mars_wra_remove_small_cells")
