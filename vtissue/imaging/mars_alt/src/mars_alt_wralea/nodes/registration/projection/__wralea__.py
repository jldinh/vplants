from openalea.core import *


__name__ = 'vplants.mars_alt.nodes.registration.projection'

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




######################################
# MAXIMUM INTENSITY PROJECTION NODES #
######################################

mars_wra_mask_surface = Factory(name='im2surface',
                                authors='Eric Moscardi',
                                category='vtissue',
                                nodemodule='projection',
                                nodeclass='im2surface',
                                inputs=({'interface': "IImage", 'name': 'image'},
                                        {'interface':IFloat,'name': 'threshold_value', 'value':45.},),
                                outputs=({'interface': "IImage", 'name': 'maximum intensity projection'},
                                         {'interface': "IImage", 'name': 'altitude'}),
                                widgetmodule=None,
                                widgetclass=None,
                                )

__all__.append("mars_wra_mask_surface")

mars_wra_mask_coordinates = Factory(name='surface2im',
                                    authors='Eric Moscardi',
                                    category='vtissue',
                                    nodemodule='projection',
                                    nodeclass='surface2im',
                                    inputs=({'interface': None, 'name': 'points'}, {'interface': None, 'name': 'altitude'}),
                                    outputs=({'interface': None, 'name': 'mask coordinates'},),
                                    widgetmodule=None,
                                    widgetclass=None,
                                    )

__all__.append("mars_wra_mask_coordinates")

