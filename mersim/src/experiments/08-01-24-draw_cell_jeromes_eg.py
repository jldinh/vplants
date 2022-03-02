#!/usr/bin/env python
"""<Short description of the module functionality.>

<Long description of the module functionality.>

:todo:
    Nothing.

:bug:
    None known.
    
:organization:
    INRIA

"""
# Module documentation variables:
__authors__="""Szymon Stoma    
"""
__contact__=""
__license__="Cecill-C"
__date__="<Timestamp>"
__version__="0.1"
__docformat__= "restructuredtext en"
__revision__="$Id: 08-01-24-draw_cell_jeromes_eg.py 7875 2010-02-08 18:24:36Z cokelaer $"

from openalea.plantgl.math import Vector3,Vector4
from openalea.plantgl.scenegraph import Color4,Shape,Material
import openalea.plantgl.all as pgl
#from openalea.pglviewer import QApplication,Viewer
#from openalea.pglviewer.data import SceneView,SceneGUI
#from openalea.pglviewer.data import SimuLoop,SimuLoopGUI
from openalea.mersim.gui.draw_cell import draw_cell

# The ovrlapping walls
sh=0.3
cell_pts=[Vector3(1,1,0),Vector3(-1,1*sh,0),Vector3(-1,-1*sh,0),Vector3(1,-1,0)]
wall_th=[0.2,0.,0.2,0.]

#cell_pts=[Vector3(1.,1.,0.),Vector3(0.,1.01,0.),Vector3(-1.,1.,0.),Vector3(-1.,-1.,0.),Vector3(1.,-1.,0.)]
#wall_th=[0.1,0.,0.,0.,0.]


th_min=0.1
th_max=1.5
cell_col=Color4(0,160,0,0)
wall_col=Color4(0,0,0,0)
pump_col=Color4(200,0,0,0)


stride=20#sup than len(cell)*(nb_ctrl_pts+2)
nb_ctrl_pts=3
mat=Material( (0,0,0) )

scv=pgl.Scene()
mesh=draw_cell(cell_pts,wall_th,th_min,th_max,cell_col,wall_col,pump_col,stride,nb_ctrl_pts,None)
scv.add(Shape(mesh,mat))
#mesh2=draw_cell(cell2_pts,[0.]*5,th_min*3,th_max,cell_col,wall_col,pump_col,stride,nb_ctrl_pts,None)
#scv.add(Shape(mesh2,mat))
#mesh3=draw_cell(cell3_pts,[0.]*5,th_min*4,th_max,cell_col,wall_col,pump_col,stride,nb_ctrl_pts,None)
#scv.add(Shape(mesh3,mat))


pgl.Viewer.display( scv )
pgl.Viewer.start()
#qapp=QApplication([])
#v=Viewer(locals())
#v.set_world(SceneGUI(scv))
#v.show()
#v.view().show_entire_world()
#qapp.exec_()