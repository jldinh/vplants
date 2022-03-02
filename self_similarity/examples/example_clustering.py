# -*- python -*-
# -*- coding: utf-8 -*-
#
#       Vplants.self_similarity
#
#       Copyright 2010 LaBRI
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

__doc__= "Example to use clustering from self_similarity package"
__docformat__ = "restructuredtext"
__license__= "Cecill-C"
__revision__= "$Id: example_clustering.py 8589 2010-04-06 20:17:42Z gaillard $"


from openalea.aml import *
from self_similarity.clustering import *

from self_similarity.graph import *
from self_similarity.cst import *
from self_similarity.mtg2graph import *


mtg_filename = './example_MTG.mtg'

g = MTG(mtg_filename)

print 'tree <=> MTG'
tree = mtg2graph(1, 2)

print 'Write the distance matrix in matrix_filename'
matrix_filename = 'distmatrix.txt'
matrix_construct(2, matrix_filename)

# output distances by number of class
treeMat = []
linear = []

# NEST method
dag_tmp = tree_reduction(tree)
tree_colored = tree_reconstruction(dag_tmp)   

# Compute reduction with c classes
# 2 classes to exact reduction
max_class = nb_nodes(dag_tmp) + 1
min_class = 2

for i in range(min_class, max_class):
    # cluster
    rect1 = matrix_clustering(matrix_filename, i)

    # construct the dag
    dag_parent = cluster_entropy(tree,rect1)
    
    if is_linear(dag_parent):
        linear.append(i)
        
    # final tree
    tree_nest_parent = tree_reconstruction(dag_parent)

    # real save
    graph2mtg(tree_colored,'classes'+str(i)+'.mtg',0)
    graph2mtg(tree_nest_parent,'classes'+str(i)+'.mtg',1)
    
    # compute distance with tree_matching
    g = MTG('classes'+str(i)+'.mtg')
    roots_to_compare = [v+1 for v in VtxList(Scale=1)]
    matching = TreeMatching(roots_to_compare,MatchingType='Edition',OrderType='Unordered',MappingType='Global',ScaleType='SingleScale')
    mappedVertexList = MatchingExtract(matching,ViewPoint = 'List',InputTree=1,ReferenceTree=2)

    treeMat.append(MatchingExtract(matching,ViewPoint = 'Distance',InputTree=1,ReferenceTree=2))
 
# print the distance between tree and pseudo nest
print 'TREE MATCHING FINAL'

comp = min_class
for i in treeMat:
    print ('Number of class: ' + str(comp) + ' Distance: ' + str(i)+'\n')
    comp += 1 

 
comp = min_class
for i in linear: 
    print "Class "+str(comp)+ " linear? "+str(i)
    comp += 1 
    
