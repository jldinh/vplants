
# This file has been generated at Wed Aug  3 17:38:43 2011

from openalea.core import *


__name__ = 'vplants.mars_alt.demo.analysis'

__editable__ = True
__description__ = 'mars_alt nodes'
__license__ = 'CECILL-C'
__url__ = 'http://openalea.gforge.inria.fr/doc/openalea/pylab/doc/_build/html/contents.html'
__alias__ = []
__version__ = '0.8.0'
__authors__ = 'Eric Moscardi'
__institutes__ = 'INRIA/CIRAD'
__icon__ = 'logo.png'


__all__ = ['_189816012', 'analysis']



_189816012 = CompositeNodeFactory(name='extract_L1',
                             description='',
                             category='image processing',
                             doc='',
                             inputs=[],
                             outputs=[],
                             elt_factory={  2: ('openalea.image.serial', 'imread'),
   4: ('vplants.mars_alt.data', 'segmentation.inr.gz'),
   5: ('vplants.mars_alt.nodes.analysis', 'extract_L1')},
                             elt_connections={  154218660: (2, 0, 5, 0), 154218684: (4, 0, 2, 0)},
                             elt_data={  2: {  'block': False,
         'caption': 'imread',
         'delay': 0,
         'factory': '<openalea.core.node.NodeFactory object at 0xb0f6e8c> : "imread"',
         'hide': True,
         'id': 2,
         'lazy': True,
         'port_hide_changed': set(),
         'posx': -299.96498541058764,
         'posy': -127.00750312630262,
         'priority': 0,
         'use_user_color': False,
         'user_application': None,
         'user_color': None},
   4: {  'block': False,
         'caption': 'segmentation.inr.gz',
         'delay': 0,
         'factory': '<openalea.core.data.DataFactory object at 0xb3bc2ec> : "segmentation.inr.gz"',
         'hide': True,
         'id': 4,
         'lazy': True,
         'port_hide_changed': set([2]),
         'posx': -344.4149354902893,
         'posy': -168.69679338667618,
         'priority': 0,
         'use_user_color': False,
         'user_application': None,
         'user_color': None},
   5: {  'block': False,
         'caption': 'extract_L1',
         'delay': 0,
         'factory': '<openalea.core.node.NodeFactory object at 0xf426f2c> : "extract_L1"',
         'hide': True,
         'id': 5,
         'lazy': True,
         'port_hide_changed': set(),
         'posx': -311.0,
         'posy': -60.0,
         'priority': 0,
         'use_user_color': False,
         'user_application': None,
         'user_color': None},
   '__in__': {  'block': False,
                'caption': 'In',
                'delay': 0,
                'hide': True,
                'id': 0,
                'lazy': True,
                'port_hide_changed': set(),
                'posx': 0,
                'posy': 0,
                'priority': 0,
                'use_user_color': True,
                'user_application': None,
                'user_color': None},
   '__out__': {  'block': False,
                 'caption': 'Out',
                 'delay': 0,
                 'hide': True,
                 'id': 1,
                 'lazy': True,
                 'port_hide_changed': set(),
                 'posx': 0,
                 'posy': 0,
                 'priority': 0,
                 'use_user_color': True,
                 'user_application': None,
                 'user_color': None}},
                             elt_value={  2: [],
   4: [  (0, 'PackageData(vplants.mars_alt.data, segmentation.inr.gz)'),
         (1, 'None'),
         (2, 'None')],
   5: [],
   '__in__': [],
   '__out__': []},
                             elt_ad_hoc={  2: {'position': [-299.96498541058764, -127.00750312630262], 'userColor': None, 'useUserColor': False},
   3: {  'position': [-311.1296373488954, -66.02751146310963],
         'useUserColor': False,
         'userColor': None},
   4: {'position': [-344.4149354902893, -168.69679338667618], 'userColor': None, 'useUserColor': False},
   5: {'position': [-311.0, -60.0], 'userColor': None, 'useUserColor': False},
   '__in__': {'position': [0, 0], 'userColor': None, 'useUserColor': True},
   '__out__': {'position': [0, 0], 'userColor': None, 'useUserColor': True}},
                             lazy=True,
                             eval_algo='LambdaEvaluation',
                             )




analysis = CompositeNodeFactory(name='analysis',
                             description='',
                             category='image processing',
                             doc='',
                             inputs=[],
                             outputs=[],
                             elt_factory={  2: ('vplants.mars_alt.nodes.analysis', 'nlabels'),
   3: ('openalea.image.serial', 'imread'),
   4: ('openalea.image.gui', 'display'),
   6: ('openalea.data structure', 'int'),
   8: ('openalea.data structure', 'bool'),
   10: ('vplants.mars_alt.nodes.analysis', 'center_of_mass'),
   11: ('openalea.data structure.list', 'list'),
   12: ('openalea.data structure', 'int'),
   13: ('openalea.data structure', 'int'),
   15: ('openalea.data structure', 'bool'),
   17: ('openalea.data structure', 'int'),
   19: ('openalea.data structure', 'int'),
   20: ('openalea.data structure', 'int'),
   21: ('vplants.mars_alt.data', 'segmentation.inr.gz'),
   22: ('vplants.mars_alt.nodes.analysis', 'center_of_mass'),
   23: ('vplants.mars_alt.nodes.analysis', 'volume'),
   24: ('vplants.mars_alt.nodes.analysis', 'volume'),
   25: ('vplants.mars_alt.nodes.analysis', 'neighbors'),
   26: ('vplants.mars_alt.nodes.analysis', 'contact_surface')},
                             elt_connections={  154218276: (8, 0, 22, 2),
   154218288: (6, 0, 22, 1),
   154218300: (11, 0, 23, 1),
   154218312: (11, 0, 24, 1),
   154218324: (15, 0, 24, 2),
   154218336: (3, 0, 25, 0),
   154218348: (20, 0, 26, 2),
   154218360: (19, 0, 26, 1),
   154218372: (3, 0, 26, 0),
   154218384: (17, 0, 25, 1),
   154218396: (3, 0, 24, 0),
   154218408: (3, 0, 23, 0),
   154218420: (3, 0, 22, 0),
   154218432: (3, 0, 10, 0),
   154218444: (3, 0, 2, 0),
   154218456: (6, 0, 10, 1),
   154218504: (13, 0, 11, 0),
   154218564: (12, 0, 11, 0),
   154218588: (21, 0, 3, 0),
   154218600: (3, 0, 4, 0)},
                             elt_data={  2: {  'block': False,
         'caption': 'nlabels',
         'delay': 0,
         'factory': '<openalea.core.node.NodeFactory object at 0xf43406c> : "nlabels"',
         'hide': True,
         'id': 2,
         'lazy': True,
         'port_hide_changed': set(),
         'posx': -54.00119372869072,
         'posy': -139.57231609876987,
         'priority': 0,
         'use_user_color': False,
         'user_application': None,
         'user_color': None},
   3: {  'block': False,
         'caption': 'imread',
         'delay': 0,
         'factory': '<openalea.core.node.NodeFactory object at 0xb0f6e8c> : "imread"',
         'hide': True,
         'id': 3,
         'lazy': True,
         'port_hide_changed': set(),
         'posx': -119.0,
         'posy': -185.5,
         'priority': 0,
         'use_user_color': False,
         'user_application': None,
         'user_color': None},
   4: {  'block': False,
         'caption': 'display',
         'delay': 0,
         'factory': '<openalea.core.node.NodeFactory object at 0xb19b0ec> : "display"',
         'hide': True,
         'id': 4,
         'lazy': True,
         'port_hide_changed': set(),
         'posx': -184.0,
         'posy': -140.25,
         'priority': 0,
         'use_user_color': False,
         'user_application': None,
         'user_color': None},
   6: {  'block': False,
         'caption': '265',
         'delay': 0,
         'factory': '<openalea.core.node.NodeFactory object at 0xb738e2c> : "int"',
         'hide': True,
         'id': 6,
         'lazy': True,
         'port_hide_changed': set(),
         'posx': -415.0,
         'posy': 32.42857142857142,
         'priority': 0,
         'use_user_color': False,
         'user_application': None,
         'user_color': None},
   8: {  'block': False,
         'caption': 'False',
         'delay': 0,
         'factory': '<openalea.core.node.NodeFactory object at 0xb738c4c> : "bool"',
         'hide': True,
         'id': 8,
         'lazy': True,
         'port_hide_changed': set(),
         'posx': -352.06229142886644,
         'posy': 31.597783832745414,
         'priority': 0,
         'use_user_color': False,
         'user_application': None,
         'user_color': None},
   10: {  'block': False,
          'caption': 'center_of_mass',
          'delay': 0,
          'factory': '<openalea.core.node.NodeFactory object at 0xf43402c> : "center_of_mass"',
          'hide': True,
          'id': 10,
          'lazy': True,
          'port_hide_changed': set(),
          'posx': -544.1658752660373,
          'posy': 147.04940446120398,
          'priority': 0,
          'use_user_color': False,
          'user_application': None,
          'user_color': None},
   11: {  'block': False,
          'caption': 'list',
          'delay': 0,
          'factory': '<openalea.core.node.NodeFactory object at 0xaf0320c> : "list"',
          'hide': True,
          'id': 11,
          'lazy': True,
          'port_hide_changed': set(),
          'posx': -178.39952250852372,
          'posy': 68.9832256449159,
          'priority': 0,
          'use_user_color': False,
          'user_application': None,
          'user_color': None},
   12: {  'block': False,
          'caption': '265',
          'delay': 0,
          'factory': '<openalea.core.node.NodeFactory object at 0xb738e2c> : "int"',
          'hide': True,
          'id': 12,
          'lazy': True,
          'port_hide_changed': set(),
          'posx': -197.84606202086994,
          'posy': 23.54701700382252,
          'priority': 0,
          'use_user_color': False,
          'user_application': None,
          'user_color': None},
   13: {  'block': False,
          'caption': '266',
          'delay': 0,
          'factory': '<openalea.core.node.NodeFactory object at 0xb738e2c> : "int"',
          'hide': True,
          'id': 13,
          'lazy': True,
          'port_hide_changed': set(),
          'posx': -156.15393797913006,
          'posy': 20.22386662051848,
          'priority': 0,
          'use_user_color': False,
          'user_application': None,
          'user_color': None},
   15: {  'block': False,
          'caption': 'False',
          'delay': 0,
          'factory': '<openalea.core.node.NodeFactory object at 0xb738c4c> : "bool"',
          'hide': True,
          'id': 15,
          'lazy': True,
          'port_hide_changed': set(),
          'posx': -80.0,
          'posy': 32.42857142857142,
          'priority': 0,
          'use_user_color': False,
          'user_application': None,
          'user_color': None},
   17: {  'block': False,
          'caption': '265',
          'delay': 0,
          'factory': '<openalea.core.node.NodeFactory object at 0xb738e2c> : "int"',
          'hide': True,
          'id': 17,
          'lazy': True,
          'port_hide_changed': set(),
          'posx': 34.0,
          'posy': 32.42857142857142,
          'priority': 0,
          'use_user_color': False,
          'user_application': None,
          'user_color': None},
   19: {  'block': False,
          'caption': '265',
          'delay': 0,
          'factory': '<openalea.core.node.NodeFactory object at 0xb738e2c> : "int"',
          'hide': True,
          'id': 19,
          'lazy': True,
          'port_hide_changed': set(),
          'posx': 161.0,
          'posy': 32.42857142857142,
          'priority': 0,
          'use_user_color': False,
          'user_application': None,
          'user_color': None},
   20: {  'block': False,
          'caption': '1',
          'delay': 0,
          'factory': '<openalea.core.node.NodeFactory object at 0xb738e2c> : "int"',
          'hide': True,
          'id': 20,
          'lazy': True,
          'port_hide_changed': set(),
          'posx': 209.0,
          'posy': 32.42857142857142,
          'priority': 0,
          'use_user_color': False,
          'user_application': None,
          'user_color': None},
   21: {  'block': False,
          'caption': 'segmentation.inr.gz',
          'delay': 0,
          'factory': '<openalea.core.data.DataFactory object at 0xb3bc2ec> : "segmentation.inr.gz"',
          'hide': True,
          'id': 21,
          'lazy': True,
          'port_hide_changed': set([2]),
          'posx': -152.84173656290378,
          'posy': -241.44346501615166,
          'priority': 0,
          'use_user_color': False,
          'user_application': None,
          'user_color': None},
   22: {  'block': False,
          'caption': 'center_of_mass',
          'delay': 0,
          'factory': '<openalea.core.node.NodeFactory object at 0xf43402c> : "center_of_mass"',
          'hide': True,
          'id': 22,
          'lazy': True,
          'port_hide_changed': set(),
          'posx': -388.97217497220595,
          'posy': 147.04940446120398,
          'priority': 0,
          'use_user_color': False,
          'user_application': None,
          'user_color': None},
   23: {  'block': False,
          'caption': 'volume',
          'delay': 0,
          'factory': '<openalea.core.node.NodeFactory object at 0xf426f4c> : "volume"',
          'hide': True,
          'id': 23,
          'lazy': True,
          'port_hide_changed': set(),
          'posx': -233.77847467837455,
          'posy': 147.04940446120398,
          'priority': 0,
          'use_user_color': False,
          'user_application': None,
          'user_color': None},
   24: {  'block': False,
          'caption': 'volume',
          'delay': 0,
          'factory': '<openalea.core.node.NodeFactory object at 0xf426f4c> : "volume"',
          'hide': True,
          'id': 24,
          'lazy': True,
          'port_hide_changed': set(),
          'posx': -120.58477438454315,
          'posy': 147.04940446120398,
          'priority': 0,
          'use_user_color': False,
          'user_application': None,
          'user_color': None},
   25: {  'block': False,
          'caption': 'neighbors',
          'delay': 0,
          'factory': '<openalea.core.node.NodeFactory object at 0xee092cc> : "neighbors"',
          'hide': True,
          'id': 25,
          'lazy': True,
          'port_hide_changed': set(),
          'posx': 0.0,
          'posy': 149.541767248682,
          'priority': 0,
          'use_user_color': False,
          'user_application': None,
          'user_color': None},
   26: {  'block': False,
          'caption': 'contact_surface',
          'delay': 0,
          'factory': '<openalea.core.node.NodeFactory object at 0xf426fec> : "contact_surface"',
          'hide': True,
          'id': 26,
          'lazy': True,
          'port_hide_changed': set(),
          'posx': 118.8026262031196,
          'posy': 147.04940446120398,
          'priority': 0,
          'use_user_color': False,
          'user_application': None,
          'user_color': None},
   '__in__': {  'block': False,
                'caption': 'In',
                'delay': 0,
                'hide': True,
                'id': 0,
                'lazy': True,
                'port_hide_changed': set(),
                'posx': 0,
                'posy': 0,
                'priority': 0,
                'use_user_color': True,
                'user_application': None,
                'user_color': None},
   '__out__': {  'block': False,
                 'caption': 'Out',
                 'delay': 0,
                 'hide': True,
                 'id': 1,
                 'lazy': True,
                 'port_hide_changed': set(),
                 'posx': 0,
                 'posy': 0,
                 'priority': 0,
                 'use_user_color': True,
                 'user_application': None,
                 'user_color': None}},
                             elt_value={  2: [],
   3: [],
   4: [(1, "'grayscale'"), (2, 'None'), (3, 'None')],
   6: [(0, '265')],
   8: [(0, 'False')],
   10: [(2, 'True')],
   11: [],
   12: [(0, '265')],
   13: [(0, '266')],
   15: [(0, 'False')],
   17: [(0, '265')],
   19: [(0, '265')],
   20: [(0, '1')],
   21: [  (0, 'PackageData(vplants.mars_alt.data, segmentation.inr.gz)'),
          (1, 'None'),
          (2, 'None')],
   22: [],
   23: [(2, 'True')],
   24: [],
   25: [],
   26: [],
   '__in__': [],
   '__out__': []},
                             elt_ad_hoc={  2: {'position': [-54.00119372869072, -139.57231609876987], 'userColor': None, 'useUserColor': False},
   3: {'position': [-119.0, -185.5], 'userColor': None, 'useUserColor': False},
   4: {'position': [-184.0, -140.25], 'userColor': None, 'useUserColor': False},
   5: {  'position': [-519.0, 93.5], 'useUserColor': False, 'userColor': None},
   6: {'position': [-415.0, 32.42857142857142], 'userColor': None, 'useUserColor': False},
   7: {  'position': [-392.0, 93.5], 'useUserColor': False, 'userColor': None},
   8: {'position': [-352.06229142886644, 31.597783832745414], 'userColor': None, 'useUserColor': False},
   9: {  'position': [-253.0, 93.5], 'useUserColor': False, 'userColor': None},
   10: {'position': [-544.1658752660373, 147.04940446120398], 'userColor': None, 'useUserColor': False},
   11: {'position': [-178.39952250852372, 68.9832256449159], 'userColor': None, 'useUserColor': False},
   12: {'position': [-197.84606202086994, 23.54701700382252], 'userColor': None, 'useUserColor': False},
   13: {'position': [-156.15393797913006, 20.22386662051848], 'userColor': None, 'useUserColor': False},
   14: {  'position': [-113.0, 93.5], 'useUserColor': False, 'userColor': None},
   15: {'position': [-80.0, 32.42857142857142], 'userColor': None, 'useUserColor': False},
   16: {  'position': [-11.0, 93.5], 'useUserColor': False, 'userColor': None},
   17: {'position': [34.0, 32.42857142857142], 'userColor': None, 'useUserColor': False},
   18: {  'position': [115.0, 93.5], 'useUserColor': False, 'userColor': None},
   19: {'position': [161.0, 32.42857142857142], 'userColor': None, 'useUserColor': False},
   20: {'position': [209.0, 32.42857142857142], 'userColor': None, 'useUserColor': False},
   21: {'position': [-152.84173656290378, -241.44346501615166], 'userColor': None, 'useUserColor': False},
   22: {'position': [-388.97217497220595, 147.04940446120398], 'userColor': None, 'useUserColor': False},
   23: {'position': [-233.77847467837455, 147.04940446120398], 'userColor': None, 'useUserColor': False},
   24: {'position': [-120.58477438454315, 147.04940446120398], 'userColor': None, 'useUserColor': False},
   25: {'position': [0.0, 149.541767248682], 'userColor': None, 'useUserColor': False},
   26: {'position': [118.8026262031196, 147.04940446120398], 'userColor': None, 'useUserColor': False},
   '__in__': {'position': [0, 0], 'userColor': None, 'useUserColor': True},
   '__out__': {'position': [0, 0], 'userColor': None, 'useUserColor': True}},
                             lazy=True,
                             eval_algo='LambdaEvaluation',
                             )



