
import sys
import os

from setuptools import setup, find_packages
from os.path import join as pj

build_prefix = "build-scons"


# Header

# Setup script
###########
#
#		compile QT interfaces
#
###########
import sys, os
from os.path import join
# Get the location of the installed egg
base_dir = os.getcwd()
cur_dir=os.getcwd()
#main viewer ui
res_dir=join(base_dir,"src","tissuepainter")
os.chdir(res_dir)
print "compile gui ressources"
execfile("compile_ui.py")
#pop state
os.chdir(cur_dir)

# Package name
name = 'tissuepainter'
namespace = 'openalea'
pkg_name= namespace + '.' + name

# Package version policy
version= '1.0.0' 

# Description
description= 'small GUI to paint elements of a tissue' 
long_description= '''
This is mainly a GUI used to graphical mark some elements (either cells or wall)
on a tissue
'''

# Author
author= 'Jerome Chopard'
author_email= 'jerome.chopard@sophia.inria.fr'
url= 'http://openalea.gforge.inria.fr'
license= 'Cecill-C' 

pkg_root_dir = 'src'
pkgs = [ pkg for pkg in find_packages(pkg_root_dir) if namespace not in pkg]
top_pkgs = [pkg for pkg in pkgs if len(pkg.split('.')) < 2]
packages = [ namespace + "." + pkg for pkg in pkgs]
package_dir = dict( [('',pkg_root_dir)] + [(namespace + "." + pkg, pkg_root_dir + "/" + pkg) for pkg in top_pkgs] )


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
    # package installation
    packages= packages,
    package_dir= package_dir,

    
    include_package_data = True,
    package_data = {'' : ['*.pyd', '*.so'],},

    zip_safe= False,

    #lib_dirs = {'lib' : pj(build_prefix, 'lib'), },
    #inc_dirs = { 'include' : pj(build_prefix, 'include') },
	#share_dirs = { 'tutorial' : pj('examples','tutorial')},

    # Scripts
#    entry_points = { 'console_scripts': [
#                            'fake_script = openalea.fakepackage.amodule:console_script', ],
#                      'gui_scripts': [
#                            'fake_gui = openalea.fakepackage.amodule:gui_script',]},

    # Dependencies
    setup_requires = ['openalea.deploy'],
    dependency_links = ['http://openalea.gforge.inria.fr/pi'],
    install_requires = ['openalea.container'],#TODO


    )


