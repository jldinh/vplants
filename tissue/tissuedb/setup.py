
import sys
import os

from setuptools import setup, find_packages
from os.path import join as pj

build_prefix = "build-scons"


# Header

# Setup script
# Package name
name = 'tissuedb'
namespace = 'openalea'
pkg_name= namespace + '.' + name

# Package version policy
version= '1.0.0' 

# Description
description= 'package to manage database of scripted files' 
long_description= '''
a simplest way to access files using a database
added with the possibility to replay script to 
generate files
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
	package_dir = { 'openalea.tissuedb':  pj('src','tissuedb'), "":"src" }, 

    
    include_package_data = True,
    package_data = {'' : ['*.pyd', '*.so'],},

    zip_safe= False,

    #lib_dirs = {'lib' : pj(build_prefix, 'lib'), },
    #inc_dirs = { 'include' : pj(build_prefix, 'include') },
	#share_dirs = { 'tutorial' : pj('examples','tutorial')},

    # Scripts
    entry_points = {
        "wralea": ['tissuedb.script = openalea.tissuedb.wralea',]
              },

    # Dependencies
    setup_requires = ['openalea.deploy'],
    dependency_links = ['http://openalea.gforge.inria.fr/pi'],
    install_requires = [],#TODO MySQLdb


    )


