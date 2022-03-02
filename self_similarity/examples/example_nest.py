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
__revision__= '$Id: example_nest.py 8589 2010-04-06 20:17:42Z gaillard $'


from amlPy import *

from vplants.self_similarity.graph import *
from self_similarity.cst import *
from self_similarity.mtg2graph import *

mtg_filename = './example_MTG.mtg'

g = MTG(mtg_filename)

print 'Create the graph'
tree = mtg2graph(1, 2)

print 'Reduction'
dag_exact = tree_reduction(tree)
tree_rec = tree_reconstruction(tree)

print 'Linearization'
dag_linearization(dag_exact)

print 'Reconstruction'
nest = tree_reconstruction(dag_exact)


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

# end file
