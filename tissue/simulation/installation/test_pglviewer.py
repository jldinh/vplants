# -*- python -*-
#
#       simulation.installation: installation tutorial package
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
This module test the installation of pglviewer
"""

__license__= "Cecill-C"
__revision__=" $Id: $ "

###################################################
#
#	read tissue and properties
#
###################################################
from openalea.pglviewer import QApplication,Viewer
from openalea.pglviewer.data import InfiniteSimu,InfiniteSimuGUI

def reinit () :
	print "reinit"

def process (time, dt) :
	print "time: %.1f" % time

simu = InfiniteSimu(0.,0.1)
simu.set_initialisation(reinit)
simu.add_process(process,"process")

qapp = QApplication([])
v = Viewer()
v.set_loop(simu)
v.add_gui(InfiniteSimuGUI(simu))
v.show()
qapp.exec_()

