# Redirect path
import os
import openalea.aml

__path__ = openalea.aml.__path__ + __path__[:]

from openalea.aml.__init__ import *
