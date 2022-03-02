
# This file has been generated at Wed Aug  3 18:14:56 2011

from openalea.core import *


__name__ = 'vplants.mars_alt.demo.structural_analysis'

__editable__ = True
__description__ = 'vtissue nodes'
__license__ = 'CECILL-C'
__url__ = 'http://openalea.gforge.inria.fr/doc/openalea/pylab/doc/_build/html/contents.html'
__alias__ = []
__version__ = '0.8.0'
__authors__ = 'Eric Moscardi'
__institutes__ = 'INRIA/CIRAD'
__icon__ = 'logo.png'


__all__ = ['_178167500', '_178166828']



_178167500 = CompositeNodeFactory(name='draw_walls',
                             description='',
                             category='image processing',
                             doc='',
                             inputs=[],
                             outputs=[],
                             elt_factory={  2: ('openalea.image.serial', 'imread'),
   3: ('openalea.image.algo', 'reverse_image'),
   4: ('openalea.image.gui', 'display'),
   6: ('openalea.image.gui', 'display'),
   7: ('vplants.mars_alt.data', 'segmentation.inr.gz'),
   8: ('vplants.mars_alt.nodes.analysis', 'draw_walls')},
                             elt_connections={  154218600: (2, 0, 8, 0),
   154218612: (8, 0, 3, 0),
   154218624: (8, 0, 6, 0),
   154218636: (3, 0, 4, 0),
   154218684: (7, 0, 2, 0)},
                             elt_data={  2: {  'block': False,
         'caption': 'imread',
         'delay': 0,
         'factory': '<openalea.core.node.NodeFactory object at 0xb0f6e8c> : "imread"',
         'hide': True,
         'id': 2,
         'lazy': True,
         'port_hide_changed': set(),
         'posx': -211.0,
         'posy': -129.0,
         'priority': 0,
         'use_user_color': False,
         'user_application': None,
         'user_color': None},
   3: {  'block': False,
         'caption': 'reverse_image',
         'delay': 0,
         'factory': '<openalea.core.node.NodeFactory object at 0xa9ee82c> : "reverse_image"',
         'hide': True,
         'id': 3,
         'lazy': True,
         'port_hide_changed': set(),
         'posx': -137.0,
         'posy': -19.0,
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
         'posx': -99.0,
         'posy': 38.0,
         'priority': 0,
         'use_user_color': False,
         'user_application': None,
         'user_color': None},
   6: {  'block': False,
         'caption': 'display',
         'delay': 0,
         'factory': '<openalea.core.node.NodeFactory object at 0xb19b0ec> : "display"',
         'hide': True,
         'id': 6,
         'lazy': True,
         'port_hide_changed': set(),
         'posx': -187.0,
         'posy': 38.0,
         'priority': 0,
         'use_user_color': False,
         'user_application': None,
         'user_color': None},
   7: {  'block': False,
         'caption': 'segmentation.inr.gz',
         'delay': 0,
         'factory': '<openalea.core.data.DataFactory object at 0xb3bc2ec> : "segmentation.inr.gz"',
         'hide': True,
         'id': 7,
         'lazy': True,
         'port_hide_changed': set([2]),
         'posx': -254.7963185759655,
         'posy': -171.03473350322122,
         'priority': 0,
         'use_user_color': False,
         'user_application': None,
         'user_color': None},
   8: {  'block': False,
         'caption': 'draw_walls',
         'delay': 0,
         'factory': '<openalea.core.node.NodeFactory object at 0xf43412c> : "draw_walls"',
         'hide': True,
         'id': 8,
         'lazy': True,
         'port_hide_changed': set(),
         'posx': -212.0,
         'posy': -69.0,
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
   6: [(1, "'grayscale'"), (2, 'None'), (3, 'None')],
   7: [  (0, 'PackageData(vplants.mars_alt.data, segmentation.inr.gz)'),
         (1, 'None'),
         (2, 'None')],
   8: [(1, 'False')],
   '__in__': [],
   '__out__': []},
                             elt_ad_hoc={  2: {'position': [-211.0, -129.0], 'userColor': None, 'useUserColor': False},
   3: {'position': [-137.0, -19.0], 'userColor': None, 'useUserColor': False},
   4: {'position': [-99.0, 38.0], 'userColor': None, 'useUserColor': False},
   5: {  'position': [-215.0, -78.0], 'useUserColor': False, 'userColor': None},
   6: {'position': [-187.0, 38.0], 'userColor': None, 'useUserColor': False},
   7: {'position': [-254.7963185759655, -171.03473350322122], 'userColor': None, 'useUserColor': False},
   8: {'position': [-212.0, -69.0], 'userColor': None, 'useUserColor': False},
   '__in__': {'position': [0, 0], 'userColor': None, 'useUserColor': True},
   '__out__': {'position': [0, 0], 'userColor': None, 'useUserColor': True}},
                             lazy=True,
                             eval_algo='LambdaEvaluation',
                             )




_178166828 = CompositeNodeFactory(name='draw_L1',
                             description='',
                             category='image processing',
                             doc='',
                             inputs=[],
                             outputs=[],
                             elt_factory={  2: ('openalea.image.serial', 'imread'),
   4: ('openalea.image.gui', 'display'),
   5: ('vplants.mars_alt.data', 'segmentation.inr.gz'),
   6: ('vplants.mars_alt.nodes.analysis', 'draw_L1')},
                             elt_connections={  154218636: (2, 0, 6, 0), 154218648: (6, 0, 4, 0), 154218684: (5, 0, 2, 0)},
                             elt_data={  2: {  'block': False,
         'caption': 'imread',
         'delay': 0,
         'factory': '<openalea.core.node.NodeFactory object at 0xb0f6e8c> : "imread"',
         'hide': True,
         'id': 2,
         'lazy': True,
         'port_hide_changed': set(),
         'posx': -282.0,
         'posy': -134.0,
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
         'posx': -267.0,
         'posy': -31.0,
         'priority': 0,
         'use_user_color': False,
         'user_application': None,
         'user_color': None},
   5: {  'block': False,
         'caption': 'segmentation.inr.gz',
         'delay': 0,
         'factory': '<openalea.core.data.DataFactory object at 0xb3bc2ec> : "segmentation.inr.gz"',
         'hide': True,
         'id': 5,
         'lazy': True,
         'port_hide_changed': set([2]),
         'posx': -326.8391090959673,
         'posy': -166.71124887394018,
         'priority': 0,
         'use_user_color': False,
         'user_application': None,
         'user_color': None},
   6: {  'block': False,
         'caption': 'draw_L1',
         'delay': 0,
         'factory': '<openalea.core.node.NodeFactory object at 0xf4340cc> : "draw_L1"',
         'hide': True,
         'id': 6,
         'lazy': True,
         'port_hide_changed': set(),
         'posx': -290.0,
         'posy': -86.0,
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
   4: [(1, "'grayscale'"), (2, 'None'), (3, 'None')],
   5: [  (0, 'PackageData(vplants.mars_alt.data, segmentation.inr.gz)'),
         (1, 'None'),
         (2, 'None')],
   6: [],
   '__in__': [],
   '__out__': []},
                             elt_ad_hoc={  2: {'position': [-282.0, -134.0], 'userColor': None, 'useUserColor': False},
   3: {  'position': [-286.0, -84.0], 'useUserColor': False, 'userColor': None},
   4: {'position': [-267.0, -31.0], 'userColor': None, 'useUserColor': False},
   5: {'position': [-326.8391090959673, -166.71124887394018], 'userColor': None, 'useUserColor': False},
   6: {'position': [-290.0, -86.0], 'userColor': None, 'useUserColor': False},
   '__in__': {'position': [0, 0], 'userColor': None, 'useUserColor': True},
   '__out__': {'position': [0, 0], 'userColor': None, 'useUserColor': True}},
                             lazy=True,
                             eval_algo='LambdaEvaluation',
                             )




