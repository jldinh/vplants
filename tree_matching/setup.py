# -*- coding: utf-8 -*-
__revision__ = "$Id: setup.py 9869 2010-11-04 17:31:41Z dbarbeau $"

from setuptools import setup, find_packages
from openalea.deploy.binary_deps import binary_deps
import os, sys
from os.path import join as pj

from openalea.deploy.metainfo import read_metainfo
metadata = read_metainfo('metainfo.ini', verbose=True)
for key,value in metadata.iteritems():
    exec("%s = '%s'" % (key, value))


build_prefix = "build-scons"

# Scons build directory
scons_parameters=["build_prefix="+build_prefix]


# platform dependencies
install_requires = []#[binary_deps('vplants.mtg'), binary_deps('vplants.stat_tool')]#, binary_deps("boost")]
setup_requires = ['openalea.deploy']


if __name__ == '__main__':
    
    setup(name=name,
          version=version,
          author=authors,
          description=description,
          url=url,
          license=license,

          # Define where to execute scons
          scons_scripts=['SConstruct'],
          # Scons parameters  
          scons_parameters=scons_parameters,
        
          # Packages
          #namespace_packages = ["openalea"],
          #create_namespaces = True,
          
          # pure python  packages
          #packages= [ "openalea", 
          #            "openalea.tree_matching"
          #            ],
          
          # python packages directory
          #package_dir= { #pkg_name : pj('src','vplants'),
          #               '' : 'src',
          #               },

          # Add package platform libraries if any
          include_package_data=True,
          zip_safe=False,

          # Specific options of openalea.deploy
          lib_dirs = {'lib' : pj(build_prefix, 'lib'),},
          inc_dirs = {'include' : pj(build_prefix, 'include') },
          

          # Dependencies
          setup_requires = setup_requires, 
          install_requires = install_requires, 
          dependency_links = ['http://openalea.gforge.inria.fr/pi'],
          pylint_packages = ['.']
          )


    
