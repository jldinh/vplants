# -*- coding: utf-8 -*-
__revision__ = "$Id: setup.py 9869 2010-11-04 17:31:41Z dbarbeau $"

# Setup script has been commented to ease the writing of your own file. 

# A setup script mainly consist of a call to the setup function of setuptool, that allows to create a distribution archive of a set of python modules grouped in packages (ie in directories with an __init__.py file).
# In the context of OpenAlea, this function has been extended by the openalea.deploy module to ease the simultaneaous distribution of binaries and libraries.

# (To adapt this script for your package, you mainly have to change the content of the variable defined before the call to setup function, and comment out unused options in the call of the function)

import sys
import os

from setuptools import setup, find_packages
from openalea.deploy.metainfo import read_metainfo

metadata = read_metainfo('metainfo.ini', verbose=True)
for key,value in zip(metadata.keys(), metadata.values()):
    exec("%s = '%s'" % (key, value))

pkg_root_dir = 'src'
pkgs = [ pkg for pkg in find_packages(pkg_root_dir) if namespace not in pkg]
top_pkgs = [pkg for pkg in pkgs if len(pkg.split('.')) < 2]
packages = [ namespace + "." + pkg for pkg in pkgs]
package_dir = dict( [('',pkg_root_dir)] + [(namespace + "." + pkg, pkg_root_dir + "/" + pkg) for pkg in top_pkgs] )

# Meta information
long_description= '''
The pglviewer package implement the management of GUI.
Used to display 3D simulations in real time.
'''

###########
#
#		compile QT interfaces
#
###########
#import os

#rc_file = "src/%s/icons/pglviewer.qrc" % package
#out_file = "src/%s/pglviewer_rc.py" % package
#os.system("pyrcc4 -o %s %s" % (out_file,rc_file) )

#for dirname in ("pyshell","probe","loop","scene") :
#    print "compile %s" % dirname
#    rc_file = "src/%s/%s/icons/%s.qrc" % (package,dirname,dirname)
#    out_file = "src/%s/%s/%s_rc.py" % (package,dirname,dirname)
#    os.system("pyrcc4 -o %s %s" % (out_file,rc_file) )

# setup function call
#
setup(
    # Meta data (no edition needed if you correctly defined the variables above)
    name=name,
    version=version,
    description=description,
    long_description=long_description,
    author=authors,
    author_email=authors_email,
    url=url,
    license=license,
    keywords = '',
    # package installation
    packages= packages,
    package_dir= package_dir,
    # Namespace packages creation by deploy
    namespace_packages = [namespace],
    create_namespaces = True,
    # tell setup not  tocreate a zip file but install the egg as a directory (recomended to be set to False)
    zip_safe= False,
    # Dependencies
    setup_requires = ['openalea.deploy'],
    install_requires = [],
    dependency_links = ['http://openalea.gforge.inria.fr/pi'],

    # Eventually include data in your package
    # (flowing is to include all versioned files other than .py)
    include_package_data = True,
    # (you can provide an exclusion dictionary named exclude_package_data to remove parasites).
    # alternatively to global inclusion, list the file to include   
    package_data = {'' : ['*.pyd', '*.so', '*.zip', '*.png'],},

    # postinstall_scripts = ['',],

    # Declare scripts and wralea as entry_points (extensions) of your package 
    entry_points = {
            'wralea': ['pglviewer = openalea.pglviewer_wralea']
        },

    )

