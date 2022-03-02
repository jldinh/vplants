from openalea.core import *


__name__ = 'vplants.mars_alt.nodes.registration.lineages'

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




##############################
# LINEAGE REGISTRATION NODES #
##############################

alt_deformation_field = Factory(name='lineage2deformation',
                                authors='Eric Moscardi',
                                category='vtissue',
                                nodemodule='lineage_registration',
                                nodeclass='deformation_field',
                                inputs=({'interface': "IImage", 'name': 'parent cells segmented image '},
                                        {'interface': "IImage", 'name': 'daugther cells segmented image '},
                                        {'interface': IDict, 'name': 'mapping initialisation'},
                                        {'interface': IFloat, 'name': 'sigma'}),
                                outputs=({'interface': "IImage", 'name': 'vector field'},),
                                widgetmodule=None,
                                widgetclass=None,
                                )

__all__.append("alt_deformation_field")

alt_alt_preparation = Factory(name='lineage2rigid',
                              authors='Eric Moscardi',
                              category='vtissue',
                              nodemodule='lineage_registration',
                              nodeclass='alt_preparation',
                              inputs=({'interface': IDict, 'name': 'mapping'},
                                      {'interface': "IImage", 'name': 'imageFusion0'},
                                      {'interface': "IImage", 'name': 'imageFusion1'},
                                      {'interface': "IImage", 'name': 'imageSegmentation0'},
                                      {'interface': "IImage", 'name': 'imageSegmentation1'}),
                              outputs=({'interface': "IImage", 'name': 'imageFusionResampled'},
                                       {'interface': "IImage", 'name': 'imageSegmentationResampled'},
                                       {'interface': "ISequence", 'name': "transfo"}),
                              widgetmodule=None,
                              widgetclass=None,
                              )

__all__.append("alt_alt_preparation")

