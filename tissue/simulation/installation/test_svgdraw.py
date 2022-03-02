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
This module test the installation of svgdraw
"""

__license__= "Cecill-C"
__revision__=" $Id: $ "

###################################################
#
#	read tissue and properties
#
###################################################
from openalea.svgdraw import open_svg

f = open_svg("test.svg",'r')
sc = f.read()
f.close()

layer = sc.get_layer("calque")

for elm in layer :
	print elm


