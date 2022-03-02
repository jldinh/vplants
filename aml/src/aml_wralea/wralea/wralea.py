# -*- python -*-
#
#       aml package: AMAPmod package interface for the amlPy module
#
#       Copyright or (C) or Copr. 2006 INRIA - CIRAD - INRA  
#
#       File author(s): Christophe Pradal <christophe.prada@cirad.fr>
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
# 
#       OpenAlea WebSite : http://openalea.gforge.inria.fr
#


__doc__="""
Wralea for AMAPmod.
"""

__license__= "Cecill"
__revision__=" $Id: wralea.py 7897 2010-02-09 09:06:21Z cokelaer $"


from openalea.core import *



import mtg_factory
import stat_factory

def register_packages(pkgmanager):
    # amlPy

    metainfo={ 'version' : '0.0.1',
               'license' : 'CECILL-C',
               'authors' : 'Christophe Pradal',
               'institutes' : 'CIRAD',
               'description' : 'VPlants.aml functionalities',
               'url' : 'http://openalea.gforge.inria.fr'
               }


    package = Package("vplants.mtg", metainfo)
    mtg_factory.define_factory(package)
    pkgmanager.add_package(package)

    

    package = Package("vplants.stat", metainfo)
    stat_factory.define_factory(package)
    pkgmanager.add_package(package)


