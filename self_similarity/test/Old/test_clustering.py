# -*- python -*-
# -*- coding: utf-8 -*-
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


from self_similarity.clustering import *


def test_check_value():
    """ Test value """
    assert check_value(0)==0, 'check_value(0) == %d'%check_value(0)
    assert check_value(1)==1, 'check_value(1) == %d'%check_value(1)
    assert check_value(-1)==0, 'check_value(-1) == %d'%check_value(-1)  
    import sys
    assert check_value(sys.maxint+1)==sys.maxint, 'check_value(sys.maxint+1) == %d'%check_value(sys.maxint+1)
    
    
def test_matrix_construct():
    """ Test the construction of the matrix """
    # to be change without amlPy use.
    mtg_filename = 'exampleMTG.mtg'
    matrix_filename = 'matrix.txt'
    root = 2
    matrix_construct(mtg_filename, matrix_filename, root)
    assert os.path.isfile(matrix_filename)
    assert file = open(matrix_filename)
    assert len(file.readlines())==252, 'len(file.readlines()) == %d'%len(file.readlines())
    l1 = f.readline()
    
    os.remove(name)
 
 
def test_matrix_clustering():
    """ Test  """


def test_div_geo():
    
def test_add_geo():
    
def test_cluster_fast():
    
def test_tree_cpy():
    """ Test  """

    
def test_update_tree_signature():
    """ Test  """

    
def test_select_node_clus():
    """ Test  """

    
def test_tree_reduction_clus_parent():
    """ Test  """

# end file test
