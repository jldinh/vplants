# -*- coding: utf-8 -*-
__revision__ = "$Id: setup.py 7870 2010-02-08 18:10:22Z cokelaer $"

import sys
import os

from setuptools import setup, find_packages
from os.path import join as pj

build_prefix = "build-scons"


# Header

# Setup script

# Package name
name = 'cphysics'
namespace = 'openalea'
pkg_name= namespace + '.' + name

# Package version policy
version= '1.0.0' 

# Description
description= 'C++ version of physics module' 
long_description= '''
see openalea.physics module description.
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
    scons_scripts=['SConstruct'],
    scons_parameters=["build","build_prefix="+build_prefix],

    # Packages
    namespace_packages = [namespace],
    create_namespaces = True,
    packages =  [ 'openalea.' + x for x in find_packages('src') ],
    package_dir = { 'openalea.cphysics':  pj('src','cphysics'), '' : 'src', }, 

    
    include_package_data = True,
    package_data = {'' : ['*.pyd', '*.so', '*.dylib'],},
    exclude_package_data = { '': ['*.pdf'] },

    zip_safe= False,

    lib_dirs = {'lib' : pj(build_prefix, 'lib'), },
    inc_dirs = { 'include' : pj(build_prefix, 'include') },
    
    #postinstall_scripts = ['',],

    # Scripts
#    entry_points = { 'console_scripts': [
#                            'fake_script = openalea.fakepackage.amodule:console_script', ],
#                      'gui_scripts': [
#                            'fake_gui = openalea.fakepackage.amodule:gui_script',]},

    # Dependencies
    setup_requires = ['openalea.deploy'],
    dependency_links = ['http://openalea.gforge.inria.fr/pi'],
    #install_requires = [],


    )


