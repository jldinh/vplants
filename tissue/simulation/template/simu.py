# -*- python -*-
#
#       simulation.template: example simulation package
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
This module launch the simulation
"""

__license__= "Cecill-C"
__revision__=" $Id: $ "

###################################################
#
#	read tissue and properties
#
###################################################
from openalea.celltissue import topen

f = topen("tissue.zip",'r')
t,descr = f.read()
conf = f.read_config("config")
f.close()

###################################################
#
#	processes
#
###################################################
def display_time (time, dt) :
	print conf.author,time

###################################################
#
#	GUI
#
###################################################
from simu_view import SimuView
from simu_gui import SimuGUI

sc = SimuView(vars())
gui = SimuGUI(sc)

###################################################
#
#	simulation loop
#
###################################################
from openalea.pglviewer import QApplication,Viewer
from openalea.pglviewer.data import InfiniteSimu,InfiniteSimuGUI

simu = InfiniteSimu(0.,0.1)
simu.add_process(display_time,"time")

qapp = QApplication([])
v = Viewer()
v.set_world(sc)
v.set_loop(simu)
v.add_gui(InfiniteSimuGUI(simu))
v.add_gui(gui)
v.show()
v.view().show_entire_world()
qapp.exec_()


