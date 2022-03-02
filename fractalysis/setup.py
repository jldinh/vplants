# -*- coding: iso-8859-15 -*-

import sys, os
from setuptools import setup, find_packages
from openalea.deploy.binary_deps import binary_deps
from os.path import join as pj

from openalea.deploy.metainfo import read_metainfo
metadata = read_metainfo('metainfo.ini', verbose=True)
for key,value in metadata.iteritems():
    exec("%s = '%s'" % (key, value))

# Package name
pkg_name= namespace + '.' + package
wralea_name= namespace + '.' + package + '_wralea'

# Scons build directory
build_prefix= "build-scons"

# platform dependencies
install_requires = []
"""
install_requires = [binary_deps('vplants.plantgl'),]
"""

if sys.platform.startswith('win'):
    install_requires = [binary_deps('vplants.plantgl'),]
    install_requires += [binary_deps("boost"),]

setup_requires = install_requires + ['openalea.deploy']


# Main setup
setup(
    # Meta data
    name=name,
    version=version,
    description=description,
    long_description=long_description,
    author=authors,
    author_email=authors_email,
    url=url,
    license=license,
    
    # Define what to execute with scons
    # scons is responsible to put compiled library in the write place
    # ( lib/, package/, etc...)
    scons_scripts = ['SConstruct'],

    # scons parameters  
    scons_parameters = ["build","build_prefix="+build_prefix],

    # Packages
    namespace_packages = [namespace,'openalea'],
    create_namespaces = True,

    # pure python  packages
    packages= [ pkg_name, 
                pkg_name+'.light', 
                pkg_name+'.engine', 
                pkg_name+'.fractutils',
                'openalea',
                'openalea.'+package,
                'openalea.'+package+'_wralea',
                wralea_name, 
                wralea_name+'.light', 
                wralea_name+'.light.castshadow', 
                wralea_name+'.engine', 
                wralea_name+'.engine.boxcounting', 
                wralea_name+'.engine.two_surfaces', 

 ],

    # python packages directory
    package_dir= {  pkg_name : pj('src', package),
                    pkg_name+'.light' :pj('src', package, 'light'),
                    pkg_name+'.light.castshadow' :pj('src', package, 'light', 'castshadow'),
                    pkg_name+'.engine' :pj('src', package, 'engine'),
                    pkg_name+'.engine.boxcounting' :pj('src', package, 'engine', 'boxcounting'),
                    pkg_name+'.engine.two_surfaces' :pj('src', package, 'engine', 'two_surfaces'),
                    pkg_name+'.fractutils' :pj('src', package, 'fractutils'),
                    wralea_name : pj('src',package+'_wralea'),
                    '' : 'src',
                  },

    # add package platform libraries if any
    package_data= { '' : ['*.so', '*.dll', '*.pyd', '*.png', '*.dylib', '*.geom', '*.bgeom', '*.drf', '*.mtg' ]},
    include_package_data=True,
    zip_safe = False,
                     

    # Specific options of openalea.deploy
    lib_dirs = {'lib' : pj(build_prefix, 'lib'),},
    inc_dirs = { 'include' : pj(build_prefix, 'include') },
    share_dirs = { 'doc': 'doc',},
          

    # Dependencies
    setup_requires = setup_requires ,
    install_requires = install_requires,
    dependency_links = ['http://openalea.gforge.inria.fr/pi'],

    # entry_points
    entry_points = {"wralea": [
            "fractalysis = "+wralea_name,
            "castshadow = "+wralea_name+".light.castshadow",
            "two_surfaces = "+wralea_name+".engine.two_surfaces",
            "boxcounting = "+wralea_name+".engine.boxcounting",
            ]
                    },
   pylint_packages = ['src/fractalysis/engine','sec/fractalysis/light','src/fractalysis/fracutils']
  )


