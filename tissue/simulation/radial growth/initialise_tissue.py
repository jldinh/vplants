# -*- python -*-
#
#       simulation.global growth: example simulation package of global growth field
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

from openalea.celltissue import topen

f = topen("tissue.zip",'a')
t,descr = f.read()
cfg = f.read_config("config")

cell_age = dict( (cid,0.) for cid in t.elements(cfg.cell) )

f.write(cell_age,"cell_age","age of cells")
f.close()

