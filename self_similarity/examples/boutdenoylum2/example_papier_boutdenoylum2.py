# -*- python -*-
# -*- coding: utf-8 -*-
#
#       Vplants.self_similarity
#
#       Copyright 2009 LaBRI
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

__doc__= 'Example: compression of young_oak'
__docformat__ = 'restructuredtext'
__license__= 'Cecill-C'
__revision__= '$Id: $'


from openalea.aml import *
from self_similarity.clustering import *

from self_similarity.graph import *
from self_similarity.cst import *
from self_similarity.mtg2graph import *
from self_similarity.tulip import *

 
# Need ./walnut.mtg files
mtg_filename = './boutdenoylum2.mtg'

g = MTG(mtg_filename)

print 'tree <=> MTG'
tree = mtg2graph(3, 3)

print 'Write the distance matrix in matrix_filename'
matrix_filename = 'distmatrix-boutdenoylum2.txt'
matrix_construct(matrix_filename, 3)

# output distances by number of class
treeMat = []
linear = []
nbEdges = []
nbNodes = []
nbSign = []

# NEST method
dag_tmp = tree_reduction(tree)
tree_colored = tree_reconstruction(dag_tmp)
print 'Save tulip file'
print '1'
save_tulip(tree_colored, 'boutdenoylum2tree.tlp')
print '2'
save_tulip(dag_tmp, 'boutdenoylum2_dagexa.tlp')
 

# Compute reduction with c classes
# 2 classes to exact reduction
max_class = nb_nodes(dag_tmp) + 1
#max_class = 12
min_class = 1

for i in range(min_class, max_class):
    print 'Compute '+str(i)+' classes'
    # cluster
    rect1 = matrix_clustering(matrix_filename, i)

    # construct the dag
    dag_parent = cluster_fast(tree,rect1)

    nbNodes.append(nb_nodes (dag_parent))
    nbEdges.append(edge_nb(dag_parent))
    
    print '3'
    save_tulip(dag_parent, 'boutdenoylum2_dagclasses'+str(i)+'.tlp')

    
    if is_linear(dag_parent):
        linear.append(i)
        
    # final tree
    tree_nest_parent = tree_reconstruction(dag_parent)
    nbSign.append(max_signature_edge(tree_nest_parent))

    print '4'
    save_tulip(tree_nest_parent, 'boutdenoylum2_treeclasses'+str(i)+'.tlp')

    # real save
    graph2mtg(tree_colored,'boutdenoylum2treeclasses'+str(i)+'.mtg',0)
    graph2mtg(tree_nest_parent,'boutdenoylum2treeclasses'+str(i)+'.mtg',1)
    
    # compute distance with tree_matching
    g = MTG('boutdenoylum2treeclasses'+str(i)+'.mtg')
    roots_to_compare = [v+1 for v in VtxList(Scale=1)]
    matching = TreeMatching(roots_to_compare,MatchingType='Edition',OrderType='Unordered',MappingType='Global',ScaleType='SingleScale')
    mappedVertexList = MatchingExtract(matching,ViewPoint = 'List',InputTree=1,ReferenceTree=2)

    treeMat.append(MatchingExtract(matching,ViewPoint = 'Distance',InputTree=1,ReferenceTree=2))
 
# print the distance between tree and pseudo nest
print 'TREE MATCHING FINAL'


logfile = open('boutdenoylum2TopoDistance', 'w') 
logfile.write('Number of class: Distance:\n')
comp = min_class
for i in treeMat:
    logfile.write(str(comp) + '\t'+ str(i)+'\n')
    comp += 1 
logfile.close()

logfile2 = open('boutdenoylum2treeTopoLinerar', 'w') 
for i in linear: 
    logfile2.write("Class linear "+str(i)+"\n")
logfile2.close()


logfile3 = open('boutdenoylum2treeNodes', 'w') 
comp = min_class
for i in nbNodes: 
    logfile3.write(str(comp) + '\t'+ str(i)+'\n')
    comp += 1
logfile3.write("intial: "+str(nb_nodes(tree_colored)))  
logfile3.close()

logfile4 = open('boutdenoylum2treeEdges', 'w') 
comp = min_class
for i in nbEdges: 
    logfile4.write(str(comp) + '\t'+ str(i)+'\n')
    comp += 1
logfile4.write("intial: "+str(edge_nb(tree_colored)))    
logfile4.close()

logfile5 = open('agraftreeSignature', 'w+') 
comp = min_class
for i in nbSign: 
    logfile5.write(str(comp) + '\t'+ str(i)+'\n')
    comp += 1  
logfile5.close()
    
print '*** End ***'

# end file
