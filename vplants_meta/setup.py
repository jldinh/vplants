# -*- coding: utf-8 -*-
__revision__ = "$Id: setup.py 13450 2012-12-21 15:59:33Z pradal $"

import os, sys
pj = os.path.join

from setuptools import setup, find_packages

from openalea.deploy.metainfo import read_metainfo
from openalea.deploy.binary_deps import binary_deps

metadata = read_metainfo('metainfo.ini', verbose=True)
for key,value in metadata.iteritems():
    exec("%s = '%s'" % (key, value))


if sys.platform.startswith('win'):
    external_dependencies = [
    binary_deps('boost'),
    'gnuplot',
    ]
else:
    external_dependencies = [
    #'qt4>=4.4.3-2',
    'qhull',
    'bisonflex',
    binary_deps('boost'),
    'gnuplot',
    ]


Openalea = ["openalea."+t for t in ["container >= 2.2.0", 
                                    "pglviewer >= 1.0.0", 
                                    "svgdraw >= 1.0.0",
                                    "mtg >= 1.0.0"
                                    ]]
                                    
Vplants = ["vplants."+t for t in [ 'plantgl >= 2.16.0',
                                   'tool >= 1.0.0',
                                   'stat_tool >= 1.0.0',
                                   'sequence_analysis >= 1.0.0',
                                   'amlobj >= 1.0.0',
                                   'tree_matching >= 1.0.0',
                                   'aml >= 1.0.0',
                                   'fractalysis >= 1.0.0',
                                   'mtg >= 1.0.0',
                                   'weberpenn >= 1.0.0',
                                   'lpy == 2.1.0',     
                                   'tree >= 1.0.0',
                                   'tree_statistic >= 1.0.0',
                                   'mechanics >= 1.0.0',
                                   'physics >= 1.0.0',
                                    ]]                                           
    
VPlantsTissue = ["vplants.tissue."+t for t in [ "celltissue >= 1.0.0", 
                                                "genepattern >= 1.0.0", 
                                                "growth >= 1.0.0", 
                                                "tissue >= 1.0.0", 
                                                "tissueedit >= 1.0.0", 
                                                "tissueshape >= 1.0.0", 
                                                "tissueview >= 1.0.0", 
                                                "vmanalysis >= 1.0.0"
                                                ]]                                                                          
    
    
alea_dependencies = Openalea+Vplants+VPlantsTissue



install_requires = alea_dependencies
if sys.platform.startswith('win'):
    install_requires.extend(external_dependencies)
install_requires = []

setup(
    name = name,
    version = version,
    description = description,
    long_description = long_description,
    author = authors,
    author_email = authors_email,
    url = url,
    license = license,


    namespace_packages = ['vplants'],
    create_namespaces=False,
    zip_safe=False,

    packages=find_packages('src'),

    package_dir={"":"src" },

    add_plat_name = True,

    # Add package platform libraries if any
    include_package_data=True,
    package_data = {'' : ['*.png'],},
    # Dependencies
    setup_requires = ['openalea.deploy'],
    install_requires = install_requires,
    dependency_links = ['http://openalea.gforge.inria.fr/pi'],

    # entry_points
    entry_points = {"wralea": ['vplants = vplants']},
    )


