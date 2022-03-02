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

#from openalea.qttools import compile_ui,compile_rc,make_menu
import os
from PyQt4 import uic
from openalea.core.path import path

def compile_rc(fn):
    fn = path(fn)
    if fn.ext != '.qrc':
        return
    name = fn.namebase
    out_file = name+'_rc.py'

    os.system("pyrcc4 -o %s %s" % (out_file,fn))

def compile_ui(fn):
    fn = path(fn)
    if fn.ext != '.ui':
        return
    name = fn.namebase
    out_file = name+'_ui.py'

    f = open(out_file,'w')
    uic.compileUi(fn,f)
    f.close()

def make_menu (filename) :
    f=open(filename,'r')
    lines=f.readlines()
    f.close()
    f=open(filename,'w')
    for line in lines :
        if " MainWindow." not in line \
            and "centralwidget" not in line \
            and "        self.menubar" not in line \
            and "statusbar" not in line :
            if "self.menubar" in line :
                f.write(line.replace("self.menubar","MainWindow"))
            elif "QToolBar" in line :
                f.write(line.replace("MainWindow",""))
            else :
                f.write(line)
    f.close()

#compile GUI
uiname=compile_ui("tissue_property_dialog.ui")
uiname=compile_ui("probe_dialog.ui")

#compile GUI
uiname=compile_ui("tissuepainter.ui")
#make_menu(uiname)

#compile rc
rcname=compile_rc("tissuepainter.qrc")

