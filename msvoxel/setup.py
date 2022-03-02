# -*- coding: utf-8 -*-
__revision__ = "$Id: setup.py 17608 2014-10-17 07:46:31Z pradal $"

from setuptools import setup, find_packages
from openalea.deploy.binary_deps import binary_deps
import os, sys
from os.path import join as pj
 
packagename = 'msvoxel'
namespace = 'openalea'
build_prefix = "build-scons"

# Scons build directory
scons_parameters=["build_prefix="+build_prefix]

# platform dependencies
install_requires = []
if sys.platform.startswith('win'):
    install_requires = [binary_deps('vplants.mtg')]
    install_requires += [binary_deps("boostpython")]

setup_requires = install_requires + ['openalea.deploy']

if __name__ == '__main__':
    
    setup(name='VPlants.MsVoxel',
          version='0.1',
          author='',
          description='msvoxel library',
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
          inc_dirs = {'include' : pj(build_prefix, 'include') },
          

          # Dependencies
          setup_requires = setup_requires,
          install_requires = install_requires,
          dependency_links = ['http://openalea.gforge.inria.fr/pi'],
          )


    
