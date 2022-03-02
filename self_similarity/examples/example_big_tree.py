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
from openalea.mtg.mtg import *
import openalea.mtg.aml as aml
import openalea.mtg.plantframe as plantframe
from openalea.mtg import dresser
from openalea.plantgl.all import Viewer
from self_similarity.clustering import *

from self_similarity.graph import *
from self_similarity.cst import *
from self_similarity.mtg2graph import *
from self_similarity.tulip import *

from math import ceil,log

from geometry import *

 
# Need ./SIG.mtg files
mtg_filename = './treeSIGnothin2.mtg'

#g = MTG(mtg_filename)
g= aml.MTG(mtg_filename)

print 'Compute an AML PlantFrame'
# to have complete geometrical information
def diam(x) :
    r = Feature(x,'TopDia')
    if r: return r/2
       
pf = PlantFrame(1,Scale=3,TopDiameter=diam)
    
# retrieve geometrical info from plantframe. For this convert orientation into relative orientation
parameters = compute_geom_parameters(pf,VtxList(Scale=3))

print 'tree <=> MTG'
tree = mtg2graph(3, 3, parameters)
dag_tmp = tree_reduction(tree)
tree_colored = tree_reconstruction_params(dag_tmp)   


### save first file

matrix_filename = 'distmatrix.txt'
matrix_construct(3,matrix_filename)

matrix_params_filename = 'Params.txt'
print_matrix_params(tree, matrix_params_filename,0)

(params,val) = matrix_params_clustering(matrix_params_filename, 1)
rect1 = matrix_clustering_huge_file(matrix_filename,nb_nodes(tree_colored))

# construct the dag
print 'compute dag parent'
dag_parent = cluster_fast2(tree,rect1,params,val,1)

print 'compute treerec'
tree_nest_coCom = tree_reconstruction_params(dag_parent)

graph2mtg(tree_nest_coCom,'initial2.mtg',0)




# output distances by number of class
treeMat = []
linear = []

# NEST method

#graph2mtg(tree_colored,'treeAlrec.mtg',0) 
# Need ./SIG.mtg files
mtg_filename = './initial2.mtg'


#g = MTG(mtg_filename)
g= aml.MTG(mtg_filename)

print 'tree <=> MTG'
tree = mtg2graph_params(2, 2)


print 'Write the distance matrix in matrix_filename'
matrix_filename = 'treeALParams2.txt'
matrix_construct_params_volume(2,matrix_filename)


# Compute reduction with c classes
# 2 classes to exact reduction
max_class = nb_nodes(dag_tmp) 
topolist = [nb_nodes(tree),max_class,max_class-max_class*10/100]

print 'Nb vertices (tree) '+str(nb_nodes(tree))+'\n'
print 'Nb edges (tree) '+str(edge_nb(tree))+'\n'

print 'Nb vertices (DAG) '+str(nb_nodes(dag_tmp))+'\n'
print 'Nb edges (DAG) '+str(edge_nb(dag_tmp))+'\n'


inputSizePA=nb_nodes(tree_colored)*ceil(log(nb_nodes(tree_colored))/log(2))
inputSizeC=nb_nodes(tree_colored)*(4+8+16)

noCompress= tree_reconstruction_params(dag_tmp) 

nb_geo = 2

for i in topolist:
    
    #(params,val) = matrix_params_clustering('SIGParams.txt', nb_geo)
    
    print 'Compute '+str(i)+' classes'
    # cluster
    rect1 = matrix_clustering_huge_file(matrix_filename, i)

    # construct the dag
    ## dag_parent = cluster_fast2(tree,rect1,params,val)
    dag_parent = cluster_fast_params(tree,rect1)
    
    if is_linear(dag_parent):
        linear.append(i)

        
    # final tree
    tree_nest_parent = tree_reconstruction_params(dag_parent)
    print 'nb sign '+str(max_signature_edge(tree_nest_parent))+'\n'
    print 'nb Edge '+ str(edge_nb(dag_parent))+'\n'
    print nb_nodes(dag_parent)

    if i==nb_nodes(tree):
        noCompress=tree_reconstruction_params(dag_parent)
        
    outputPA=edge_nb(dag_parent)*(ceil(log(nb_nodes(dag_parent))/log(2))+ceil(log(max_signature_edge(tree_nest_parent)+1)/log(2)))
    # real save
    maxSize=height_of_graph(tree_nest_parent)
    if height_of_graph(noCompress)>maxSize:
        maxSize=height_of_graph(noCompress)
    graph2mtg(tree_nest_parent,'bigTreeclasses'+str(i)+'.mtg',0,maxSize,1)
    graph2mtg(noCompress,'bigTreeclasses'+str(i)+'.mtg',1,maxSize,1)


        
    # compute distance with tree_matching
    g = MTG('bigTreeclasses'+str(i)+'.mtg')
    

    pre_roots_to_compare=VtxList(Scale=1)
    roots_to_compare=[]
    for j in pre_roots_to_compare:
        roots_to_compare.append(j+1)
    matching = TreeMatching(roots_to_compare,MatchingType='Edition',OrderType='Unordered',MappingType='Global',ScaleType='SingleScale')
    treeMat.append(MatchingExtract(matching,ViewPoint = 'Distance',InputTree=1,ReferenceTree=2)/(nb_nodes(tree_nest_parent)+nb_nodes(noCompress)))

    print 'Compute representation'
    g2 = MTG('bigTreeclasses'+str(i)+'.mtg')
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
    sc.save('FinalSIG'+str(i)+'nbgeo'+str(nb_geo)+'.bgeom')
    Plot(pf)
    Viewer.frameGL.saveImage('InitialSIG.png')
    Viewer.display(sc)
    Viewer.frameGL.saveImage('FinalSIG'+str(i)+'compressionPA'+str(outputPA/inputSizePA)+'compressionC'+str(outputC/inputSizeC)+'.png')
    


    
print '*** End ***'

# end file
