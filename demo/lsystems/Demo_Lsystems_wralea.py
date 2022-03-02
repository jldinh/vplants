
# This file has been generated at $TIME

from openalea.core import *

def register_packages(pkgmanager):
    
    metainfo = {'description': 'Demo of PyLsystems', 'license': 'GPL', 'url': '', 'version': '0.1', 'authors': 'F. Boudon', 'institutes': 'Inria/Cirad/Inra'} 
    pkg = UserPackage("Demo.Lsystems", metainfo)

    

    nf = CompositeNodeFactory(name='MarkovLsystem', 
                              description='', 
                              category='Demo,demo,stat',
                              doc='',
                              inputs=[],
                              outputs=[],
                              elt_factory={2: ('Catalog.Python', 'fread'), 3: ('PyLSytems', 'LSystem'), 4: ('PyLSytems', 'run'), 5: ('PyLSytems', 'plot'), 8: ('System', 'annotation'), 9: ('Catalog.Data', 'dict'), 10: ('System', 'annotation'), 11: ('System', 'annotation'), 12: ('System', 'annotation'), 13: ('Catalog.Data', 'packagedir'), 14: ('Catalog.Data', 'filename'), 15: ('System', 'annotation'), 16: ('System', 'annotation'), 17: ('System', 'annotation')},
                              elt_connections={151785316: (14, 0, 2, 0), 151785352: (2, 0, 3, 0), 151785292: (13, 0, 14, 1), 151785328: (3, 0, 5, 1), 151785364: (9, 0, 3, 3), 151785304: (4, 0, 5, 0), 151785340: (3, 0, 4, 0)},
                              elt_data={2: {'lazy': False, 'hide': True, 'port_hide_changed': set([]), 'priority': 0, 'caption': 'fread', 'posx': 168.75, 'posy': 257.5, 'minimal': False}, 3: {'lazy': False, 'hide': True, 'port_hide_changed': set([]), 'priority': 0, 'caption': 'LSystem', 'posx': 220.0, 'posy': 368.75, 'minimal': False}, 4: {'lazy': True, 'hide': True, 'port_hide_changed': set([]), 'priority': 0, 'caption': 'run', 'posx': 176.25, 'posy': 432.5, 'minimal': False}, 5: {'lazy': True, 'hide': True, 'port_hide_changed': set([]), 'priority': 0, 'caption': 'plot', 'posx': 248.75, 'posy': 500.0, 'minimal': False}, 8: {'txt': '3D output', 'posx': 335.0, 'posy': 506.25}, 9: {'lazy': True, 'hide': True, 'port_hide_changed': set([]), 'priority': 0, 'caption': 'dict', 'posx': 273.75, 'posy': 245.0, 'minimal': False}, 10: {'txt': 'Package : PyLSystems', 'posx': 573.75, 'posy': 63.75}, 11: {'txt': 'Author : Frederic Boudon', 'posx': 575.0, 'posy': 91.25}, 12: {'txt': 'Plant simulation with LSystems', 'posx': 575.0, 'posy': 20.0}, 13: {'lazy': True, 'hide': True, 'port_hide_changed': set([]), 'priority': 0, 'caption': 'packagedir', 'posx': 151.80555555555554, 'posy': 132.22222222222223, 'minimal': False}, 14: {'lazy': True, 'hide': True, 'port_hide_changed': set([1]), 'priority': 0, 'caption': 'filename', 'posx': 154.58333333333334, 'posy': 182.22222222222223, 'minimal': False}, 15: {'txt': 'Source file', 'posx': 277.22222222222223, 'posy': 129.44444444444446}, 16: {'txt': 'L system editor', 'posx': 337.5, 'posy': 368.75}, 17: {'txt': 'Parameters', 'posx': 348.75, 'posy': 232.5}, '__out__': {'lazy': True, 'hide': True, 'port_hide_changed': set([]), 'priority': 0, 'caption': 'Out', 'posx': 20.0, 'posy': 250.0, 'minimal': False}, '__in__': {'lazy': True, 'hide': True, 'port_hide_changed': set([]), 'priority': 0, 'caption': 'In', 'posx': 20.0, 'posy': 5.0, 'minimal': False}},
                              elt_value={2: [], 3: [(1, "''"), (2, '-1')], 4: [(1, "''"), (2, '20')], 5: [], 8: [], 9: [(0, "{'NbPlant': 4}")], 10: [], 11: [], 12: [], 13: [(0, "'Demo.Lsystems'")], 14: [(0, "'lsys_markov.lpy'")], 15: [], 16: [], 17: [], '__out__': [], '__in__': []},
                              lazy=True,
                              )

    pkg.add_factory(nf)


    pkgmanager.add_package(pkg)


