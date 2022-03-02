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
non mandatory file to create a tissue
"""

__license__= "Cecill-C"
__revision__=" $Id: $ "
from openalea.celltissue import topen,Tissue,Config,ConfigItem

t=Tissue()

conf=Config("main")
conf.add_item(ConfigItem("author","jerome"))

f=topen("tissue.zip",'w')
f.write(t)
f.write_config(conf,"config")
f.close()


