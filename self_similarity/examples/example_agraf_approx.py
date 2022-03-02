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

__doc__= 'Example to use clustering from self_similarity package'
__docformat__ = 'restructuredtext'
__license__= 'Cecill-C'
__revision__= '$Id: example_agraf_approx.py 8589 2010-04-06 20:17:42Z gaillard $'


from openalea.aml import *
from self_similarity.clustering import *

from self_similarity.graph import *
from self_similarity.cst import *
from self_similarity.mtg2graph import *
from self_similarity.tulip import *

from geometry import *

# need agraf.mtg file
mtg_filename = './walnut.mtg'

g = MTG(mtg_filename)

print 'Compute an AML PlantFrame'
# to have complete geometrical information
def diam(x) :
    r = Feature(x,'TopDia')
    if r: return r/10
       
pf = PlantFrame(1,Scale=3,TopDiameter=diam)

# Retrieve geometrical info from plantframe.
# For this convert orientation into relative orientation
parameters = compute_geom_parameters(pf,VtxList(Scale=3))

print 'Create graphs'
# MTG and parameters => tree with parameters
tree = mtg2graph(3, 3, parameters)

print 'NEST method'
dag_tmp = tree_reduction(tree)
print 'Number nodes tree'
print nb_nodes(tree)
print 'Number nodes DAG'
print nb_nodes(dag_tmp)


graph2mtg(tree,'agrafInit.mtg',0)
g2 = MTG('agrafInit.mtg')



print 'Write the distance matrix in matrix_filename'
matrix_filename = 'distmatrixagraf.txt'
matrix_construct(2, matrix_filename)


# 543 classes to exact reduction
max_class = 6000
min_class = 5999

for i in range(min_class, max_class):
        
    rect1 = matrix_clustering(matrix_filename, i)

    print 'DAG construction'
    dag_parent = cluster_fast_params(tree, rect1)
    print 'Number of nodes:'
    print len(dag_parent.nodes)
    print 'Number of edges:'
    print len(dag_parent.edges)
  

    print 'Compute reconstruction'
    tree_nest_parent = tree_reconstruction_params(dag_parent)
    print 'Number of nodes in reconstruction'
    print len(tree_nest_parent.nodes)

    print 'Save tulip file'
    #save_tulip(tree_nest_parent, 'Agraf'+str(i)+'g'+str(nb_geo)+'.tlp')
    print 'Save mtg file'
    graph2mtg(tree_nest_parent,'Agraf'+str(i)+'.mtg',0)

    print 'Open MTG'
    g2 = MTG('Agraf'+str(i)+'.mtg')
    # retrieve geometrical info from plantframe. For this convert orientation into relative orientation
    vtxlist = VtxList(Scale=2)

    parameters2 = {}
    parameters2['AnchorT'] ={}
    parameters2['Length'] ={}
    parameters2['Diameter'] ={}
    parameters2['QtOrientation'] = {}
    for v in VtxList(Scale=2):
        parameters2['Diameter'][v]=Feature(v,'Diameter')
        parameters2['Length'][v]=Feature(v,'Length')
        parameters2['AnchorT'][v]=Feature(v,'AnchorT')

        val_quater = Quaternion(Feature(v,'Q1'),Feature(v,'Q2'),Feature(v,'Q3'),Feature(v,'Q4'))
        parameters2['QtOrientation'][v]=val_quater

    def get_param2(v,paramname): return parameters2[paramname][v]

    print 'Compute representation'
    sc = compute_representation(Root(vtxlist[0]),get_param2)
    sc.save('AgrafInitial.bgeom')
    Plot(pf)
    Viewer.frameGL.saveImage('AgrafInitial.png')
    Viewer.display(sc)
    Viewer.frameGL.saveImage('Agraf'+str(i)+'.png')

print '*** End ***'

# end file
