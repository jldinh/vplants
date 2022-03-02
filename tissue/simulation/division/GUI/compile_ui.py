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
This module intialise the tissue with all needed properties
"""

__license__= "Cecill-C"
__revision__=" $Id: $ "

from shutil import move
from openalea.qttools import compile_ui,compile_rc

#compile GUI
uiname=compile_ui("simu.ui")
move(uiname,"..")

#compile rc
rcname=compile_rc("simu.qrc")
move(rcname,"..")

