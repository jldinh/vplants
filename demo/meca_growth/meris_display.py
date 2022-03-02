from pglviewer import Viewer
from celltissue.gui import black
from celltissue.simulation import SimuLoop,SimuLoopGUI
from os.path import dirname
from display import Redraw
from meristem_gui import MeristemView2D,MeristemGUI
from growth import Growth
from division import CellDivision
from cell_state import CellState

class RedrawNode(object):
    def __call__(self, *inputs):
        return Redraw(*inputs)

class MeristemView2DNode(object):
    def __call__(self, *inputs):
        return MeristemView2D(*inputs)

class LoopNode(object):
    def __call__(self, *inputs):
        dt,nb_steps=inputs
        return ([dt*i for i in xrange(nb_steps)],)

class SimuLoopNode(object):
    def __call__(self, *inputs):
        return SimuLoop(*inputs)

class SimuGUINode(object):
    def __init__ (self) :
        self.v=Viewer(locals())
        self.v.set_2D()
    def __call__(self, *inputs):
        view,loop=inputs
        view.display_wisp(1,True)
        view.set_wisp_color(1,black)
        loop.run_processes(1e-6)
        # test_strain=[meca.turgor_strain(wid).trace() for wid in t.wisps(0)]
        # view._strain_min=min(test_strain)/1.5
        # view._strain_max=max(test_strain)*1.1
        self.v.set_world(MeristemGUI(view))
        self.v.set_loop(SimuLoopGUI(loop))
        self.v.show()
        self.v.view().show_entire_world()


