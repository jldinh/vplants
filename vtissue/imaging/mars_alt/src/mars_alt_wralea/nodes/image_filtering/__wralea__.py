from openalea.core import *


__name__ = 'vplants.mars_alt.nodes.image_filtering'

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



mars_wra_filtering = Factory(name='filtering',
                authors='Eric Moscardi',
                category='vtissue',
                nodemodule='filtering',
                nodeclass='wra_filtering',
                inputs=({'interface': None, 'name': 'image'},
                        {'interface': IEnumStr(enum=['gaussian', 'alternate sequential', 'most representative']),
                         'name': 'filter type', 'value': 'gaussian'},
                        {'interface': IFloat, 'name': 'filter value', 'value': 0.5}),
                outputs=({'interface': None, 'name': 'filtered image'},),
                widgetmodule=None,
                widgetclass=None,
               )

__all__.append("mars_wra_filtering")
