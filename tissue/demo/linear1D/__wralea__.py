
# This file has been generated at Sun Dec 20 12:16:28 2009

from openalea.core import *


__name__ = 'demo.tissue.linear1D'

__editable__ = True
__description__ = '1D demo fo growing tissue'
__license__ = ''
__url__ = ''
__alias__ = []
__version__ = ''
__authors__ = 'jerome chopard'
__institutes__ = ''
__icon__ = ''


__all__ = ['division_division', 'state_state', '_25810512']



division_division = Factory(name='division',
                description='',
                category='Unclassified',
                nodemodule='division',
                nodeclass='division',
                inputs=[{'interface': None, 'name': 'tissuedb', 'value': None, 'desc': ''}, {'interface': IDict, 'name': 'prop', 'value': None, 'desc': ''}, {'interface': IFloat, 'name': 'threshold', 'value': 9999999.0, 'desc': ''}],
                outputs=[{'interface': IFunction, 'name': 'func', 'desc': ''}],
                widgetmodule=None,
                widgetclass=None,
               )




state_state = Factory(name='state',
                description='',
                category='Unclassified',
                nodemodule='state',
                nodeclass='state',
                inputs=[{'interface': None, 'name': 'tissuedb', 'value': None, 'desc': ''}],
                outputs=[{'interface': IFunction, 'name': 'func', 'desc': ''}],
                widgetmodule=None,
                widgetclass=None,
               )




_25810512 = CompositeNodeFactory(name='demo growth',
                             description='',
                             category='Unclassified',
                             doc='',
                             inputs=[],
                             outputs=[],
                             elt_factory={  2: ('tissue.data', 'linear1D.zip'),
   3: ('tissue.core', 'read'),
   4: ('tissue.growth', 'unconstrained1D'),
   5: ('tissue.core', 'prop'),
   6: ('openalea.data structure', 'float'),
   7: ('tissue.core', 'topo'),
   9: ('vplants.plantgl.objects', 'Material'),
   11: ('pglviewer', 'viewer'),
   12: ('openalea.scheduler', 'scheduler'),
   13: ('pglviewer.gui', 'loopgui'),
   14: ('pglviewer.view', 'loop'),
   16: ('tissue.core', 'prop'),
   17: ('demo.tissue.linear1D', 'state'),
   18: ('tissue.core', 'prop'),
   19: ('demo.tissue.linear1D', 'division'),
   22: ('openalea.scheduler', 'task'),
   25: ('openalea.scheduler', 'task'),
   28: ('openalea.scheduler', 'task'),
   31: ('openalea.scheduler', 'task'),
   32: ('tissue.core', 'prop'),
   33: ('tissue.core', 'topo'),
   34: ('tissue.view', 'mesh_view1D')},
                             elt_connections={  7746080: (5, 1, 34, 1),
   7746104: (34, 0, 11, 0),
   7746128: (3, 0, 7, 0),
   7746152: (18, 0, 19, 0),
   7746176: (13, 0, 11, 1),
   7746200: (18, 1, 19, 1),
   7746224: (14, 0, 13, 0),
   7746248: (6, 0, 4, 3),
   7746272: (34, 1, 31, 0),
   7746296: (9, 0, 34, 3),
   7746320: (2, 0, 3, 0),
   7746344: (28, 0, 12, 0),
   7746368: (31, 0, 12, 0),
   7746392: (32, 0, 33, 0),
   7746416: (3, 0, 32, 0),
   7746440: (19, 0, 25, 0),
   7746464: (12, 0, 14, 0),
   7746488: (3, 0, 17, 0),
   7746536: (4, 0, 22, 0),
   7746560: (7, 0, 5, 0),
   7746632: (16, 1, 4, 2),
   7746680: (7, 1, 34, 0),
   7746704: (33, 0, 16, 0),
   7746728: (25, 0, 12, 0),
   7746752: (32, 1, 4, 0),
   7746776: (22, 0, 12, 0),
   7746800: (17, 0, 28, 0),
   7746824: (33, 1, 4, 1),
   7746848: (3, 0, 18, 0)},
                             elt_data={  2: {  'block': False,
         'caption': 'linear1D.zip',
         'hide': True,
         'lazy': True,
         'port_hide_changed': set([2]),
         'posx': 106.25,
         'posy': 33.75,
         'priority': 0,
         'user_application': None},
   3: {  'block': False,
         'caption': 'read',
         'hide': True,
         'lazy': True,
         'port_hide_changed': set([]),
         'posx': 135.0,
         'posy': 120.0,
         'priority': 0,
         'user_application': None,
         'user_color': (255, 85, 0)},
   4: {  'block': False,
         'caption': 'unconstrained1D',
         'hide': True,
         'lazy': False,
         'port_hide_changed': set([]),
         'posx': 544.43462401795739,
         'posy': 459.81025533108868,
         'priority': 0,
         'user_application': None,
         'user_color': (85, 170, 0)},
   5: {  'block': False,
         'caption': 'prop',
         'hide': True,
         'lazy': True,
         'port_hide_changed': set([]),
         'posx': 163.60788439955107,
         'posy': 353.47397586980924,
         'priority': 0,
         'user_application': None,
         'user_color': (255, 85, 0)},
   6: {  'block': False,
         'caption': '0.0',
         'hide': True,
         'lazy': True,
         'port_hide_changed': set([]),
         'posx': 678.45679012345659,
         'posy': 353.47397586980924,
         'priority': 0,
         'user_application': None},
   7: {  'block': False,
         'caption': 'topo',
         'hide': True,
         'lazy': True,
         'port_hide_changed': set([]),
         'posx': 78.803310886644226,
         'posy': 353.47397586980924,
         'priority': 0,
         'user_application': None,
         'user_color': (255, 85, 0)},
   9: {  'block': False,
         'caption': 'Material',
         'hide': True,
         'lazy': True,
         'port_hide_changed': set([]),
         'posx': 235.41245791245791,
         'posy': 353.47397586980924,
         'priority': 0,
         'user_application': None,
         'user_color': (85, 170, 255)},
   11: {  'block': False,
          'caption': 'viewer',
          'hide': True,
          'lazy': True,
          'port_hide_changed': set([]),
          'posx': 350.61167227833892,
          'posy': 827.5799663299664,
          'priority': 0,
          'user_application': None,
          'user_color': (255, 170, 0)},
   12: {  'block': False,
          'caption': 'scheduler',
          'hide': True,
          'lazy': True,
          'port_hide_changed': set([]),
          'posx': 664.43462401795739,
          'posy': 685.78423120089792,
          'priority': 0,
          'user_application': None},
   13: {  'block': False,
          'caption': 'loopgui',
          'hide': True,
          'lazy': True,
          'port_hide_changed': set([]),
          'posx': 383.57182940516282,
          'posy': 765.27918069584769,
          'priority': 0,
          'user_application': None,
          'user_color': (255, 170, 0)},
   14: {  'block': False,
          'caption': 'loop',
          'hide': True,
          'lazy': True,
          'port_hide_changed': set([]),
          'posx': 681.93462401795739,
          'posy': 745.78423120089792,
          'priority': 0,
          'user_application': None},
   16: {  'block': False,
          'caption': 'prop',
          'hide': True,
          'lazy': True,
          'port_hide_changed': set([]),
          'posx': 614.69996258885135,
          'posy': 353.47397586980924,
          'priority': 0,
          'user_application': None,
          'user_color': (255, 85, 0)},
   17: {  'block': False,
          'caption': 'state',
          'hide': True,
          'lazy': False,
          'port_hide_changed': set([]),
          'posx': 977.64590347923695,
          'posy': 459.81025533108868,
          'priority': 0,
          'user_application': None,
          'user_color': (85, 170, 127)},
   18: {  'block': False,
          'caption': 'prop',
          'hide': True,
          'lazy': True,
          'port_hide_changed': set([]),
          'posx': 780.29180695847344,
          'posy': 353.47397586980924,
          'priority': 0,
          'user_application': None,
          'user_color': (255, 85, 0)},
   19: {  'block': False,
          'caption': 'division',
          'hide': True,
          'lazy': False,
          'port_hide_changed': set([]),
          'posx': 782.39337822671189,
          'posy': 459.81025533108868,
          'priority': 0,
          'user_application': None,
          'user_color': (255, 85, 255)},
   22: {  'block': False,
          'caption': 'task',
          'hide': True,
          'lazy': True,
          'port_hide_changed': set([]),
          'posx': 593.1846240179575,
          'posy': 593.08817340067344,
          'priority': 0,
          'user_application': None,
          'user_color': (85, 170, 0)},
   25: {  'block': False,
          'caption': 'task',
          'hide': True,
          'lazy': True,
          'port_hide_changed': set([]),
          'posx': 809.58754208754215,
          'posy': 593.08817340067344,
          'priority': 0,
          'user_application': None,
          'user_color': (255, 85, 255)},
   28: {  'block': False,
          'caption': 'task',
          'hide': True,
          'lazy': True,
          'port_hide_changed': set([]),
          'posx': 991.93462401795739,
          'posy': 593.08817340067344,
          'priority': 0,
          'user_application': None,
          'user_color': (85, 170, 127)},
   31: {  'block': False,
          'caption': 'task',
          'hide': True,
          'lazy': True,
          'port_hide_changed': set([]),
          'posx': 326.25,
          'posy': 593.08817340067344,
          'priority': 0,
          'user_application': None,
          'user_color': (85, 170, 255)},
   32: {  'block': False,
          'caption': 'prop',
          'hide': True,
          'lazy': True,
          'port_hide_changed': set([]),
          'posx': 474.18630751964065,
          'posy': 353.47397586980924,
          'priority': 0,
          'user_application': None,
          'user_color': (255, 85, 0)},
   33: {  'block': False,
          'caption': 'topo',
          'hide': True,
          'lazy': True,
          'port_hide_changed': set([]),
          'posx': 537.943135054246,
          'posy': 353.47397586980924,
          'priority': 0,
          'user_application': None,
          'user_color': (255, 85, 0)},
   34: {  'block': False,
          'caption': 'mesh_view1D',
          'hide': True,
          'lazy': True,
          'port_hide_changed': set([]),
          'posx': 151.25,
          'posy': 459.81025533108868,
          'priority': 0,
          'user_application': None,
          'user_color': (85, 170, 255)},
   '__in__': {  'block': False,
                'caption': 'In',
                'hide': True,
                'lazy': True,
                'port_hide_changed': set([]),
                'posx': 20.0,
                'posy': 5.0,
                'priority': 0,
                'user_application': None},
   '__out__': {  'block': False,
                 'caption': 'Out',
                 'hide': True,
                 'lazy': True,
                 'port_hide_changed': set([]),
                 'posx': 20.0,
                 'posy': 250.0,
                 'priority': 0,
                 'user_application': None}},
                             elt_value={  2: [  (0, 'PackageData(tissue.data, linear1D.zip)'),
         (1, 'None'),
         (2, 'None')],
   3: [],
   4: [],
   5: [(1, "'position'")],
   6: [(0, '0.01')],
   7: [(1, "'mesh_id'"), (2, "'config'")],
   9: [  (0, "''"),
         (1, '(63, 57, 255)'),
         (2, '2.0'),
         (3, 'Color3(0,0,0)'),
         (4, '1.0'),
         (5, '(0, 0, 0)'),
         (6, '0.0')],
   11: [(2, 'True'), (3, 'None'), (4, "'Viewer'")],
   12: [],
   13: [],
   14: [],
   16: [(1, "'growth_speed'")],
   17: [],
   18: [(1, "'volume'")],
   19: [(2, '1.5')],
   22: [(1, '1'), (2, '2'), (3, "'growth'"), (4, '0')],
   25: [(1, '1'), (2, '3'), (3, "'division'"), (4, '0')],
   28: [(1, '1'), (2, '4'), (3, "'cellstate'"), (4, '0')],
   31: [(1, '1'), (2, '0'), (3, "'display'"), (4, '0')],
   32: [(1, "'position'")],
   33: [(1, "'mesh_id'"), (2, "'config'")],
   34: [(2, '1.0'), (4, '6')],
   '__in__': [],
   '__out__': []},
                             lazy=True,
                             )



