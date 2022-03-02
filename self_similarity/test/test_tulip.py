# -*- python -*-
#
#       VPlants.Self_Similarity: Test package
#
#       Copyright 2010 Labri  
#
#       File author(s): Anne-Laure Gaillard <anne-laure.gaillard@labri.fr>
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
# 
#       OpenAlea WebSite : http://openalea.gforge.inria.fr
#
################################################################################

__doc__="""
Self Similarity unit tests
"""

__license__= "Cecill"
__revision__=" $Id"


from self_similarity.tulip import *


def test_save_tulip():
    """ Test file creation """
    name = "./test_to_delete.tlp"
    graph = 0
    save_tulip(graph,name)
    assert(os.path.isfile(name))
    os.remove(name)
    
    
def test_blue_color_vertex():
    """ Test blue coloration """
    assert blue_color_vertex(1,1) == 0, 'blue_color_vertex(1,1) == %d'%blue_color_vertex(1,1)
    assert blue_color_vertex(1,2) == 255, 'blue_color_vertex(1,2) == %d'%blue_color_vertex(1,2)
    assert blue_color_vertex(2,2) == 0, 'blue_color_vertex(2,2) == %d'%blue_color_vertex(2,2)
    assert blue_color_vertex(1,3) == 0, 'blue_color_vertex(1,3) == %d'%blue_color_vertex(1,3)
    assert blue_color_vertex(2,3) == 255, 'blue_color_vertex(2,3) == %d'%blue_color_vertex(2,3)
 
 
def test_green_color_vertex():
    """ Test green coloration """
    assert green_color_vertex(1,1) == 0, 'green_color_vertex(1,1) == %d'%green_color_vertex(1,1)
    assert green_color_vertex(1,2) == 255, 'green_color_vertex(1,2) == %d'%green_color_vertex(1,2)
    assert green_color_vertex(2,2) == 0, 'green_color_vertex(2,2) == %d'%green_color_vertex(2,2)
    assert green_color_vertex(1,3) == 255, 'green_color_vertex(1,3) == %d'%green_color_vertex(1,3)
    assert green_color_vertex(2,3) == 0, 'green_color_vertex(2,3) == %d'%green_color_vertex(2,3)
    
    
def test_red_color_vertex():
    """ Test red coloration """
    assert red_color_vertex(1,1) == 255, 'red_color_vertex(1,1) == %d'%red_color_vertex(1,1)
    assert red_color_vertex(1,2) == 0, 'red_color_vertex(1,2) == %d'%red_color_vertex(1,2)
    assert red_color_vertex(2,2) == 255, 'red_color_vertex(2,2) == %d'%red_color_vertex(2,2)
    assert red_color_vertex(1,3) == 0, 'red_color_vertex(1,3) == %d'%red_color_vertex(1,3)
    assert red_color_vertex(2,3) == 0, 'red_color_vertex(2,3) == %d'%red_color_vertex(2,3)

# end file test
