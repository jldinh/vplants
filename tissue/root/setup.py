###########
#
#		compile tissue files
#
###########
import sys, os
from os.path import join,basename,splitext,exists
from glob import glob
from subprocess import call

cur_dir = os.getcwd()
os.chdir(join(".","src","root_wralea","data") )

print "compile tissues"
for drawing_name in glob("*.svg") :
	tissue_name = "%s.zip" % splitext(drawing_name)[0]
	if not exists(tissue_name) :
		print "compile",drawing_name
		ret = call("python create_tissue.py %s" % drawing_name,shell = True)
	else :
		print tissue_name

#pop state
os.chdir(cur_dir)

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
# (used to construct egg infos)
long_description= '''
Root simulations
'''

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
            'wralea': ['root = openalea.root_wralea']
        },

    )

