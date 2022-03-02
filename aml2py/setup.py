# -*- coding: utf-8 -*-
__revision__ = "$Id: setup.py 12238 2012-06-19 12:23:53Z pradal $"

# import
#from distutils.core import setup
from setuptools import setup, find_packages

from openalea.deploy.metainfo import read_metainfo

metadata = read_metainfo('metainfo.ini', verbose=True)
for key,value in metadata.iteritems():
    exec("%s = '%s'" % (key, value))



setup(name=name,
      version=version,
      description=description,
      long_description=long_description,
      author=authors,
      author_email=authors_email,
      url=url,
      license=license,

      py_modules=['aml2py'], 
      package_dir = {'':'src'}, 
      # entry_points
      entry_points = { 
        "console_scripts": ['aml2py = aml2py:main'],
        },
)

