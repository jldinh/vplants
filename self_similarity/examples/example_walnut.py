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

__doc__= 'Example to use cst from self_similarity package'
__docformat__ = 'restructuredtext'
__license__= 'Cecill-C'
__revision__= '$Id: example_walnut.py 8770 2010-04-28 20:49:14Z gaillard $'

# for mac usage
import sys
sys.path.append('../src/self_similarity')

from amlPy import *

from graph import *
from tulip import *
from cst import *
from mtg2graph import *


# Need ./walnut.mtg file
mtg_filename = './walnut.mtg'

g = MTG(mtg_filename)

print 'Create the graph'
tree = mtg2graph(4, 3)
print 'Number node tree '+str(nb_nodes(tree))


print 'Compute reduction'
dag_exact = tree_reduction(tree)
print 'Number nodes DAG '+str(nb_nodes(dag_exact))
print 'Number edges DAG '+str(edge_nb(dag_exact))

tree_rec = tree_reconstruction(dag_exact)
print tree_rec.max_signature_edge
print tree_rec.sum_signature_edge

save_tulip(tree_rec,'walnutrec.tlp')


exits
print 'Compute linearization'
dag_linearization(dag_exact)

print 'Number node line '+str(nb_nodes(dag_exact))

print 'Compute reconstruction could be long... Be patient'
nest = tree_reconstruction(dag_exact)


save_tulip(nest,'walnut.tlp')

print 'Write the trees in a mtg file'
graph2mtg(tree_rec,'example_distance.mtg',0)
graph2mtg(nest,'example_distance.mtg',1)
    
print 'Compute distance with tree_matching'
g = MTG('example_distance.mtg')
roots_to_compare = [v+1 for v in VtxList(Scale=1)]
matching = TreeMatching(roots_to_compare,MatchingType='Edition',OrderType='Unordered',MappingType='Global',ScaleType='SingleScale')
mappedVertexList = MatchingExtract(matching,ViewPoint = 'List',InputTree=1,ReferenceTree=2)

print 'Distance: '
print MatchingExtract(matching,ViewPoint = 'Distance',InputTree=1,ReferenceTree=2)

print '*** End ***'

# end file
