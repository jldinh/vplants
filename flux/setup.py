# -*- coding: utf-8 -*-
__revision__ = "$Id: setup.py 17608 2014-10-17 07:46:31Z pradal $"

from setuptools import setup, find_packages
import os, sys
from os.path import join as pj
 
packagename = 'flux'
namespace = 'openalea'
build_prefix = "build-scons"

# Scons build directory
scons_parameters=["build_prefix="+build_prefix]

# platform dependencies
install_requires = []
"""
install_requires = ['vplants.mtg']
"""
if sys.platform.startswith('win'):
    install_requires = ["boostpython"]

setup_requires = install_requires + ['openalea.deploy']


if __name__ == '__main__':
    
    setup(name='VPlants.Flux',
          version='0.1',
          author='',
          description='flux library',
          url='',
          license='GPL',
          
          # Define where to execute scons
          scons_scripts=['SConstruct'],
          # Scons parameters  
          scons_parameters=scons_parameters,
        
          # Packages
          #packages=
          #package_dir=
      
          # Add package platform libraries if any
          include_package_data=True,
          zip_safe = False,

          # Specific options of openalea.deploy
          lib_dirs = {'lib' : pj(build_prefix, 'lib'),},
          inc_dirs = { 'include' : pj(build_prefix, 'include') },
          

          # Dependencies
          setup_requires = setup_requires,
          install_requires = install_requires,
          dependency_links = ['http://openalea.gforge.inria.fr/pi'],
          )


    
