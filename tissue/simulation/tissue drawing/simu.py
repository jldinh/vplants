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
cfg = f.read_config("config")
pos,descr = f.read("position")
f.close()

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
#	display loop
#
###################################################
from openalea.pglviewer import QApplication,Viewer

qapp = QApplication([])
v = Viewer()
v.set_world(sc)
v.add_gui(gui)
v.show()
v.set_2D()
qapp.exec_()


