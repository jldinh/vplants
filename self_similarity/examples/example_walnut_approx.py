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

__doc__= 'Example: reduction of walnut with geometry parameters'
__docformat__ = 'restructuredtext'
__license__= 'Cecill-C'
__revision__= '$Id: example_walnut_approx.py 7885 2010-02-09 07:42:56Z cokelaer $'


from openalea.aml import *
from self_similarity.clustering import *

from self_similarity.graph import *
from self_similarity.cst import *
from self_similarity.mtg2graph import *
from self_similarity.tulip import *

from geometry import *

 
# Need ./walnut.mtg files
mtg_filename = './walnut.mtg'

g = MTG(mtg_filename)

print 'Compute an AML PlantFrame'
# to have complete geometrical information
def diam(x) :
    r = Feature(x,'TopDia')
    if r: return r/10
       
pf = PlantFrame(1,Scale=3,TopDiameter=diam)
    
# retrieve geometrical info from plantframe. For this convert orientation into relative orientation
parameters = compute_geom_parameters(pf,VtxList(Scale=3))

# tree <=> MTG
print 'Graph construction'
tree = mtg2graph(3, 3,parameters)

# Write the distance matrix in matrix_filename
print 'Construct matrix'
matrix_filename = 'distmatrix_walnut.txt'
#matrix_construct(matrix_filename, 3)

print 'Write params'
#print_matrix_params(tree,'walnutParams.txt')


#geolist = [115,230,460,920,1840]
geolist=[2]
for nb_geo in geolist:
    
    print 'Compute geo clustering '+str(nb_geo)
    (params,val) = matrix_params_clustering('walnutParams.txt', nb_geo)

    # 920 classes to exact reduction
    classes = [736]

    for i in classes:
        print 'Compute class '+str(i)
        print 'Compute cluster'
        rect1,rect2 = matrix_clustering_entropy(matrix_filename, i)

        print 'Compute DAG'
        dag_parent = cluster_fast_entropy(tree, rect1, rect2,params,val)
        print 'Number of nodes'
        print len(dag_parent.nodes)
        print 'Number of edges'
        print len(dag_parent.edges)
        tree_nest_parent = tree_reconstruction(dag_parent)
        print 'Number of nodes in final'
        print len(tree_nest_parent.nodes)
    
        print 'mtg save'
        graph2mtg(tree_nest_parent,'WalnutEntropy'+str(i)+'nbgeo'+str(nb_geo)+'.mtg',0)

        print 'Compute representation'
        g2 = MTG('WalnutEntropy'+str(i)+'nbgeo'+str(nb_geo)+'.mtg')
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


        sc = compute_representation(Root(vtxlist[0]),get_param2)
        sc.save('FinalWalnut'+str(i)+'nbgeo'+str(nb_geo)+'.bgeom')
        Plot(pf)
        #Viewer.dialog.question('InitialWalnut rep')
        Viewer.frameGL.saveImage('InitialWalnut.png')
        Viewer.display(sc)
        #Viewer.dialog.question('Final rep')
        Viewer.frameGL.saveImage('FinalWalnutEntropy'+str(i)+'nbgeo'+str(nb_geo)+'.png')
    
print '*** End ***'

# end file
