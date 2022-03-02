###############################################################################
# -*- python -*-
#
#       amlPy function definition 
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
###############################################################################

__doc__="""
amlPy function definition
"""

__license__= "Cecill-C"
__revision__=" $Id: mtg_factory.py 7897 2010-02-09 09:06:21Z cokelaer $ "

from openalea.core.external import *

def define_factory(package):
    """ Define factories for arithmetics nodes """

    nf = Factory( name= "MTG", 
                  description= "MTG file creation", 
                  category = "scene.MTG", 
                  nodemodule = "py_mtg",
                  nodeclass = "py_MTG",
                  )

    package.add_factory( nf )

    nf = Factory( name= "VtxList", 
                  description= "Array of vertices contained in a MTG", 
                  category = "scene.MTG", 
                  nodemodule = "py_mtg",
                  nodeclass = "py_VtxList",
                  )

    package.add_factory( nf )

    nf = Factory( name= "Feature", 
                  description= "Feature data stored on MTG vertices", 
                  category = "scene.MTG", 
                  nodemodule = "py_mtg",
                  nodeclass = "py_Feature",
                  )

    package.add_factory( nf )

    nf = Factory( name= "VtxFunction", 
                  description= "Common function on  MTG", 
                  category = "scene.MTG", 
                  nodemodule = "py_mtg",
                  nodeclass = "VtxFunction",
                  )

    package.add_factory( nf )

    nf = Factory( name= "TopoFunction", 
                  description= "Common function on  MTG", 
                  category = "scene.MTG", 
                  nodemodule = "py_mtg",
                  nodeclass = "TopoFunction",
                  )

    package.add_factory( nf )

    nf = Factory( name= "Complex", 
                  description= "Complex of a vertex.", 
                  category = "scene.MTG", 
                  nodemodule = "py_mtg",
                  nodeclass = "py_Complex",
                  )

    package.add_factory( nf )

    nf = Factory( name= "Components", 
                  description= "Set of components of a vertex.", 
                  category = "scene.MTG", 
                  nodemodule = "py_mtg",
                  nodeclass = "py_Components",
                  )

    package.add_factory( nf )

    nf = Factory( name= "MTGRoot", 
                  description= "Returns the global root of a MTG.", 
                  category = "scene.MTG", 
                  nodemodule = "py_mtg",
                  nodeclass = "py_MTGRoot",
                  inputs=(dict(name='graph'),),
                  outputs=(dict(name='Vtx',interface=IInt),),
                  )

    package.add_factory( nf )

    nf = Factory( name= "Axis", 
                  description= "Returns the sequence of vertices defining the axis of a given vertex.", 
                  category = "scene.MTG", 
                  nodemodule = "py_mtg",
                  nodeclass = "py_Axis",
                  )

    package.add_factory( nf )

    nf = Factory( name= "PlantFrame", 
                  description= "Constructs a geometric interpretation of a MTG.", 
                  category = "scene.MTG", 
                  nodemodule = "py_mtg",
                  nodeclass = "py_PlantFrame",
                  )
    package.add_factory( nf )

    nf = Factory( name= "DressingData", 
                  description= "Data and default geometric parameters used to compute the geometric interpretation of a MTG.", 
                  category = "scene.MTG", 
                  nodemodule = "py_mtg",
                  nodeclass = "py_dressingdata",
                  inputs=(dict(name="MTG"),dict(name="filename", interface=IFileStr)),
                  outputs=(dict(name="DressingData"),),
                  )
    package.add_factory( nf )

    nf = Factory( name= "PlotPlantFrame", 
                  description= "Plot PlantFrame objects.", 
                  category = "scene.MTG", 
                  nodemodule = "py_mtg",
                  nodeclass = "py_PlotPlantFrame",
                  )
    package.add_factory( nf )

    nf = Factory( name= "PlotLineTree", 
                  description= "Plot Linetree objects.", 
                  category = "scene.MTG", 
                  nodemodule = "py_mtg",
                  nodeclass = "py_PlotLineTree",
                  )
    package.add_factory( nf )

    nf = Factory( name= "Linetree2Scene", 
                  description= "Extract scene from Linetree.", 
                  category = "scene.MTG", 
                  nodemodule = "py_mtg",
                  nodeclass = "py_Linetree2Scene",
                  inputs= ( dict( name = "linetree", interface=None ),
                            dict( name = "scale", interface=IEnumStr(['Micro', 'Macro']), value = 'Micro'),
                          ),
                  outputs=(dict(name="Scene", interface = None),
                          ),
                  )
    package.add_factory( nf )

    nf = Factory( name= "Quotient", 
                  description= "Quotient Linetree objects.", 
                  category = "scene.MTG", 
                  nodemodule = "py_mtg",
                  nodeclass = "py_Quotient",
                  )
    package.add_factory( nf )

    nf = Factory( name= "Compress", 
                  description= "Create a compressed representation of Linetree objects.", 
                  category = "scene.MTG", 
                  nodemodule = "py_mtg",
                  nodeclass = "py_Compress",
                  )
    package.add_factory( nf )

    nf = Factory( name= "VirtualPattern", 
                  description= "Object containing the specification to add (virtual) components to an existing PlantFrame.", 
                  category = "scene.MTG", 
                  nodemodule = "py_mtg",
                  nodeclass = "py_VirtualPattern",
                  )
    package.add_factory( nf )
    
