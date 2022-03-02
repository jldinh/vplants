# -*- python -*-
#
#       tissueview: display a tissue
#
#       Copyright 2006 INRIA - CIRAD - INRA  
#
#       File author(s): Jerome Chopard <jerome.chopard@sophia.inria.fr>
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
# 
#       OpenAlea WebSite : http://openalea.gforge.inria.fr
#

__doc__="""
node definition for tissueview package
"""

__license__= "Cecill-C"
__revision__=" $Id: $ "

from openalea.core import Factory
from openalea.core.interface import *

__name__ = "tissue.view"
__alias__ = []
__version__ = '0.0.2'
__license__ = "Cecill-C"
__authors__ = 'Jerome Chopard'
__institutes__ = 'INRIA/CIRAD'
__description__ = 'tissueview Node library.'
__url__ = 'http://openalea.gforge.inria.fr'
__icon__ = "icon.png"

__all__ = []

#########################################
#
#	PGL ext
#
#########################################
clearsc = Factory( name= "clear", 
				description= "",
				category = "",
				nodemodule = "pgl_ext",
				nodeclass = "clear_sc",
				inputs=(dict(name="sc", interface=None,),
				dict(name="send_signal", interface=IBool,value=False),),
				outputs=(dict(name="sc", interface=None,),),
				toscriptclass_name = "clear_sc_script",
			)

__all__.append('clearsc')

#########################################
#
#	color maps
#
#########################################
material_map = Factory( name= "map_mat", 
				description= "",
				category = "",
				nodemodule = "color",
				nodeclass = "material_map",
				inputs=(dict(name="prop", interface=IDict,),
				        dict(name="cmap", interface=IFunction),),
				outputs=(dict(name="func", interface=IFunction,),),
				toscriptclass_name = "material_map_script",
			)

__all__.append('material_map')

map_int = Factory( name= "map_int", 
				description= "",
				category = "",
				nodemodule = "color",
				nodeclass = "int_map",
				inputs=(),
				outputs=(dict(name="func", interface=IFunction,),),
				toscriptclass_name = "int_map_script",
			)

__all__.append('map_int')

map_jet = Factory( name= "map_jet", 
				description= "",
				category = "",
				nodemodule = "color",
				nodeclass = "jet_map",
				inputs=(dict(name="cmap", interface=IFloat, value=0.),
				        dict(name="vmax", interface=IFloat, value=1.),),
				outputs=(dict(name="cmap", interface=IFunction,),),
				toscriptclass_name = "jet_map_script",
			)

__all__.append('map_jet')

map_green = Factory( name= "map_green", 
				description= "",
				category = "",
				nodemodule = "color",
				nodeclass = "green_map",
				inputs=(dict(name="cmap", interface=IFloat, value=0.),
				        dict(name="vmax", interface=IFloat, value=1.),),
				outputs=(dict(name="cmap", interface=IFunction,),),
				toscriptclass_name = "green_map_script",
			)

__all__.append('map_green')

#########################################
#
#	display mesh
#
#########################################
mesh = Factory( name= "mesh", 
				description= "",
				category = "",
				nodemodule = "display_mesh",
				nodeclass = "display_mesh",
				inputs=(dict(name="mesh", interface=None,),
				        dict(name="pos", interface=None,),
				        dict(name="deg", interface=IInt,),
						dict(name="mat", interface=None,),
						dict(name="shrink", interface=IInt, value=0),
						dict(name="sc", interface=None),),
				outputs=(dict(name="sc", interface=None,),),
				toscriptclass_name = "display_mesh_script",
			)

__all__.append('mesh')

mesh2D = Factory( name= "mesh2D", 
				description= "",
				category = "",
				nodemodule = "display_mesh",
				nodeclass = "display_mesh2D",
				inputs=(dict(name="mesh", interface=None,),
				        dict(name="pos", interface=None,),
				        dict(name="deg", interface=IInt,),
						dict(name="mat", interface=None,),
						dict(name="shrink", interface=IInt, value=0),
						dict(name="offset", interface=IInt, value=0),
						dict(name="sc", interface=None),
						dict(name="clear", interface=IBool, value=False),),
				outputs=(dict(name="sc", interface=None,),),
				toscriptclass_name = "display_mesh2D_script",
			)

__all__.append('mesh2D')

mesh1D = Factory( name= "mesh1D", 
				description= "",
				category = "",
				nodemodule = "display_mesh",
				nodeclass = "display_mesh1D",
				inputs=(dict(name="mesh", interface=None,),
				        dict(name="pos", interface=None,),
				        dict(name="width", interface=IFloat, value=1.),
						dict(name="mat", interface=None,),
						dict(name="shrink", interface=IInt, value=0),
						dict(name="sc", interface=None),),
				outputs=(dict(name="sc", interface=None,),),
				toscriptclass_name = "display_mesh1D_script",
			)

__all__.append('mesh1D')

#########################################
#
#	display property
#
#########################################
mesh_prop = Factory( name= "mesh_prop", 
				description= "",
				category = "",
				nodemodule = "display_prop",
				nodeclass = "display_scalar_prop",
				inputs=(dict(name="mesh", interface=None,),
				        dict(name="pos", interface=None,),
				        dict(name="deg", interface=IInt,),
						dict(name="prop", interface=None,),
						dict(name="shrink", interface=IInt, value=0),
						dict(name="cmap", interface=IFunction),
						dict(name="sc", interface=None),),
				outputs=(dict(name="sc", interface=None,),),
				toscriptclass_name = "display_scalar_prop_script",
			)

__all__.append('mesh_prop')

mesh_prop2D = Factory( name= "mesh_prop2D", 
				description= "",
				category = "",
				nodemodule = "display_prop",
				nodeclass = "display_scalar_prop2D",
				inputs=(dict(name="mesh", interface=None,),
				        dict(name="pos", interface=None,),
				        dict(name="deg", interface=IInt,),
						dict(name="prop", interface=None,),
						dict(name="shrink", interface=IInt, value=0),
						dict(name="cmap", interface=IFunction),
						dict(name="offset", interface=IInt, value=0),
						dict(name="sc", interface=None),),
				outputs=(dict(name="sc", interface=None,),),
				toscriptclass_name = "display_scalar_prop2D_script",
			)

__all__.append('mesh_prop2D')

mesh_tens = Factory( name= "mesh_tens", 
				description= "",
				category = "",
				nodemodule = "display_prop",
				nodeclass = "display_tensorial_prop",
				inputs=(dict(name="mesh", interface=None,),
				        dict(name="pos", interface=None,),
				        dict(name="deg", interface=IInt, value=0),
						dict(name="prop", interface=None,),
						dict(name="scaling", interface=IFloat, value=1.),
						dict(name="sc", interface=None),),
				outputs=(dict(name="sc", interface=None,),),
				toscriptclass_name = "display_tensorial_prop_script",
			)

__all__.append('mesh_tens')

#########################################
#
#	select
#
#########################################
select_mesh = Factory( name= "select_mesh", 
				description= "",
				category = "",
				nodemodule = "select_mesh",
				nodeclass = "select_mesh",
				inputs=(dict(name="mesh", interface=None,),
				        dict(name="pos", interface=None,),
				        dict(name="deg", interface=IInt,),),
				outputs=(dict(name="draw func", interface=None,),),
				toscriptclass_name = "select_mesh_script",
			)

__all__.append('select_mesh')

#########################################
#
#	views
#
#########################################
mesh_view = Factory( name= "mesh_view", 
				description= "",
				category = "",
				nodemodule = "mesh_view",
				nodeclass = "mesh_view",
				inputs=(dict(name="mesh", interface=None,),
				        dict(name="pos", interface=None,),
				        dict(name="deg", interface=IInt,),
						dict(name="shrink", interface=IInt, value=0),
						dict(name="cmap", interface=IFunction),),
				outputs=(dict(name="sc", interface=None,),
				         dict(name="redraw", interface=IFunction,),
				         dict(name="select", interface=IFunction,),),
				toscriptclass_name = "mesh_view_script",
			)

__all__.append('mesh_view')

mesh_view2D = Factory( name= "mesh_view2D", 
				description= "",
				category = "",
				nodemodule = "mesh_view",
				nodeclass = "mesh_view2D",
				inputs=(dict(name="mesh", interface=None,),
				        dict(name="pos", interface=None,),
				        dict(name="deg", interface=IInt,),
						dict(name="shrink", interface=IInt, value=0),
						dict(name="cmap", interface=IFunction),
						dict(name="offset", interface=IInt, value=0),),
				outputs=(dict(name="sc", interface=None,),
				         dict(name="redraw", interface=IFunction,),
				         dict(name="select", interface=IFunction,),),
				toscriptclass_name = "mesh_view2D_script",
			)

__all__.append('mesh_view2D')

mesh_view1D = Factory( name= "mesh_view1D", 
				description= "",
				category = "",
				nodemodule = "mesh_view",
				nodeclass = "mesh_view1D",
				inputs=(dict(name="mesh", interface=None,),
				        dict(name="pos", interface=None,),
				        dict(name="with", interface=IFloat,),
						dict(name="cmap", interface=IFunction),
						dict(name="shrink", interface=IInt, value=0),),
				outputs=(dict(name="sc", interface=None,),
				         dict(name="redraw", interface=IFunction,),
				         dict(name="select", interface=IFunction,),),
				toscriptclass_name = "mesh_view1D_script",
			)

__all__.append('mesh_view1D')

scalar_prop_view = Factory( name= "scalar_prop_view", 
				description= "",
				category = "",
				nodemodule = "prop_view",
				nodeclass = "scalar_prop_view",
				inputs=(dict(name="mesh", interface=None,),
				        dict(name="pos", interface=None,),
				        dict(name="deg", interface=IInt,),
						dict(name="prop", interface=None,),
						dict(name="shrink", interface=IInt, value=0),
						dict(name="cmap", interface=IFunction),),
				outputs=(dict(name="sc", interface=None,),
				         dict(name="redraw", interface=IFunction,),
				         dict(name="select", interface=IFunction,),),
				toscriptclass_name = "scalar_prop_view_script",
			)

__all__.append('scalar_prop_view')

tensorial_prop_view = Factory( name= "tensorial_prop_view", 
				description= "",
				category = "",
				nodemodule = "prop_view",
				nodeclass = "tensorial_prop_view",
				inputs=(dict(name="mesh", interface=None,),
				        dict(name="pos", interface=None,),
				        dict(name="deg", interface=IInt,),
						dict(name="prop", interface=None,),
						dict(name="scaling", interface=IFloat, value=1.),),
				outputs=(dict(name="sc", interface=None,),
				         dict(name="redraw", interface=IFunction,),
				         dict(name="select", interface=IFunction,),),
				toscriptclass_name = "tensorial_prop_view_script",
			)

__all__.append('tensorial_prop_view')

