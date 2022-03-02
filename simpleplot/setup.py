# -*- coding: utf-8 -*-
__revision__ = "$Id: setup.py 7887 2010-02-09 07:49:59Z cokelaer $"

import sys
import os

from setuptools import setup, find_packages
from os.path import join as pj

build_prefix = "build-scons"

# Header

# Setup script

# Package name
name = 'simpleplot'
namespace = 'openalea'
pkg_name= namespace + '.' + name

# Package version policy
version= '1.0.0' 

# Description
description= 'basic elements to display sequences of values' 
long_description= '''
simple plot contains the definition of a sequence and
a plotter to display it
'''

# Author
author= 'Jerome Chopard'
author_email= 'jerome.chopard@sophia.inria.fr'
url= 'http://openalea.gforge.inria.fr'
license= 'Cecill-C' 



# Main setup
setup(
    # Meta data
    name=name,
    version=version,
    description=description,
    long_description=long_description,
    author=author,
    author_email=author_email,
    url=url,
    license=license,
    keywords = '',

    
    # Define what to execute with scons
    #scons_scripts=['SConstruct'],
    #scons_parameters=["build","build_prefix="+build_prefix],

    # Packages
    namespace_packages = [namespace],
    create_namespaces = True,
    py_modules = [],
    packages =  [ 'openalea.' + x for x in find_packages('src') ],
	package_dir = { 'openalea.simpleplot':  pj('src','simpleplot'), "":"src" }, 

    
    include_package_data = True,
    package_data = {'' : ['*.pyd', '*.so'],},

    zip_safe= False,

    #lib_dirs = {'lib' : pj(build_prefix, 'lib'), },
    #inc_dirs = { 'include' : pj(build_prefix, 'include') },
	#share_dirs = { 'tutorial' : pj('examples','tutorial')},
    
    #postinstall_scripts = ['celltissue_postinstall',],

    # Scripts
    entry_points = {},

    # Dependencies
    setup_requires = ['openalea.deploy'],
    dependency_links = ['http://openalea.gforge.inria.fr/pi'],
    install_requires = [],


    )


