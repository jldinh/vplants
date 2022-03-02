# -*- coding: utf-8 -*-
__revision__ = "$Id: $"

import os, sys
pj = os.path.join

from setuptools import setup

from openalea.deploy.metainfo import read_metainfo
from openalea.deploy.binary_deps import binary_deps

metadata = read_metainfo('metainfo.ini', verbose=True)
for key,value in metadata.iteritems():
    exec("%s = '%s'" % (key, value))

external_dependencies = []
if sys.platform.startswith('win'):
    external_dependencies = [
    binary_deps('boost'),
    MinGW,
    bisonflex,
    scons,
    qt4_dev,
    SOAPpy
    ]



install_requires = external_dependencies


setup(
    name = name,
    version = version,
    description = description,
    long_description = long_description,
    author = authors,
    author_email = authors_email,
    url = url,
    license = license,


    add_plat_name = True,

    # Dependencies
    setup_requires = ['openalea.deploy'],
    install_requires = install_requires,
    dependency_links = ['http://openalea.gforge.inria.fr/pi'],
    )


