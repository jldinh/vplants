# -*- python -*-
#
#       tissue_growth: simulation of a growing tissue
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
node definition for simulation fo a growing tissue
"""

__license__= "Cecill-C"
__revision__=" $Id: __wralea__.py 7897 2010-02-09 09:06:21Z cokelaer $ "

from openalea.core import Factory
from openalea.core.interface import *

__name__ = "demo.tissue.growth"
__alias__ = []
__version__ = '0.0.2'
__license__ = "Cecill-C"
__authors__ = 'Jerome Chopard'
__institutes__ = 'INRIA/CIRAD'
__description__ = 'Tissue growth Node library.'
__url__ = 'http://openalea.gforge.inria.fr'

__all__ = []

#########################################
#
#	physiology
#
#########################################
init_physiology = Factory( name= "init.physiology", 
				description= "",
				category = "",
				nodemodule = "physiology",
				nodeclass = "init_physiology",
				inputs=(dict(name="param", interface=None,),),
				outputs=(dict(name="param", interface=None,),),
			)

__all__.append('init_physiology')

physiology_process = Factory( name= "physiology", 
				description= "",
				category = "",
				nodemodule = "physiology",
				nodeclass = "physiology_process",
				inputs=(dict(name="param", interface=None,),),
				outputs=(dict(name="process", interface=None,),),
			)

__all__.append('physiology_process')

#########################################
#
#	mechanics
#
#########################################
init_mechanics = Factory( name= "init.mechanics", 
				description= "",
				category = "",
				nodemodule = "mechanics",
				nodeclass = "init_mechanics",
				inputs=(dict(name="param", interface=None,),),
				outputs=(dict(name="param", interface=None,),),
			)

__all__.append('init_mechanics')

mechanics_process = Factory( name= "mechanics", 
				description= "",
				category = "",
				nodemodule = "mechanics",
				nodeclass = "mechanics_process",
				inputs=(dict(name="param", interface=None,),),
				outputs=(dict(name="process", interface=None,),),
			)

__all__.append('mechanics_process')

#########################################
#
#	growth
#
#########################################
init_growth = Factory( name= "init.growth", 
				description= "",
				category = "",
				nodemodule = "growth",
				nodeclass = "init_growth",
				inputs=(dict(name="param", interface=None,),),
				outputs=(dict(name="param", interface=None,),),
			)

__all__.append('init_growth')

growth_process1 = Factory( name= "growth1", 
				description= "",
				category = "",
				nodemodule = "growth",
				nodeclass = "growth_process1",
				inputs=(dict(name="param", interface=None,),),
				outputs=(dict(name="process", interface=None,),),
			)

__all__.append('growth_process1')

growth_process2 = Factory( name= "growth2", 
				description= "",
				category = "",
				nodemodule = "growth",
				nodeclass = "growth_process2",
				inputs=(dict(name="param", interface=None,),),
				outputs=(dict(name="process", interface=None,),),
			)

__all__.append('growth_process2')

#########################################
#
#	division
#
#########################################
init_division = Factory( name= "init.division", 
				description= "",
				category = "",
				nodemodule = "division",
				nodeclass = "init_division",
				inputs=(dict(name="param", interface=None,),),
				outputs=(dict(name="param", interface=None,),),
			)

__all__.append('init_division')

division_process = Factory( name= "division", 
				description= "",
				category = "",
				nodemodule = "division",
				nodeclass = "division_process",
				inputs=(dict(name="param", interface=None,),),
				outputs=(dict(name="process", interface=None,),),
			)

__all__.append('division_process')

#########################################
#
#	cell state
#
#########################################
init_cell_state = Factory( name= "init.cell_state", 
				description= "",
				category = "",
				nodemodule = "cell_state",
				nodeclass = "init_cell_state",
				inputs=(dict(name="param", interface=None,),),
				outputs=(dict(name="param", interface=None,),),
			)

__all__.append('init_cell_state')

cell_state_process1 = Factory( name= "cell_state1", 
				description= "",
				category = "",
				nodemodule = "cell_state",
				nodeclass = "cell_state_process1",
				inputs=(dict(name="param", interface=None,),),
				outputs=(dict(name="process", interface=None,),),
			)

__all__.append('cell_state_process1')

cell_state_process2 = Factory( name= "cell_state2", 
				description= "",
				category = "",
				nodemodule = "cell_state",
				nodeclass = "cell_state_process2",
				inputs=(dict(name="param", interface=None,),),
				outputs=(dict(name="process", interface=None,),),
			)

__all__.append('cell_state_process2')

cell_state_process3 = Factory( name= "cell_state3", 
				description= "",
				category = "",
				nodemodule = "cell_state",
				nodeclass = "cell_state_process3",
				inputs=(dict(name="param", interface=None,),),
				outputs=(dict(name="process", interface=None,),),
			)

__all__.append('cell_state_process3')

#########################################
#
#	GUI
#
#########################################
create_gui = Factory( name= "create.gui", 
				description= "",
				category = "",
				nodemodule = "gui",
				nodeclass = "create_gui",
				inputs=(dict(name="param", interface=None,),),
				outputs=(dict(name="sc", interface=None,),
						dict(name="gui", interface=None,),),
			)

__all__.append('create_gui')

redraw_process = Factory( name= "redraw", 
				description= "",
				category = "",
				nodemodule = "gui",
				nodeclass = "redraw_process",
				inputs=(dict(name="sc", interface=None,),),
				outputs=(dict(name="process", interface=None,),),
			)

__all__.append('redraw_process')

init_simulation = Factory( name= "init.simulation", 
				description= "",
				category = "",
				nodemodule = "gui",
				nodeclass = "init_simulation",
				inputs=(dict(name="sc", interface=None,),),
				outputs=(dict(name="func", interface=None,),),
			)

__all__.append('init_simulation')

create_simulation = Factory( name= "create.simulation", 
				description= "",
				category = "",
				nodemodule = "gui",
				nodeclass = "create_simulation",
				inputs=(dict(name="param", interface=None,),
						dict(name="init_func", interface=None,),
						dict(name="process_list", interface=None,),),
				outputs=(dict(name="simu", interface=None,),),
			)

__all__.append('create_simulation')

launch_gui = Factory( name= "launch.gui", 
				description= "",
				category = "",
				nodemodule = "gui",
				nodeclass = "launch_gui",
				inputs=(dict(name="sc", interface=None,),
						dict(name="gui", interface=None,),
						dict(name="simu", interface=None,),
						dict(name="param", interface=None,),),
				outputs=(),
			)

__all__.append('launch_gui')
#########################################
#
#	inout
#
#########################################
create_param = Factory( name= "create.param", 
				description= "",
				category = "",
				nodemodule = "inout",
				nodeclass = "create_param",
				inputs=(),
				outputs=(dict(name="param", interface=None,),),
			)

__all__.append('create_param')

read_tissue = Factory( name= "read.tissue", 
				description= "",
				category = "",
				nodemodule = "inout",
				nodeclass = "read_tissue",
				inputs=(dict(name="name", interface=IFileStr,),
						dict(name="param", interface=None,),),
				outputs=(dict(name="param", interface=None,),),
			)

__all__.append('read_tissue')




