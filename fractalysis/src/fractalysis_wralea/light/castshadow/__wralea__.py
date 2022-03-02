
# This file has been generated at Fri Jul  4 09:33:37 2008

from openalea.core import *


__name__ = 'Demo.Light'

__editable__ = True
__version__ = '0.1'
__description__ = 'Multi-scale light interception demo'
__license__ = 'CeCIL'
__authors__ = 'DDS'
__url__ = ''
__institutes__ = 'VirtualPlants'
__icon__ = 'castshadow_icon.png'
 

__all__ = ['_147407180', 'MuSLIM', 'scalesTable']


_147407180 = DataFactory(name='mango_f21_L.bgeom', 
                    description='Mango f21', 
                    editors=None,
                    includes=None,
                    )



MuSLIM = CompositeNodeFactory(name='MuSLIM', 
                             description='Generates MuSLIM images', 
                             category='demo',
                             doc='',
                             inputs=[],
                             outputs=[],
                             elt_factory={  2: ('catalog.pickle', 'pickle load'),
   3: ('Demo.Light', 'scalesTable'),
   4: ('Geometric Operator', 'import scene'),
   5: ('PlantGL.Objects', 'Scene'),
   6: ('fractalysis.light', 'create MSS'),
   7: ('catalog.data', 'string'),
   8: ('fractalysis.light', 'Light interception'),
   9: ('system', 'annotation'),
   10: ('fractalysis.light', 'Light direction'),
   14: ('PlantGL.Visualization', 'plot3D'),
   15: ('system', 'annotation'),
   16: ('system', 'annotation'),
   17: ('system', 'annotation'),
   18: ('system', 'annotation'),
   19: ('system', 'annotation'),
   20: ('Demo.Light', 'mango_f21_L.bgeom'),
   21: ('system', 'annotation'),
   24: ('catalog.functional', 'map'),
   25: ('catalog.file', 'packagedir'),
   26: ('catalog.data', 'list'),
   27: ('system', 'annotation'),
   28: ('image.basics', 'view image'),
   29: ('system', 'X'),
   30: ('system', 'annotation'),
   31: ('system', 'annotation'),
   32: ('system', 'annotation')},
                             elt_connections={  135712512: (20, 0, 4, 0),
   135712524: (8, 2, 28, 0),
   135712536: (2, 0, 6, 2),
   135712548: (28, 0, 24, 0),
   135712560: (5, 0, 14, 0),
   135712572: (4, 0, 5, 0),
   135712584: (29, 0, 8, 1),
   135712596: (25, 0, 8, 4),
   135712608: (5, 0, 6, 1),
   135712620: (7, 0, 6, 0),
   135712632: (26, 0, 8, 2),
   135712644: (6, 0, 8, 0),
   135712656: (3, 0, 2, 0),
   135712668: (10, 0, 24, 1)},
                             elt_data={  2: {  'caption': 'pickle load',
         'hide': True,
         'lazy': False,
         'minimal': False,
         'port_hide_changed': set([]),
         'posx': 583.75,
         'posy': 311.25,
         'priority': 0,
         'user_application': None},
   3: {  'caption': 'scalesTable',
         'hide': True,
         'lazy': True,
         'port_hide_changed': set([2]),
         'posx': 585.0,
         'posy': 240.0,
         'priority': 0,
         'user_application': None},
   4: {  'caption': 'import scene',
         'hide': True,
         'lazy': True,
         'minimal': False,
         'port_hide_changed': set([]),
         'posx': 283.75,
         'posy': 220.0,
         'priority': 0,
         'user_application': None},
   5: {  'caption': 'Scene',
         'hide': True,
         'lazy': False,
         'minimal': False,
         'port_hide_changed': set([]),
         'posx': 318.75,
         'posy': 283.75,
         'priority': 0,
         'user_application': None},
   6: {  'caption': 'create MSS',
         'hide': True,
         'lazy': True,
         'minimal': False,
         'port_hide_changed': set([]),
         'posx': 358.75,
         'posy': 543.75,
         'priority': 0,
         'user_application': None},
   7: {  'caption': "'mango_f21'",
         'hide': True,
         'lazy': True,
         'minimal': False,
         'port_hide_changed': set([]),
         'posx': 211.25,
         'posy': 490.0,
         'priority': 0,
         'user_application': None},
   8: {  'caption': 'Light interception',
         'hide': True,
         'lazy': True,
         'port_hide_changed': set([]),
         'posx': 453.75,
         'posy': 666.25,
         'priority': 0,
         'user_application': None},
   9: {  'posx': 955.54895222181813,
         'posy': 86.72483960450279,
         'txt': 'Team : Virtual Plants'},
   10: {  'caption': 'Light direction',
          'hide': True,
          'lazy': True,
          'port_hide_changed': set([]),
          'posx': 715.0,
          'posy': 765.0,
          'priority': 0,
          'user_application': None},
   14: {  'caption': 'plot3D',
          'hide': True,
          'lazy': False,
          'minimal': False,
          'port_hide_changed': set([]),
          'posx': 190.0,
          'posy': 336.25,
          'priority': 0,
          'user_application': None},
   15: {'posx': -8.741639333367857, 'posy': 233.39966151849652, 'txt': ''},
   16: {  'posx': 703.75,
          'posy': 630.0,
          'txt': 'Computing light interception, \ngenerating image and saving data'},
   17: {  'posx': 686.25,
          'posy': 358.75,
          'txt': 'Reading multiscale\ndecomposition'},
   18: {  'posx': 55.0,
          'posy': 455.0,
          'txt': 'Generating multiscale\nstructure'},
   19: {  'posx': 11.25,
          'posy': 286.25,
          'txt': 'Loading and viewing \n3D mockup'},
   20: {  'caption': 'mango_f21_L.bgeom',
          'hide': True,
          'lazy': True,
          'port_hide_changed': set([2]),
          'posx': 237.5,
          'posy': 152.5,
          'priority': 0,
          'user_application': None},
   21: {'posx': 332.5, 'posy': 778.75, 'txt': 'Image viewer'},
   24: {  'caption': 'map',
          'hide': True,
          'lazy': True,
          'port_hide_changed': set([]),
          'posx': 647.5,
          'posy': 903.75,
          'priority': 0,
          'user_application': None},
   25: {  'caption': 'packagedir',
          'hide': True,
          'lazy': True,
          'port_hide_changed': set([]),
          'posx': 651.25,
          'posy': 560.0,
          'priority': 0,
          'user_application': None},
   26: {  'caption': 'list',
          'hide': True,
          'lazy': True,
          'port_hide_changed': set([]),
          'posx': 596.25,
          'posy': 506.25,
          'priority': 0,
          'user_application': None},
   27: {'posx': 405.0, 'posy': 18.75, 'txt': 'Multiscale Light Interception'},
   28: {  'caption': 'view image',
          'hide': True,
          'lazy': True,
          'port_hide_changed': set([]),
          'posx': 533.75,
          'posy': 773.75,
          'priority': 0,
          'user_application': None},
   29: {  'caption': 'X0',
          'hide': True,
          'lazy': True,
          'port_hide_changed': set([]),
          'posx': 495.0,
          'posy': 588.75,
          'priority': 0,
          'user_application': None},
   30: {  'posx': 956.70838864296263,
          'posy': 58.500330973657981,
          'txt': 'Authors : Da SILVA D.'},
   31: {  'posx': 958.84613432754031,
          'posy': 28.935258763957677,
          'txt': 'Packages : Fractalysis, plantGL, image'},
   32: {  'posx': 957.86782506410691,
          'posy': 117.17765749878068,
          'txt': 'Credits : \n    digitized tree : INRA - UMR Piaf\n    BOUDON Frederic\n'},
   '__in__': {  'caption': 'In',
                'hide': True,
                'lazy': True,
                'minimal': False,
                'port_hide_changed': set([]),
                'posx': 20.0,
                'posy': 5.0,
                'priority': 0},
   '__out__': {  'caption': 'Out',
                 'hide': True,
                 'lazy': True,
                 'minimal': False,
                 'port_hide_changed': set([]),
                 'posx': 20.0,
                 'posy': 250.0,
                 'priority': 0}},
                             elt_value={  2: [],
   3: [(0, 'PackageData(Demo.Light, scalesTable)'), (1, 'None'), (2, 'None')],
   4: [],
   5: [],
   6: [(3, "'Cvx Hull'")],
   7: [(0, "'mango_f21'")],
   8: [(3, "'150x150'")],
   9: [],
   10: [  (0, 'True'),
          (1, '43.3643'),
          (2, '3.5238'),
          (3, '172'),
          (4, '17.0'),
          (5, '18.0'),
          (6, '60'),
          (7, 'False'),
          (8, '1'),
          (9, '0')],
   14: [],
   15: [],
   16: [],
   17: [],
   18: [],
   19: [],
   20: [  (0, 'PackageData(Demo.Light, mango_f21_L.bgeom)'),
          (1, 'None'),
          (2, 'None')],
   21: [],
   24: [],
   25: [(0, "'Demo.Light'")],
   26: [(0, "['A', 'A', 'R']")],
   27: [],
   28: [],
   29: [(0, "'x'")],
   30: [],
   31: [],
   32: [],
   '__in__': [],
   '__out__': []},
                             lazy=True,
                             )



scalesTable = DataFactory(name='scalesTable', 
                    description='Mango f21 scales description', 
                    editors=None,
                    includes=None,
                    )



