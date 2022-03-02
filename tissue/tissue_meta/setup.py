import os, sys
pj = os.path.join

from setuptools import setup, find_packages

from openalea.deploy.metainfo import read_metainfo
metadata = read_metainfo('metainfo.ini', verbose=True)
for key,value in zip(metadata.keys(), metadata.values()):
    exec("%s = '%s'" % (key, value))

long_description = """Install all packages
mandatory to perform full tissue simulations
"""

external_dependencies = []

alea_dependencies = []
#'openalea.container',
#'pglviewer',
#'physics',
#'svgdraw',
#'celltissue',
#'growth',
#'tissueedit',
#'tissueshape',
#'tissueview',
#'vmanalysis'
#]

install_requires = alea_dependencies
if sys.platform.startswith('win'):
    install_requires.extend(external_dependencies)
print install_requires

setup(
    name = name,
    version = version,
    description = description,
    long_description = long_description,
    author = authors,
    author_email = authors_email,
    url = url,
    license = license,


    create_namespaces=False,
    zip_safe=False,

    packages=find_packages('src'),

    package_dir={"":"src" },

    # Add package platform libraries if any
    include_package_data=True,
    package_data = {'' : ['*.png','*.zip','*.svg'],},
    # Dependencies
    setup_requires = ['openalea.deploy'],
    install_requires = install_requires,
    dependency_links = ['http://openalea.gforge.inria.fr/pi'],

    # entry_points
    entry_points = {"wralea": ['tissue = tissue']},
    )


