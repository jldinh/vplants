from openalea.core import *


__name__ = 'vplants.mars_alt.nodes.analysis'

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




analysis_neighbors = Factory(name='neighbors',
                             authors='Eric Moscardi',
                             description='Return the list of neighbors of a label',
                             category='vtissue',
                             nodemodule='analysis',
                             nodeclass='neighbors',
                             inputs=({'interface': None, 'name': 'image'},
                                     {'interface': ISequence, 'name': 'labels', 'value': None}),
                             outputs=({'interface': ISequence, 'name': 'centers'},),
                             widgetmodule=None,
                             widgetclass=None,
                             )
__all__.append('analysis_neighbors')

analysis_extract_L1 = Factory(name='extract_L1',
                authors='Eric Moscardi',
                description='Extract cells in the layer 1 from a segmented image',
                category='vtissue',
                nodemodule='analysis',
                nodeclass='extract_L1',
                inputs=({'interface': None, 'name': 'image'},),
                outputs=({'interface': ISequence, 'name': 'imL1'},),
                widgetmodule=None,
                widgetclass=None,
               )
__all__.append('analysis_extract_L1')

analysis_volume = Factory(name='volume',
                authors='Eric Moscardi',
                description='Return the volume of the labels',
                category='vtissue',
                nodemodule='analysis',
                nodeclass='volume',
                inputs=({'interface': None, 'name': 'image'},
                        {'interface': ISequence, 'name': 'labels', 'value': None},
                        {'interface': IBool, 'name': 'real', 'value': True}),
                outputs=({'interface': ISequence, 'name': 'centers'},),
                widgetmodule=None,
                widgetclass=None,
               )
__all__.append('analysis_volume')

analysis_surface_area = Factory(name='contact_surface',
                authors='Eric Moscardi',
                description='Return the surface of contact between two labels',
                category='vtissue',
                nodemodule='analysis',
                nodeclass='surface_area',
                inputs=({'interface': None, 'name': 'image'},
                        {'interface': IInt, 'name': 'label1'},
                        {'interface': IInt, 'name': 'label2'}),
                outputs=({'interface': IFloat, 'name': 'centers'},),
                widgetmodule=None,
                widgetclass=None,
               )
__all__.append('analysis_surface_area')

analysis_center_of_mass = Factory(name='center_of_mass',
                authors='Eric Moscardi',
                description='Return the center of mass of the labels',
                category='vtissue',
                nodemodule='analysis',
                nodeclass='center_of_mass',
                inputs=({'interface': None, 'name': 'image'},
                        {'interface': ISequence, 'name': 'labels', 'value': None},
                        {'interface': IBool, 'name': 'real', 'value': True}),
                outputs=({'interface': ISequence, 'name': 'centers'},),
                widgetmodule=None,
                widgetclass=None,
               )
__all__.append('analysis_center_of_mass')

analysis_nlabels = Factory(name='nlabels',
                authors='Eric Moscardi',
                description='Return the number of labels',
                category='vtissue',
                nodemodule='analysis',
                nodeclass='nlabels',
                inputs=({'interface': None, 'name': 'image'},),
                outputs=({'interface': IInt, 'name': 'num_labels'},),
                widgetmodule=None,
                widgetclass=None,
               )
__all__.append('analysis_nlabels')

#########################
# STRUCTURAL ANALYSIS ? #
#########################

structural_analysis_draw_L1 = Factory(name='draw_L1',
                authors='Eric Moscardi',
                description='Draw cells in the layer 1 from a segmented image',
                category='vtissue',
                nodemodule='analysis',
                nodeclass='draw_L1',
                inputs=({'interface': None, 'name': 'image'},),
                outputs=({'interface': None, 'name': 'imL1'},),
                widgetmodule=None,
                widgetclass=None,
               )
__all__.append('structural_analysis_draw_L1')

structural_analysis_draw_walls = Factory(name='draw_walls',
                authors='Eric Moscardi',
                description='Draw walls from a segmented image',
                category='vtissue',
                nodemodule='analysis',
                nodeclass='draw_walls',
                inputs=({'interface': None, 'name': 'image'}, {'interface': IBool, 'name': 'dilation', 'value': False}),
                outputs=({'interface': None, 'name': 'walls'},),
                widgetmodule=None,
                widgetclass=None,
               )
__all__.append('structural_analysis_draw_walls')
