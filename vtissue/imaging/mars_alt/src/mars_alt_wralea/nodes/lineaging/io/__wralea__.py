from openalea.core import *


__name__ = 'vplants.mars_alt.nodes.lineaging.io'

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



########################
# LINEAGE INPUT/OUTPUT #
########################

lineage_from_file = Factory(name='read_lineage',
                            authors='Daniel BARBEAU',
                            category='cell lineaging',
                            nodemodule='io',
                            nodeclass='lineage_from_file',
                            inputs=[{'interface': IFileStr, 'name': 'lineage_file', 'value': None},
                                    ],
                            outputs = [{'interface': IDict, 'name': 'expert_lineages', 'desc': 'A dictionnary mapping mother labels to a list of child.'}],
                            widgetmodule=None,
                            widgetclass=None,
               )

__all__.append("lineage_from_file")

lineage_to_file = Factory(name='write_lineage',
                          authors='Daniel BARBEAU',
                          category='cell lineaging',
                          nodemodule='io',
                          nodeclass='lineage_to_file',
                          inputs=[{'interface': IFileStr, 'name': 'lineage_file', 'value': None},
                                  {'interface': IDict, 'name': 'expert_lineages', 'desc': 'A dictionnary mapping mother labels to a list of child.'}],
                          outputs=[{'interface': IDict, 'name': 'expert_lineages', 'desc': 'A dictionnary mapping mother labels to a list of child.'}],
                          widgetmodule=None,
                          widgetclass=None,
               )

__all__.append("lineage_to_file")


