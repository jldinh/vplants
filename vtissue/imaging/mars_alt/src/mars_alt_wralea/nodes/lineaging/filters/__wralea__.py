from openalea.core import *


__name__ = 'vplants.mars_alt.nodes.lineaging.filters'

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


has_descendant = Factory(name='has_descendant',
                          authors='Daniel BARBEAU',
                          category='cell lineaging',
                          nodemodule='filters',
                          nodeclass='has_descendant_filter',
                          inputs=[],
                          outputs=[{'interface': "IFunction",    'name': 'filter',    'desc': 'A filter that ensures that all parents have descendants'},],
                          widgetmodule=None,
                          widgetclass=None,
                          )

__all__.append("has_descendant")


growth_conservation = Factory(name='growth_conservation',
                          authors='Daniel BARBEAU',
                          category='cell lineaging',
                          nodemodule='filters',
                          nodeclass='growth_conservation_filter',
                          inputs=[{'interface': "IFloat", 'name': 'threshold', 'value': 0.97, 'desc' : "A factor (volume_p * threshold <= sum_volume_kids"}],
                          outputs=[{'interface': "IFunction",    'name': 'filter',    'desc': "A filter that ensures that the sum of the children's volume is at least equal to the parent's volume"},],
                          widgetmodule=None,
                          widgetclass=None,
                          )

__all__.append("growth_conservation")


one_connected_component = Factory(name='one_connected_component',
                                  authors='Daniel BARBEAU',
                                  category='cell lineaging',
                                  nodemodule='filters',
                                  nodeclass='one_connected_component_filter',
                                  inputs=[],
                                  outputs=[{'interface': "IFunction",    'name': 'filter',    'desc': 'A filter that ensures that for each parent its the children form a single connected component'},],
                                  widgetmodule=None,
                                  widgetclass=None,
                                  )

__all__.append("one_connected_component")


adjacencies_preserved = Factory(name='adjacencies_preserved',
                          authors='Daniel BARBEAU',
                          category='cell lineaging',
                          nodemodule='filters',
                          nodeclass='adjacencies_preserved_filter',
                          inputs=[{'interface': "IInt", 'name': 'nb_adj', 'value': 2, 'desc' : "Maximum number of unrespected adjacencies per parent beyond which the lineage is discarded"}],
                          outputs=[{'interface': "IFunction",    'name': 'filter',    'desc': "A filter that ensures that descendants of neighboor parent cells are adjacent"},],
                          widgetmodule=None,
                          widgetclass=None,
                          )

__all__.append("adjacencies_preserved")


adjacencies_preserved_original = Factory(name='adjacencies_preserved_original',
                          authors='Daniel BARBEAU',
                          category='cell lineaging',
                          nodemodule='filters',
                          nodeclass='adjacencies_preserved2_filter',
                          inputs=[{'interface': "IInt", 'name': 'nb_adj', 'value': 2, 'desc' : "Maximum number of unrespected adjacencies per parent beyond which the lineage is discarded"}],
                          outputs=[{'interface': "IFunction",    'name': 'filter',    'desc': "A filter that ensures that descendants of neighboor parent cells are adjacent"},],
                          widgetmodule=None,
                          widgetclass=None,
                          )

__all__.append("adjacencies_preserved_original")
