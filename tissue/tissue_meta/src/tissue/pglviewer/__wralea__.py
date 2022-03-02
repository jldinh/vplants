
# This file has been generated at Fri Dec 18 18:39:11 2009

from openalea.core import *


__name__ = 'tissue.pglviewer._tuto'

__editable__ = True
__description__ = ''
__license__ = ''
__url__ = ''
__alias__ = ['pglviewer._tuto']
__version__ = ''
__authors__ = ''
__institutes__ = ''
__icon__ = ''


__all__ = ['functions_function_move_scene', '_62157648', 'functions_function_generate_scene', '_62157520', '_76938576', '_62157584']



functions_function_move_scene = Factory(name='func move scene',
                description='',
                category='Unclassified',
                nodemodule='functions',
                nodeclass='function_move_scene',
                inputs=[{'interface': None, 'name': 'scene', 'value': None, 'desc': ''}],
                outputs=[{'interface': None, 'name': 'scene', 'desc': ''}],
                widgetmodule=None,
                widgetclass=None,
               )




_62157648 = CompositeNodeFactory(name='tuto1 launch viewer',
                             description='',
                             category='Unclassified',
                             doc='',
                             inputs=[],
                             outputs=[],
                             elt_factory={  2: ('pglviewer', 'viewer'),
   3: ('pglviewer.view', 'scene'),
   4: ('pglviewer.gui', 'viewergui'),
   5: ('pglviewer.gui', 'view3dgui'),
   6: ('pglviewer.gui', 'scgui'),
   7: ('pglviewer._tuto', 'func generate scene')},
                             elt_connections={  13648536: (3, 0, 2, 0),
   13648560: (6, 0, 2, 1),
   13648584: (7, 0, 3, 0),
   13648608: (4, 0, 2, 1),
   13648632: (5, 0, 2, 1),
   13648656: (3, 0, 6, 0)},
                             elt_data={  2: {  'block': False,
         'caption': 'viewer',
         'hide': True,
         'lazy': False,
         'port_hide_changed': set(),
         'posx': 317.5,
         'posy': 302.5,
         'priority': 0,
         'user_application': None},
   3: {  'block': False,
         'caption': 'scene',
         'hide': True,
         'lazy': True,
         'port_hide_changed': set(),
         'posx': 70.0,
         'posy': 82.5,
         'priority': 0,
         'user_application': None},
   4: {  'block': False,
         'caption': 'viewergui',
         'hide': True,
         'lazy': True,
         'port_hide_changed': set(),
         'posx': 240.0,
         'posy': 165.0,
         'priority': 0,
         'user_application': None},
   5: {  'block': False,
         'caption': 'view3dgui',
         'hide': True,
         'lazy': True,
         'port_hide_changed': set(),
         'posx': 341.25,
         'posy': 165.0,
         'priority': 0,
         'user_application': None},
   6: {  'block': False,
         'caption': 'scgui',
         'hide': True,
         'lazy': True,
         'port_hide_changed': set(),
         'posx': 441.25,
         'posy': 166.25,
         'priority': 0,
         'user_application': None},
   7: {  'block': False,
         'caption': 'func generate scene',
         'hide': True,
         'lazy': True,
         'port_hide_changed': set(),
         'posx': 22.5,
         'posy': -5.0,
         'priority': 0,
         'user_application': None},
   '__in__': {  'block': False,
                'caption': 'In',
                'hide': True,
                'lazy': True,
                'port_hide_changed': set(),
                'posx': 20.0,
                'posy': 5.0,
                'priority': 0,
                'user_application': None},
   '__out__': {  'block': False,
                 'caption': 'Out',
                 'hide': True,
                 'lazy': True,
                 'port_hide_changed': set(),
                 'posx': 20.0,
                 'posy': 250.0,
                 'priority': 0,
                 'user_application': None}},
                             elt_value={  2: [(2, 'False'), (3, 'None'), (4, "'Viewer'")],
   3: [],
   4: [],
   5: [],
   6: [],
   7: [],
   '__in__': [],
   '__out__': []},
                             lazy=True,
                             )




functions_function_generate_scene = Factory(name='func generate scene',
                description='',
                category='Unclassified',
                nodemodule='functions',
                nodeclass='function_generate_scene',
                inputs=[],
                outputs=[{'interface': None, 'name': 'scene', 'desc': ''}],
                widgetmodule=None,
                widgetclass=None,
               )




_62157520 = CompositeNodeFactory(name='tuto2 use loop',
                             description='',
                             category='Unclassified',
                             doc='',
                             inputs=[],
                             outputs=[],
                             elt_factory={  2: ('pglviewer', 'viewer'),
   3: ('pglviewer.view', 'scene'),
   4: ('openalea.flow control', 'annotation'),
   5: ('openalea.flow control', 'X'),
   6: ('openalea.scheduler', 'task'),
   7: ('pglviewer._tuto', 'func generate scene'),
   8: ('openalea.scheduler', 'scheduler'),
   9: ('pglviewer.view', 'loop'),
   10: ('openalea.flow control', 'rendez vous'),
   12: ('pglviewer.gui', 'loopgui'),
   13: ('openalea.flow control', 'annotation'),
   14: ('openalea.flow control', 'annotation'),
   15: ('openalea.flow control', 'annotation'),
   16: ('openalea.flow control', 'annotation'),
   17: ('pglviewer._tuto', 'func move scene')},
                             elt_connections={  13648440: (5, 0, 10, 1),
   13648464: (12, 0, 2, 1),
   13648488: (3, 0, 2, 0),
   13648512: (9, 0, 12, 0),
   13648536: (17, 0, 10, 0),
   13648560: (6, 0, 8, 0),
   13648584: (3, 0, 17, 0),
   13648608: (8, 0, 9, 0),
   13648632: (10, 0, 6, 0),
   13648656: (7, 0, 3, 0)},
                             elt_data={  2: {  'block': False,
         'caption': 'viewer',
         'hide': True,
         'lazy': False,
         'port_hide_changed': set(),
         'posx': 101.25,
         'posy': 575.0,
         'priority': 0,
         'user_application': None},
   3: {  'block': False,
         'caption': 'scene',
         'hide': True,
         'lazy': True,
         'port_hide_changed': set(),
         'posx': 80.0,
         'posy': 137.5,
         'priority': 0,
         'user_application': None},
   4: {  'posx': 190.0, 'posy': 85.0, 'txt': 'Generate a random scene'},
   5: {  'block': False,
         'caption': 'X0',
         'hide': True,
         'lazy': True,
         'port_hide_changed': set(),
         'posx': 605.0,
         'posy': 178.75,
         'priority': 0,
         'user_application': None},
   6: {  'block': False,
         'caption': 'task',
         'hide': True,
         'lazy': True,
         'port_hide_changed': set(),
         'posx': 536.25,
         'posy': 281.25,
         'priority': 0,
         'user_application': None},
   7: {  'block': False,
         'caption': 'func generate scene',
         'hide': True,
         'lazy': True,
         'port_hide_changed': set(),
         'posx': 32.5,
         'posy': 56.25,
         'priority': 0,
         'user_application': None},
   8: {  'block': False,
         'caption': 'scheduler',
         'hide': True,
         'lazy': True,
         'port_hide_changed': set(),
         'posx': 618.75,
         'posy': 372.5,
         'priority': 0,
         'user_application': None},
   9: {  'block': False,
         'caption': 'loop',
         'hide': True,
         'lazy': True,
         'port_hide_changed': set(),
         'posx': 635.0,
         'posy': 436.25,
         'priority': 0,
         'user_application': None},
   10: {  'block': False,
          'caption': 'rendez vous',
          'hide': True,
          'lazy': True,
          'port_hide_changed': set(),
          'posx': 541.25,
          'posy': 230.0,
          'priority': 0,
          'user_application': None},
   12: {  'block': False,
          'caption': 'loopgui',
          'hide': True,
          'lazy': True,
          'port_hide_changed': set(),
          'posx': 368.75,
          'posy': 488.75,
          'priority': 0,
          'user_application': None},
   13: {  'posx': 647.5,
          'posy': 116.25,
          'txt': 'Taks: move the global position of the scene'},
   14: {  'posx': 420.0,
          'posy': 536.25,
          'txt': 'Create a loop GUI to manage the loop\nfrom the viewer'},
   15: {  'posx': 98.75,
          'posy': 720.0,
          'txt': 'Usage:\n     1) evaluate the dataflow, a viewer must popup\n     2) use the different actions to drive the simulation'},
   16: {  'posx': 532.5, 'posy': 27.5, 'txt': 'Author: Jerome Chopard'},
   17: {  'block': False,
          'caption': 'func move scene',
          'hide': True,
          'lazy': False,
          'port_hide_changed': set(),
          'posx': 486.25,
          'posy': 108.75,
          'priority': 0,
          'user_application': None},
   '__in__': {  'block': False,
                'caption': 'In',
                'hide': True,
                'lazy': True,
                'port_hide_changed': set(),
                'posx': 20.0,
                'posy': 5.0,
                'priority': 0,
                'user_application': None},
   '__out__': {  'block': False,
                 'caption': 'Out',
                 'hide': True,
                 'lazy': True,
                 'port_hide_changed': set(),
                 'posx': 20.0,
                 'posy': 250.0,
                 'priority': 0,
                 'user_application': None}},
                             elt_value={  2: [(2, 'False'), (3, 'None'), (4, "'Viewer'")],
   3: [],
   4: [],
   5: [(0, "'x'")],
   6: [(1, '1'), (2, '0'), (3, "'move'"), (4, '0')],
   7: [],
   8: [],
   9: [],
   10: [],
   12: [],
   13: [],
   14: [],
   15: [],
   16: [],
   17: [],
   '__in__': [],
   '__out__': []},
                             lazy=True,
                             )




_76938576 = CompositeNodeFactory(name='tuto4 multi views',
                             description='',
                             category='Unclassified',
                             doc='',
                             inputs=[],
                             outputs=[],
                             elt_factory={  2: ('pglviewer', 'viewer'),
   3: ('pglviewer.view', 'scene'),
   4: ('pglviewer.gui', 'viewergui'),
   5: ('pglviewer.gui', 'view3dgui'),
   6: ('pglviewer.gui', 'scgui'),
   7: ('pglviewer._tuto', 'func generate scene'),
   8: ('pglviewer', 'viewer'),
   9: ('pglviewer.gui', 'scgui')},
                             elt_connections={  40387128: (9, 0, 8, 1),
   40387152: (8, 0, 2, 3),
   40387176: (3, 0, 9, 0),
   40387200: (3, 0, 8, 0),
   40387224: (3, 0, 2, 0),
   40387248: (5, 0, 2, 1),
   40387272: (6, 0, 2, 1),
   40387296: (7, 0, 3, 0),
   40387320: (3, 0, 6, 0),
   40387344: (4, 0, 2, 1)},
                             elt_data={  2: {  'block': False,
         'caption': 'viewer',
         'hide': True,
         'lazy': False,
         'port_hide_changed': set(),
         'posx': 317.5,
         'posy': 302.5,
         'priority': 0,
         'user_application': None},
   3: {  'block': False,
         'caption': 'scene',
         'hide': True,
         'lazy': True,
         'port_hide_changed': set(),
         'posx': 70.0,
         'posy': 82.5,
         'priority': 0,
         'user_application': None},
   4: {  'block': False,
         'caption': 'viewergui',
         'hide': True,
         'lazy': True,
         'port_hide_changed': set(),
         'posx': 240.0,
         'posy': 165.0,
         'priority': 0,
         'user_application': None},
   5: {  'block': False,
         'caption': 'view3dgui',
         'hide': True,
         'lazy': True,
         'port_hide_changed': set(),
         'posx': 341.25,
         'posy': 165.0,
         'priority': 0,
         'user_application': None},
   6: {  'block': False,
         'caption': 'scgui',
         'hide': True,
         'lazy': True,
         'port_hide_changed': set(),
         'posx': 441.25,
         'posy': 166.25,
         'priority': 0,
         'user_application': None},
   7: {  'block': False,
         'caption': 'func generate scene',
         'hide': True,
         'lazy': True,
         'port_hide_changed': set(),
         'posx': 22.5,
         'posy': -5.0,
         'priority': 0,
         'user_application': None},
   8: {  'block': False,
         'caption': 'viewer',
         'hide': True,
         'lazy': False,
         'port_hide_changed': set(),
         'posx': 512.5,
         'posy': 301.25,
         'priority': 0,
         'user_application': None},
   9: {  'block': False,
         'caption': 'scgui',
         'hide': True,
         'lazy': True,
         'port_hide_changed': set(),
         'posx': 576.25,
         'posy': 162.5,
         'priority': 0,
         'user_application': None},
   '__in__': {  'block': False,
                'caption': 'In',
                'hide': True,
                'lazy': True,
                'port_hide_changed': set(),
                'posx': 20.0,
                'posy': 5.0,
                'priority': 0,
                'user_application': None},
   '__out__': {  'block': False,
                 'caption': 'Out',
                 'hide': True,
                 'lazy': True,
                 'port_hide_changed': set(),
                 'posx': 20.0,
                 'posy': 250.0,
                 'priority': 0,
                 'user_application': None}},
                             elt_value={  2: [(2, 'False'), (4, "'Viewer'")],
   3: [],
   4: [],
   5: [],
   6: [],
   7: [],
   8: [(2, 'False'), (3, 'None'), (4, "'Viewer2'")],
   9: [],
   '__in__': [],
   '__out__': []},
                             lazy=True,
                             )




_62157584 = CompositeNodeFactory(name='tuto3 use probe',
                             description='',
                             category='Unclassified',
                             doc='',
                             inputs=[],
                             outputs=[],
                             elt_factory={  4: ('pglviewer.view', 'scene'),
   5: ('pglviewer', 'viewer'),
   6: ('pglviewer._tuto', 'func generate scene'),
   7: ('pglviewer', 'viewer'),
   8: ('pglviewer.gui', 'probegui'),
   9: ('pglviewer.view', 'probe'),
   10: ('pglviewer', 'viewer')},
                             elt_connections={  28713552: (6, 0, 4, 0),
   28713576: (9, 0, 8, 0),
   28713600: (9, 0, 5, 0),
   28713624: (9, 0, 10, 0),
   28713648: (4, 0, 7, 0),
   28713672: (4, 0, 9, 0),
   28713696: (8, 0, 10, 1),
   28713720: (5, 0, 10, 3),
   28713744: (7, 0, 10, 3)},
                             elt_data={  4: {  'block': False,
         'caption': 'scene',
         'hide': True,
         'lazy': True,
         'port_hide_changed': set(),
         'posx': 91.166666666666657,
         'posy': 106.25,
         'priority': 0,
         'user_application': None},
   5: {  'block': False,
         'caption': 'viewer',
         'hide': True,
         'lazy': False,
         'port_hide_changed': set(),
         'posx': 62.5,
         'posy': 363.75,
         'priority': 0,
         'user_application': None,
         'user_color': (255, 170, 0)},
   6: {  'block': False,
         'caption': 'func generate scene',
         'hide': True,
         'lazy': True,
         'port_hide_changed': set(),
         'posx': 37.166666666666657,
         'posy': 38.75,
         'priority': 0,
         'user_application': None},
   7: {  'block': False,
         'caption': 'viewer',
         'hide': True,
         'lazy': False,
         'port_hide_changed': set(),
         'posx': 381.25,
         'posy': 163.75,
         'priority': 0,
         'user_application': None,
         'user_color': (255, 170, 0)},
   8: {  'block': False,
         'caption': 'probegui',
         'hide': True,
         'lazy': True,
         'port_hide_changed': set(),
         'posx': 241.25,
         'posy': 235.0,
         'priority': 0,
         'user_application': None},
   9: {  'block': False,
         'caption': 'probe',
         'hide': True,
         'lazy': True,
         'port_hide_changed': set(),
         'posx': 91.666666666666657,
         'posy': 185.0,
         'priority': 0,
         'user_application': None},
   10: {  'block': False,
          'caption': 'viewer',
          'hide': True,
          'lazy': False,
          'port_hide_changed': set(),
          'posx': 238.97727272727275,
          'posy': 476.13636363636351,
          'priority': 0,
          'user_application': None,
          'user_color': (255, 170, 0)},
   '__in__': {  'block': False,
                'caption': 'In',
                'hide': True,
                'lazy': True,
                'port_hide_changed': set(),
                'posx': 20.0,
                'posy': 5.0,
                'priority': 0,
                'user_application': None},
   '__out__': {  'block': False,
                 'caption': 'Out',
                 'hide': True,
                 'lazy': True,
                 'port_hide_changed': set(),
                 'posx': 20.0,
                 'posy': 250.0,
                 'priority': 0,
                 'user_application': None}},
                             elt_value={  4: [],
   5: [(1, 'None'), (2, 'False'), (3, 'None'), (4, "'side'")],
   6: [],
   7: [(1, 'None'), (2, 'False'), (3, 'None'), (4, "'full view'")],
   8: [],
   9: [],
   10: [(2, 'False'), (4, "'Viewer'")],
   '__in__': [],
   '__out__': []},
                             lazy=True,
                             )



