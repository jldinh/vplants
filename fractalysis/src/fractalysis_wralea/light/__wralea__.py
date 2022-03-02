
# This file has been generated at Thu Jul 31 17:10:57 2008

from openalea.core import *


__name__ = 'vplants.fractalysis.light'

__editable__ = True
__description__ = 'Fractalysis light nodes.'
__license__ = 'CeCILL-C'
__url__ = 'http://openalea.gforge.inria.fr'
__alias__ = ['fractalysis.light']
__version__ = '0.0.2'
__authors__ = 'OpenAlea consortium'
__institutes__ = 'INRIA/CIRAD'
__icon__ = 'light_icon.png'
 

__all__ = ['light_nodes_light_direction', 'light_nodes_light_intercept', 'light_nodes_create_MSS', 'light_nodes_generate_pix', 'light_nodes_light_recieved']



light_nodes_light_direction = Factory(name='Light direction', 
                description='Defines the direction of incident light', 
                category='Light,scene', 
                nodemodule='light_nodes',
                nodeclass='light_direction',
                inputs=({'interface': IBool, 'name': 'Direct directions', 'value': True}, {'interface': IFloat, 'name': 'Latitude', 'value': 43.3643}, {'interface': IFloat, 'name': 'Longitude', 'value': 3.5238}, {'interface': IFloat(min=1, max=365, step=1), 'name': 'Day', 'value': 172}, {'interface': IFloat(min=0, max=23, step=0.500000), 'name': 'Start hour', 'value': 7}, {'interface': IFloat(min=0, max=23, step=0.500000), 'name': 'Stop hour', 'value': 19}, {'interface': IFloat(min=1, max=60, step=1), 'name': 'Time step(min)', 'value': 30}, {'interface': IBool, 'name': 'Turtle directions', 'value': True}, {'interface': IFloat(min=1, max=23, step=1), 'showwidget': False, 'hide': True, 'name': 'Sun shift', 'value': 1}, {'interface': IFloat(min=1, max=23, step=1), 'showwidget': False, 'hide': True, 'name': 'GMT shift', 'value': 0}),
                outputs=({'interface': ISequence, 'name': 'Sunlight directions'},),
                widgetmodule=None,
                widgetclass=None,
                )




light_nodes_light_intercept = Factory(name='Light interception', 
                description='Compute directional light interception as STAR values and shadow picture', 
                category='Light,scene', 
                nodemodule='light_nodes',
                nodeclass='light_intercept',
                inputs=({'interface': None, 'name': 'MSS'}, {'interface': ISequence, 'showwidget': False, 'name': 'Light direction'}, {'interface': ISequence, 'name': 'Distribution'}, {'interface': IEnumStr(enum=('100x100', '150x150', '200x200', '300x300', '600x600')), 'name': 'Image size', 'value': '150x150'}, {'interface': IDirStr, 'name': 'Save path'}),
                outputs=({'interface': IFloat, 'name': 'Star turbid'}, {'interface': IFloat, 'name': 'Star'}, {'interface': None, 'name': 'Image'}),
                widgetmodule=None,
                widgetclass=None,
                )




light_nodes_create_MSS = Factory(name='create MSS', 
                description='Generates a multi scale structure', 
                category='Light,scene', 
                nodemodule='light_nodes',
                nodeclass='create_MSS',
                inputs=({'interface': IStr, 'name': 'Name', 'value': 'myMMS'}, 
                {'interface': None, 'name': 'Scene'}, 
                {'interface': ISequence, 'name': 'Scale table', 'value': None}, 
                {'interface': IEnumStr(enum=('Cvx Hull', 'Sphere', 'Ellipse', 'Box')), 'name': 'Enveloppe type', 'value': 'Cvx Hull'},
                {'interface': IDict, 'name': 'Opacities'}
                      ),
                outputs=({'interface': None, 'name': 'MSS'},),
                widgetmodule=None,
                widgetclass=None,
                )




light_nodes_generate_pix = Factory(name='generatePix', 
                description='Generates directional shadow picture', 
                category='Light,scene', 
                nodemodule='light_nodes',
                nodeclass='generate_pix',
                inputs=({'interface': None, 'name': 'MSS'}, {'interface': ISequence, 'name': 'Light direction'}, {'interface': ISequence, 'name': 'Distribution'}, {'interface': IEnumStr(enum=('100x100', '150x150', '200x200', '300x300', '600x600')), 'name': 'Image size', 'value': '300x300'}, {'interface': IDirStr, 'name': 'Save path'}),
                outputs=({'interface': None, 'name': 'Image'},),
                widgetmodule=None,
                widgetclass=None,
                )




light_nodes_light_recieved = Factory(name='Received light', 
                description='Compute directional recieved light for one scale as relative ratio', 
                category='Light,scene', 
                nodemodule='light_nodes',
                nodeclass='light_received',
                inputs=({'interface': None, 'name': 'MSS'}, {'interface': IFloat(min=1, max=16777216, step=1), 'name': 'Scale', 'value': 1}, {'interface': ISequence, 'showwidget': False, 'name': 'Light direction'}, {'interface': IEnumStr(enum=('Multiscale', 'Real', 'Turbid')), 'name': 'Mode', 'value': 'Multiscale'}, {'interface': IEnumStr(enum=('100x100', '150x150', '200x200', '300x300', '600x600')), 'name': 'Image size', 'value': '150x150'}, {'interface': IDirStr, 'name': 'Save path'}),
                outputs=({'interface': IDict, 'name': 'Recieved ratio'}, {'interface': None, 'name': 'PGL scene'}),
                widgetmodule=None,
                widgetclass=None,
                )




