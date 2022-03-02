
# Redirect path
import os

cdir = os.path.dirname(__file__)
pdir = os.path.join(cdir, "../../tutorial")
pdir = os.path.abspath(pdir)

__path__ = [pdir] + __path__[:]

from vplants.tutorial.__init__ import *
