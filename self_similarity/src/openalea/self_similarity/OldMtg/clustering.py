# -*- python -*-
# -*- coding: utf-8 -*-
#
#       Vplants.Self_similarity: Self_similarity tools package
#
#       Copyright 2010 LaBRI
#
#       File author: Anne-Laure Gaillard <anne-laure.gaillard@labri.fr>
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
# 
#       OpenAlea WebSite : http://openalea.gforge.inria.fr
#
################################################################################

'''
Clustering tools for the approximation self_similarity method.
'''

__license__= "Cecill-C"
__revision__=" $Id: clustering.py 17111 2014-07-09 15:42:49Z azais $ "
__docformat__ = "restructuredtext en"

# for mac usage
import sys
sys.path.append('../src/self_similarity')

# for treeMatching
from openalea.aml import *
# manipulation of structure
from graph import *

# for matrix creation treeeMatching2
#from openalea.tree_matching import *
""" Problem import does not work! """

# for clustering
#import rpy2.rpy_classic as rpy
#import rpy2.rpy_classic as r
from rpy import *

def matrix_construct_clustering(root, matrix_filename, nb_class=2):
    """
    Clustering distance matrix from a matrix_filename file with method_tool
    algorithm.
    Selection of nb_class in the clustering.
    Returns the python object with the classes.

    Usage
    -----
    .. python ::
        matrix_clustering(matrix_filename, nb_class, method_tool)

    Parameters
    ----------
        - `matrix_filename` (str): name of the distance matrix file.
        - `nb_class` (int): the number of classes in final classification.
        - `method_tool` (str): name of the clustering method.
        the agglomeration method to be used. This should be (an unambiguous
        abbreviation of) one of "ward", "single", "complete", "average",
        "mcquitty", "median" or "centroid".
        
    Returns
    -------
        A Python dict with the clusters.

    Details
    -------
        The clustering process is done with Rpy.
        If nb_class < 2 or nb_class > size(matrix) Rpy exception.
    """
    assert os.path.isfile(matrix_filename), 'Error file matrix '+str(matrix_filename)
    
    # self-similar matching
    m = TreeMatching([root])
    # save the matrix
    print 'MatchingExt'
    mat = MatchingExtract(m, ViewPoint="DistanceMatrix")
    print 'Clustering'
    clus = Clustering(mat, "Hierarchy",Algorithm="Agglomerative")
    print 'Fin Clustering'
    
    print clus



    
    return 

            
def matrix_construct(root, matrix_file='dist_matrix.txt'):
    """ Construct a distance matrix.
    
    Construct a distance matrix with Zhang algorithm from an open mtg file and
    write it in a file.

    Usage
    -----
      matrix_construct(matrix_file, root)

    :Parameters:
      - `root` (int): the root's id in the mtg.
      - `matrix_file` (str): name of the distance matrix file (output).
        
    :Returns:
      None.
        
    :Examples:
      from openalea.aml import *
      mtg_filename = '../example/agraf.mtg'
      g = MTG(mtg_filename)
      tree = mtg2graph(3, 3)
      matrix_construct(3)
      
    .. warning:: Must have an open MTG, use amlPy,
                 need written permission in matrix_filename path.
    ------------
    
    .. todo:: Do not use amlPy.
    ---------
        
    """  
    # self-similar matching
    m = TreeMatching([root])
    # save the matrix
    MatchingExtract(m, ViewPoint="saveDistanceMatrix", FileName=matrix_file)

           
def matrix_construct_params(root, matrix_file='dist_matrix.txt', vecto_numeric=[]):
    """ Construct a distance matrix.
    
    Construct a distance matrix with Zhang algorithm from an open mtg file and
    write it in a file.

    Usage
    -----
     matrix_construct_params(root, matrix_file, vecto_numeric)

    :Parameters:
      - `root` (int): the root's id in the mtg.
      - `matrix_file` (str): name of the distance matrix file (output).
      - `vector_numeric` (tabular): numeric values of attributs.
        
    :Returns:
      None.
        
    :Examples:
      from openalea.aml import *
      mtg_filename = '../example/agraf.mtg'
      g = MTG(mtg_filename)
      tree = mtg2graph(3, 3)
      matrix_filename = 'distmatrixagraf.txt'
      matrix_construct(matrix_filename, 3)
      
    .. warning:: Must have an open MTG, use amlPy,
                 need written permission in matrix_filename path.
    ------------
    
    .. todo:: Do not use amlPy.
    ---------
        
    """
    # diam, long, Q1 to Q4 required
    def diam(x):
        return Feature(x,"Diameter")
    def long(x):
        return Feature(x,"Length")
    def Q1(x):
        return Feature(x,"Q1")
    def Q2(x):
        return Feature(x,"Q2")
    def Q3(x):
        return Feature(x,"Q3")
    def Q4(x):
        return Feature(x,"Q4")

    # numeric values can be modified... now in the code
    if vecto_numeric==[]:
        VectoDist = VectorDistance(.3,'NUMERIC',.3,'NUMERIC',.1,'NUMERIC',
                                    .1,'NUMERIC',.1,'NUMERIC',.1,'NUMERIC',
                                    Distance='QUADRATIC')
    else:
        VectoDist = VectorDistance(vecto_numeric[0],'NUMERIC',vecto_numeric[1],'NUMERIC',
                                   vecto_numeric[2],'NUMERIC',vecto_numeric[3],'NUMERIC',
                                   vecto_numeric[4],'NUMERIC',vecto_numeric[5],'NUMERIC',
                                    Distance='QUADRATIC')

    func = [diam, long, Q1, Q2, Q3, Q4]
    match = TreeMatching([root], MatchingType='by_weights',
                              FuncList=func, VectorDistance=VectoDist)

    # save the distance
    MatchingExtract(match, ViewPoint="saveDistanceMatrix", FileName=matrix_file)
        
        
def matrix_construct_params_volume(root, matrix_file='dist_matrix.txt', vecto_numeric=[]):
    """ Construct a distance matrix.
    
    Construct a distance matrix with Zhang algorithm from an open mtg file and
    write it in a file.

    Usage
    -----
     matrix_construct_params(root, matrix_file, vecto_numeric)

    :Parameters:
      - `root` (int): the root's id in the mtg.
      - `matrix_file` (str): name of the distance matrix file (output).
      - `vector_numeric` (tabular): numeric values of attributs.
        
    :Returns:
      None.
        
    :Examples:
      from openalea.aml import *
      mtg_filename = '../example/agraf.mtg'
      g = MTG(mtg_filename)
      tree = mtg2graph(3, 3)
      matrix_filename = 'distmatrixagraf.txt'
      matrix_construct(matrix_filename, 3)
      
    .. warning:: Must have an open MTG, use amlPy,
                 need written permission in matrix_filename path.
    ------------
    
    .. todo:: Do not use amlPy.
    ---------
        
    """
    # diam, long, Q1 to Q4 required
    def diam(x):
        return Feature(x,"Diameter")*Feature(x,"Length")

    # numeric values can be modified... now in the code
    if vecto_numeric==[]:
        VectoDist = VectorDistance(1.0,'NUMERIC',
                                    Distance='QUADRATIC')
    else:
        VectoDist = VectorDistance(vecto_numeric[0],'NUMERIC',vecto_numeric[1],'NUMERIC',
                                   vecto_numeric[2],'NUMERIC',vecto_numeric[3],'NUMERIC',
                                   vecto_numeric[4],'NUMERIC',vecto_numeric[5],'NUMERIC',
                                    Distance='QUADRATIC')

    func = [diam]
    match = TreeMatching([root], MatchingType='by_weights',
                              FuncList=func, VectorDistance=VectoDist)

    # save the distance
    MatchingExtract(match, ViewPoint="saveDistanceMatrix", FileName=matrix_file)
           
#######
# IMPORT DOES NOT WORK!
#######         
def matrix_construct_treeMatching2(matrix_file, scalep, rootp):
    """ Construct a distance matrix.
    
    Construct a distance matrix with Zhang algorithm from a tree and
    write it in a file.

    Usage
    -----
      mtg2graph(scale, root, parameters)

    :Parameters:
      - `matrix_file` (str): name of the distance matrix file (output).
        
    :Returns:
      The c_graph relative to the MTG file.
        
    :Examples:
      from openalea.aml import *
      mtg_filename = '../example/agraf.mtg'
      g = MTG(mtg_filename)
      tree = mtg2graph(3, 3)
      
    .. warning:: NOT YET IMPLEMENTED,
                 need written permission in matrix_filename path.
    ------------
    
    .. todo:: THIS METHOD!
    ---------
        
    """    
    
    tree = mtg2TreeGraph(scale=scalep, root=rootp)

    # topological cost only
    node_cost = NodeCost("Topology")
    
    # self-similar matching
    m = Matching(tree, tree, node_cost)

    # save the matrix
    MatchingExtract(m, ViewPoint="saveDistanceMatrix", FileName=matrix_file)


def matrix_clustering_huge_file(matrix_filename, nb_class=2, method_tool='ward'):
    """
    Clustering distance matrix from a matrix_filename file with method_tool
    algorithm.
    Selection of nb_class in the clustering.
    Returns the python object with the classes.

    Usage
    -----
    .. python ::
        matrix_clustering(matrix_filename, nb_class, method_tool)

    Parameters
    ----------
        - `matrix_filename` (str): name of the distance matrix file.
        - `nb_class` (int): the number of classes in final classification.
        - `method_tool` (str): name of the clustering method.
        the agglomeration method to be used. This should be (an unambiguous
        abbreviation of) one of "ward", "single", "complete", "average",
        "mcquitty", "median" or "centroid".
        
    Returns
    -------
        A Python dict with the clusters.

    Details
    -------
        The clustering process is done with Rpy.
        If nb_class < 2 or nb_class > size(matrix) Rpy exception.
    """
    assert os.path.isfile(matrix_filename), 'Error file matrix '+str(matrix_filename)
    
    os.system("R --arch x86_64 -f test.r "+str(matrix_filename)+' '+str(nb_class)+' '+str(method_tool))

    rect = {}
    f = open('file.csv','r')
    for line in f.readlines() :
        data = line.split()
        rect[data[0]] = data[1]
    print rect
    return rect


def matrix_clustering(matrix_filename, nb_class=2, method_tool='ward'):
    """
    Clustering distance matrix from a matrix_filename file with method_tool
    algorithm.
    Selection of nb_class in the clustering.
    Returns the python object with the classes.

    Usage
    -----
    .. python ::
        matrix_clustering(matrix_filename, nb_class, method_tool)

    Parameters
    ----------
        - `matrix_filename` (str): name of the distance matrix file.
        - `nb_class` (int): the number of classes in final classification.
        - `method_tool` (str): name of the clustering method.
        the agglomeration method to be used. This should be (an unambiguous
        abbreviation of) one of "ward", "single", "complete", "average",
        "mcquitty", "median" or "centroid".
        
    Returns
    -------
        A Python dict with the clusters.

    Details
    -------
        The clustering process is done with Rpy.
        If nb_class < 2 or nb_class > size(matrix) Rpy exception.
    """
    assert os.path.isfile(matrix_filename), 'Error file matrix '+str(matrix_filename)
    
    # R tools
    set_default_mode(NO_CONVERSION)

    # Reading and clustering with Rpy
    a = read_table(matrix_filename)
    mydist = as_dist(a)
    
    # Make classes
    clust = hclust(mydist, method=method_tool)

    # Converts R object to Python dict
    set_default_mode(BASIC_CONVERSION)
    rect = cutree(clust, k=nb_class)
    return rect


def print_matrix_params(tree, matrix_filename,orientation=1):
    """
    Write in matrix_filename 
    Usage
    -----
    .. python ::
        print_matrix_params(tree, matrix_filename,orientation)

    Parameters
    ----------
        - `tree` ():
        - `matrix_filename` ():
        - `orientation` ():
        
    Returns
    -------


    Details
    -------

    """
    # delete the old file if exists
    try:
        source = open(matrix_filename,'w')
    except IOError:
        sys.exit('Could not create '+ matrix_filename)    

    i = 0
    for n in tree.nodes:
        source.write(n.parameters.print_params(0))
        i+=1
        
    source.close()


# ???????????????
# ENCORE UTILE ? VERIFIER AVEC LES NOUVEAUX PARAMS
def print_matrix_orient(dicto, matrix_filename):
    """
    """
    # delete the old file if exists
    try:
        source = open(matrix_filename,'w')
    except IOError:
        sys.exit('Could not create '+ matrix_filename)    

    #print 'here'+str(dicto)
    comp=0
    for i in dicto:
        #print i+'iiiiii'
        source.write(i.print_params_orient())
        #print i
        #if i == 'QtOrientation':
        #    for j in range[4]:
        #source.write(str(i)+'\t')
        #comp+=1
        #if comp%4==0:
        #    source.write('\n')
    
    source.close()
    

# ???????????????
# ENCORE UTILE ? VERIFIER AVEC LES NOUVEAUX PARAMS
def matrix_params_clustering(matrix_filename, nb_class=4):
    """
    Clustering distance matrix from a matrix_filename file with method_tool
    algorithm.
    Selection of nb_class in the clustering.
    Returns the python object with the classes.

    Usage
    -----
    .. python ::
        matrix_clustering(matrix_filename, nb_class)

    Parameters
    ----------
        - `matrix_filename` (str): name of the distance matrix file.  
        - `nb_class` (int): the number of classes in final classification.      
    Returns
    -------
        A Python dict with the clusters and centers.

    Details
    -------
        The clustering process is done with Rpy.
    """
    assert os.path.isfile(matrix_filename), 'Error file '+matrix_filename

    if nb_class>1:
        try:
            # R tools
            rpy.set_default_mode(rpy.NO_CONVERSION)
            data = rpy.r.read_table(matrix_filename)
            # no inf/non/...
            rpy.set_default_mode(rpy.BASIC_CONVERSION)
            # data,nbclass,maxit,nbinit

            print '********************start'
            print nb_class
            print data
            print 'end********************'
            clust = rpy.r.kmeans(data,nb_class)

            return (clust[0], clust[1])
        finally:
            clust={}
            clust['cluster']=[]
            clust['centers']=[]
            f=open(matrix_filename,'r')
            i=0
            for l in f.readlines():
                clust['cluster'].append(1)
                clust['centers'].append(l)
                i+=1
            
            return (clust['cluster'], clust['centers'])
    else:
        clust={}
        clust['cluster']=[]
        clust['centers']=[]
        f=open(matrix_filename,'r')
        i=0
        for l in f.readlines():
            clust['cluster'].append(1)
            clust['centers'].append(l)
            i+=1
            
        return (clust['cluster'], clust['centers'])
  

def cluster_fast(tree, rect):   
    """
    For a given c_graph(), classification
    create the DAG without save and tree intermediate.

    Usage
    -----
    .. python ::
        cluster_fast(tree, rect)

    Parameters
    ----------
        - `tree` (c_graph): the tree to update.
        - `rect` (dict): a Python dict with the clusters.
        
    Returns
    -------
        A new c_graph the reduction.

    Details
    -------

    """
    # new dag
    dag = c_graph()
    # position of the signature
    signature_pos = {}
    position = 0
    # edges number
    edges = {}
    child = {}
    
    for n in tree.nodes:
        # the vertex cluster
        num = int(n.label)
        vvid = 'V'+str(int(num+1))
        clus = int(rect[vvid])

        # first time with this signature
        if not signature_pos.has_key(clus):
        
            signature_pos[clus] = position

            # create a node in the DAG
            n_i = make_node('I'+str(position)) 
            n_i.signature = position
            dag.nodes += [n_i]

            # create edge dict
            edges[position] = {}
            child[position] = n

            position += 1

        
        #print signature_pos[clus]
        current_pos = signature_pos[clus]
        n.signature = current_pos

        if child[current_pos] == n:
            # take edges
            for j in range(nb_edges(n)):
                e = edge(n, j)
                # if output edge
                if e.start==n:
                    position_clus_end = e.end.signature
                    # not same cluster
                    if current_pos != position_clus_end:
                        if not edges[current_pos].has_key(position_clus_end):
                            edges[current_pos][position_clus_end] = 1
                        else:
                            edges[current_pos][position_clus_end] += 1
                            
                          
          
    for clust_in in edges:
        for clust_out in edges[clust_in]:
            e_i = make_edge(node(dag,clust_in),node(dag,clust_out),edges[clust_in][clust_out])
            dag.edges += [e_i]
            
            
    dag.nb_signature = position
    return dag  


def cluster_entropy(tree, rect):   
    """
    

    Usage
    -----
    .. python ::
        cluster_entropy(tree, rect, params, centers)

    Parameters
    ----------
        
    Returns
    -------
        A new c_graph the reduction.

    Details
    -------

    """
    # new dag
    dag = c_graph()
    # position of the signature
    signature_pos = {}
    position = 0
    # edges number
    edges = {}
    child = {}
    
    for n in tree.nodes:
        # the vertex cluster
        num = int(n.label)
        vvid = 'V'+str(int(num+1))
        clus = int(rect[vvid])

        # first time with this signature
        if not signature_pos.has_key(clus):
        
            signature_pos[clus] = position

            # create a node in the DAG
            n_i = make_node('I'+str(position)) 
            n_i.signature = position
            dag.nodes += [n_i]

            # create edge dict
            edges[position] = {}
            child[position] = []

            position += 1

        current_pos = signature_pos[clus]
        n.signature = current_pos
        child[current_pos].append(n)

    # the more frequent 
    for position in child:
        
        current_pos = position
        all_edges = {}
        
        for n in child[current_pos]:
            all_edges[n]=[]
            # take edges
            for j in range(nb_edges(n)):
                e = edge(n, j)
                # if output edge
                if e.start==n:
                    position_clus_end = e.end.signature
                    # not same cluster
                    if current_pos != position_clus_end:
                       all_edges[n].append(position_clus_end)
            # leaf to add in class
            if nb_edges(n)==1:
                all_edges[n].append(-1)
            all_edges[n].sort()

        # more frequent subtree    
        res = []
        more_freq = 0
        list_freq = {}
        res_list_freq = []
        for n1 in all_edges:
            if len(all_edges[n1])>0:
                if all_edges[n1] in res:
                    index_res = res.index(all_edges[n1])
                    list_freq[index_res] += 1  
                else:
                    res.append(all_edges[n1])
                    index_res = len(res)-1
                    list_freq[index_res] = 1
                # the more frequent if equal the one with the max len
                if list_freq[index_res] > more_freq:
                    more_freq = list_freq[index_res]
                    res_list_freq = res[index_res]
                elif list_freq[index_res] == more_freq:
                    if len(res[index_res])>len(res_list_freq):
                        more_freq = list_freq[index_res]
                        res_list_freq = res[index_res]
        
        # compute number of edges    
        for position_clus_end in res_list_freq:
            if not position_clus_end==-1:    
                if not edges[current_pos].has_key(position_clus_end):
                    edges[current_pos][position_clus_end] = 1
                else:
                    edges[current_pos][position_clus_end] += 1
                            
                          
          
    for clust_in in edges:
        for clust_out in edges[clust_in]:
            e_i = make_edge(node(dag,clust_in),node(dag,clust_out),edges[clust_in][clust_out])
            dag.edges += [e_i]
            
            
    dag.nb_signature = position
    return dag




def merge_edge_moy(dic):
    dicto = {}
    nb=0
    dicto[nb]={}
    comp=0
    for z in dic:
        for k in z.keys():
            # float merging
            if k == 'QtOrientation':
                if comp==0:
                    comp = 1
                    dicto[nb] = z[k]
                elif not comp == 1:
                        dicto[nb] = Quaternion.slerp(dicto[nb], z[k], comp)
                comp /= 2
    return dicto

    

def merge_edge_moy_para(matrix_filename,rect):
    f=open(matrix_filename,'r')
    dicto = {}
    w=0
        
    comp={}
    for z in f.readlines():
            
        t=z.split()
        q=Quaternion(float(t[0]),float(t[1]),float(t[2]),float(t[3]))
        if not comp.has_key(rect[w]-1):
            comp[rect[w]-1] = 1
            dicto[rect[w]-1] = q
        elif not comp[rect[w]-1] == 1:
                dicto[rect[w]-1] = Quaternion.slerp(dicto[rect[w]-1],q, comp[rect[w]-1])
        comp[rect[w]-1] /= 2
        w+=1

    return dicto          

def cluster_fast_params(tree, rect):   
    """
    For a given c_graph(), classification
    create the DAG without save and tree intermediate.

    Usage
    -----
    .. python ::
        cluster_fast_params(tree, rect)

    Parameters
    ----------
        - `tree` (c_graph): the tree to update.
        - `rect` (dict): a Python dict with the clusters.
        
    Returns
    -------
        A new c_graph the reduction.

    Details
    -------

    """
    # new dag
    dag = c_graph()
    # position of the signature
    signature_pos = {}
    position = 0
    # edges number
    edges = {}
    child = {}
    edgeOrient = {}
    edgesO = {}
    # for parametersmetry
    parametersvar = {}
    
    for n in tree.nodes:
        # the vertex cluster
        num = int(n.label)
        vvid = 'V'+str(int(num+1))
        clus = int(rect[vvid])

        # first time with this signature
        if not signature_pos.has_key(clus):
        
            signature_pos[clus] = position

            # create a node in the DAG
            n_i = make_node('I'+str(position)) 
            n_i.signature = position
            dag.nodes += [n_i]

            parametersvar[position] = parameter_manipulator2()
            for k in n.parameters.keys():
                parametersvar[position][str(k)] = []
                parametersvar[position][str(k)].append(n.parameters[k])
            
            # create edge dict
            edges[position] = {}
            child[position] = n

            position += 1
            
            current_pos = signature_pos[clus]
            n.signature = current_pos

        else:
            
            #print signature_pos[clus]
            current_pos = signature_pos[clus]
            n.signature = current_pos
            
            for k in n.parameters.keys():
                parametersvar[current_pos][str(k)].append(n.parameters[k])
            
            

        if child[current_pos] == n:
            # take edges
            for j in range(nb_edges(n)):
                e = edge(n, j)
                # if output edge
                if e.start==n:
                    position_clus_end = e.end.signature
                    # not same cluster
                    if current_pos != position_clus_end:
                        if not edges[current_pos].has_key(position_clus_end):
                            edges[current_pos][position_clus_end] = 1
                        else:
                            edges[current_pos][position_clus_end] += 1
                            
       
        
    for e in tree.edges:
        startDag=e.start.signature
        endDag=e.end.signature
        if not edgesO.has_key(startDag):
            edgesO[startDag]={}
        if not edgesO[startDag].has_key(endDag):
            edgesO[startDag][endDag] = []
        edgesO[startDag][endDag].append(e.end.parameters)
        
    
    for clus in parametersvar:
        n_i = node(dag, clus)
        n_i.parameters.data = parametersvar[clus].merge_vertex()
        if clus==0:
            n_i.parameters.data = parametersvar[clus].merge()
          
    for clust_in in edges:
        for clust_out in edges[clust_in]:
            e_i = make_edge(node(dag,clust_in),node(dag,clust_out),edges[clust_in][clust_out])
            dag.edges += [e_i]
            if not edgeOrient.has_key(e_i):
                edgeOrient[e_i] = []
            edgeOrient[e_i]=edgesO[clust_in][clust_out]
            


    for i in range(nb_nodes(dag)):
        n_i = node(dag, i)
        for j in range(nb_edges(n_i)):
            e = edge(n_i, j)
            if e.end==n_i:
                
                matrix_filename="QtOrientation.txt"

                if e.label>1:
                    print_matrix_orient(edgeOrient[e], matrix_filename)
 
                    (rect1,rect2)=matrix_params_clustering(matrix_filename, e.label)
   
                    e.parameters.data = merge_edge_moy_para(matrix_filename,rect1)
                else:
                    print_matrix_orient(edgeOrient[e], matrix_filename)
                    (rect1,rect2)=matrix_params_clustering(matrix_filename, e.label)
                    e.parameters.data = merge_edge_moy_para(matrix_filename,rect1)
                print e.parameters.data  
   
            
    dag.nb_signature = position
    return dag  




# MERGER WITH ENTROPY
def cluster_fast2(tree, rect, params, centers, if1geo=2):   
    """
    For a given c_graph(), classification
    create the DAG without save and tree intermediate.

    Usage
    -----
    .. python ::
        cluster_fast(tree, rect)

    Parameters
    ----------
        - `tree` (c_graph): the tree to update.
        - `rect` (dict): a Python dict with the clusters.
        
    Returns
    -------
        A new c_graph the reduction.

    Details
    -------

    """
    # new dag
    dag = c_graph()
    # position of the signature
    signature_pos = {}
    position = 0
    # edges number
    edges = {}
    child = {}
    edgeOrient = {}
    edgesO = {}
    # for parametersmetry
    parametersvar = {}
    
    for n in tree.nodes:
        # the vertex cluster
        num = int(n.label)
        vvid = 'V'+str(int(num+1))
        clus = int(rect[vvid])

        # first time with this signature
        if not signature_pos.has_key(clus):
    
            # cluster done number position
            signature_pos[clus] = {}
            signature_pos[clus][params[num]] = position

            # create a node in the DAG
            n_i = make_node('I'+str(position))
            n_i.signature = position
            dag.nodes += [n_i]

            parametersvar[position] = parameter_manipulator2()
            for k in n.parameters.keys():
                parametersvar[position][str(k)] = []
                parametersvar[position][str(k)].append(n.parameters[k])
            
            # create edge dict
            edges[position] = {}

            child[position] = n

            n.signature = position

            position += 1

        if not signature_pos[clus].has_key(params[num]):
            #root to not modify !
            if position >1:
        
                signature_pos[clus][params[num]] = position

                # create a node in the DAG
                n_i = make_node('I'+str(position)) 
                n_i.signature = position
                dag.nodes += [n_i]

                parametersvar[position] = parameter_manipulator2()
                for k in n.parameters.keys():
                    parametersvar[position][str(k)] = []
                    parametersvar[position][str(k)].append(n.parameters[k])
            
                # create edge dict
                edges[position] = {}

                child[position] = n

                n.signature = position

                position += 1
                #print 0
            else:
                clus_pos = 0
                # give the correct node in the DAG
                n_i = node(dag, 0)
                for k in n.parameters.keys():
                    parametersvar[clus_pos][str(k)].append(n.parameters[k])
                
                n.signature = 0
                #print 1
                signature_pos[clus]={}
                signature_pos[clus][params[num]]=0
        
        else:
            clus_pos = signature_pos[clus][params[num]]
            # give the correct node in the DAG
            n_i = node(dag, clus_pos)
        
            for k in n.parameters.keys():
                parametersvar[clus_pos][str(k)].append(n.parameters[k])
            
            n.signature = clus_pos
        current_pos = signature_pos[clus][params[num]]

        if child[current_pos] == n:
            # take edges
            for j in range(nb_edges(n)):
                e = edge(n, j)
                # if output edge
                if e.start==n:
                    position_clus_end = e.end.signature
                    # not same cluster
                    if current_pos != position_clus_end:
                        # first time with this cluster
                        if not edges[current_pos].has_key(position_clus_end):
                            edges[current_pos][position_clus_end] = 1
                        else:
                            edges[current_pos][position_clus_end] += 1
                            
                elif e.end==n:
                        
                    num_father = int(e.start.label)
                    vvid_father = 'V'+str(int(num_father+1))
                    clus_father = int(rect[vvid_father])    

    for e in tree.edges:
        startDag=e.start.signature
        endDag=e.end.signature
        if not edgesO.has_key(startDag):
            edgesO[startDag]={}
        if not edgesO[startDag].has_key(endDag):
            edgesO[startDag][endDag] = []
        edgesO[startDag][endDag].append(e.end.parameters)


    
    for clus in parametersvar:
        n_i = node(dag, clus)
        n_i.parameters.data = parametersvar[clus].merge_vertex()
        if clus==0:
            n_i.parameters.data = parametersvar[clus].merge()

        
    for clust_in in edges:
        for clust_out in edges[clust_in]:
            e_i = make_edge(node(dag,clust_in),node(dag,clust_out),edges[clust_in][clust_out])
            dag.edges += [e_i]
            if not edgeOrient.has_key(e_i):
                edgeOrient[e_i] = []
            edgeOrient[e_i]=edgesO[clust_in][clust_out]

    def merge_edge_moy(dic):
        dicto = {}
        nb=0
        dicto[nb]={}
        comp=0
        for z in dic:
            for k in z.keys():
                # float merging
                if k == 'QtOrientation':
                    if comp==0:
                        comp = 1
                        dicto[nb] = z[k]
                    elif not comp == 1:
                            dicto[nb] = Quaternion.slerp(dicto[nb], z[k], comp)
                    comp /= 2
        return dicto

    

    def merge_edge_moy_para(matrix_filename,rect):
        f=open(matrix_filename,'r')
        dicto = {}
        w=0
        
        comp={}
        for z in f.readlines():
            
            t=z.split()
            q=Quaternion(float(t[0]),float(t[1]),float(t[2]),float(t[3]))
            if not comp.has_key(rect[w]-1):
                comp[rect[w]-1] = 1
                dicto[rect[w]-1] = q
            elif not comp[rect[w]-1] == 1:
                    dicto[rect[w]-1] = Quaternion.slerp(dicto[rect[w]-1],q, comp[rect[w]-1])
            comp[rect[w]-1] /= 2
            w+=1

        for n in dicto.keys():
            print dicto[n]
            print n
            print 'dicto de n'
        return dicto          

    for i in range(nb_nodes(dag)):
        n_i = node(dag, i)
        for j in range(nb_edges(n_i)):
            e = edge(n_i, j)
            if e.end==n_i:
                
                matrix_filename="QtOrientation.txt"

                if e.label>1:
                    print '1passe'
                    print_matrix_orient(edgeOrient[e], matrix_filename)
 
                    (rect1,rect2)=matrix_params_clustering(matrix_filename, e.label)
   
                    e.parameters.data = merge_edge_moy_para(matrix_filename,rect1)
                else:
                    print 'passe2'
                    print_matrix_orient(edgeOrient[e], matrix_filename)
                    (rect1,rect2)=matrix_params_clustering(matrix_filename, e.label)
                    e.parameters.data = merge_edge_moy_para(matrix_filename,rect1)

                print 'e.parameters.data  1'           
                print e.parameters.data
                print 'e.parameters.data 2 '         
    dag.nb_signature = position
    return dag  


# TO MERGE WITH PARAMS ON EDGES
def matrix_clustering_entropy(matrix_filename, nb_class=2, method_tool='ward'):
    """
    Clustering distance matrix from a matrix_filename file with method_tool
    algorithm.
    Selection of nb_class in the clustering.
    Returns the python object with the classes.

    Usage
    -----
    .. python ::
        matrix_clustering(matrix_filename, nb_class, method_tool)

    Parameters
    ----------
        - `matrix_filename` (str): name of the distance matrix file.
        - `nb_class` (int): the number of classes in final classification.
        - `method_tool` (str): name of the clustering method.
        the agglomeration method to be used. This should be (an unambiguous
        abbreviation of) one of "ward", "single", "complete", "average",
        "mcquitty", "median" or "centroid".
        
    Returns
    -------
        A Python dict with the clusters.

    Details
    -------
        The clustering process is done with Rpy.
        If nb_class < 2 or nb_class > size(matrix) Rpy exception.
        method_tool could be: 
    """
    assert os.path.isfile(matrix_filename), 'Error file '+matrix_filename
    
    # R tools
    set_default_mode(NO_CONVERSION)

    # Reading and clustering with Rpy
    a = r.read_table(matrix_filename)

    mydist = r.as_dist(a)
    
    # Make classes
    clust = r.hclust(mydist, method=method_tool)
    
    # Converts R object to Python dict
    set_default_mode(BASIC_CONVERSION)

    rect = r.cutree(clust, k=nb_class)
    rect2 = r.cutree(clust, h=0)
    return (rect, rect2)


def cmpval(x,y):
    if x[1]>y[1]:
        return -1
    elif x[1]==y[1]:
        return 0
    else:
        return 1
 

# TO MERGE WITH PARAMS ON EDGES
def cluster_fast_entropy(tree, rect, rect_sim, params, centers):   
    """
    

    Usage
    -----
    .. python ::
        cluster_fast_entropy(tree, rect, params, centers)

    Parameters
    ----------
        
    Returns
    -------
        A new c_graph the reduction.

    Details
    -------

    """
    # new dag
    dag = c_graph()
    # position of the signature
    signature_pos = {}
    # type of trees in the same cluster
    treetype = {}
    position = 0
    # edges number
    edges = {}
    child = {}
    # for parametersmetry
    parametersvar = {}
    longVar = {}
    node_rep = {}
    
    for n in tree.nodes:
        # the vertex cluster
        num = int(n.label)
        vvid = 'V'+str(int(num+1))
        clus = int(rect[vvid])
        clus_sim = int(rect_sim[vvid])
        
        # first time with this signature
        if not signature_pos.has_key(clus):
        
            # cluster done number position
            #signature_pos[clus] = position
            signature_pos[clus] = {}
            signature_pos[clus][params[num]] = position
            #param[clus]=[params[num]]

            # create a node in the DAG
            n_i = make_node('I'+str(position))
            n_i.signature = position
            dag.nodes += [n_i]

            #n_i.parameters = n.parameters.copy()
            parametersvar[position] = parameter_manipulator2()
            for k in n.parameters.keys():
                parametersvar[position][str(k)] = []
                parametersvar[position][str(k)].append(n.parameters[k])
                
            # create edge dict
            edges[position] = {}

            #child[position] = n

            treetype[clus] = {}
            treetype[clus][params[num]] = {}
            treetype[clus][params[num]][clus_sim] = 1
            node_rep[clus] = {}
            node_rep[clus][params[num]] = {}
            node_rep[clus][params[num]][clus_sim] = n
            
            n.signature = position

            position += 1
    
        elif not signature_pos[clus].has_key(params[num]):
            #root to not modify !
            if position >1:

                # cluster done number position
                #signature_pos[clus] = position
                #param[clus].append(params[num])
            
                signature_pos[clus][params[num]] = position
                
                treetype[clus][params[num]] = {}
                treetype[clus][params[num]][clus_sim] = 1
                node_rep[clus][params[num]] = {}
                node_rep[clus][params[num]][clus_sim] = n

                # create a node in the DAG
                n_i = make_node('I'+str(position)) 
                n_i.signature = position
                dag.nodes += [n_i]

                #n_i.parameters = n.parameters.copy()
                parametersvar[position] = parameter_manipulator2()
                for k in n.parameters.keys():
                    parametersvar[position][str(k)] = []
                    parametersvar[position][str(k)].append(n.parameters[k])
                
                # create edge dict
                edges[position] = {}

                #child[position] = n

                n.signature = position

                position += 1
            else:
                clus_pos = 0
                # A CHANGER !!!
                #clus_pos = signature_pos[clus]
                # give the correct node in the DAG
                n_i = node(dag, 0)
                
                treetype[clus][params[num]] = {}
                treetype[clus][params[num]][clus_sim] = 1
                node_rep[clus][params[num]] = {}
                node_rep[clus][params[num]][clus_sim] = n
                #n_i.parameters = add_parameters(n.parameters, n_i.parameters)
            
                for k in n.parameters.keys():
                    parametersvar[clus_pos][str(k)].append(n.parameters[k])
                
                n.signature = 0
            
        else:
            clus_pos = signature_pos[clus][params[num]]
            
            if treetype[clus][params[num]].has_key(clus_sim):
                treetype[clus][params[num]][clus_sim] += 1
            else:
                treetype[clus][params[num]][clus_sim] = 1  
                node_rep[clus][params[num]][clus_sim] = n                          
            # A CHANGER !!!
            #clus_pos = signature_pos[clus]
            # give the correct node in the DAG
            n_i = node(dag, clus_pos)
            #n_i.parameters = add_parameters(n.parameters, n_i.parameters)
            
            for k in n.parameters.keys():
                parametersvar[clus_pos][str(k)].append(n.parameters[k])
                
            n.signature = clus_pos
            
        #current_pos = signature_pos[clus][params[num]]

    for clus in treetype:
        for paramets in treetype[clus]:
            L = treetype[clus][paramets].items()
            ni = L[-1][0]
            #print "nouveau noeud"
            #print ni
            #print node_rep[clus][paramets].keys()
            n = node_rep[clus][paramets][ni]
            #n = node(tree, n_rep)
            current_pos = signature_pos[clus][paramets]
            # take edges
            for j in range(nb_edges(n)):
                e = edge(n, j)
                # if output edge
                if e.start==n:
                    #print e.end.label
                    end_label = int(e.end.label)
                    vvid_end = 'V'+str(int(end_label+1))
                    clus_end = int(rect[vvid_end])
                    #print signature_pos[clus_end]
                    #print signature_pos[clus_end].keys()
                    
                    
                    #print params[clus_end]
                    #print signature_pos[clus_end][params[end_label]]
                    position_clus_end = signature_pos[clus_end][params[end_label]]
                    # not same cluster
                    if current_pos != position_clus_end:
                        # first time with this cluster
                        if not edges[current_pos].has_key(position_clus_end):
                            #print 'i'
                            edges[current_pos][position_clus_end] = 1
                        else:
                            #print 'i'
                            edges[current_pos][position_clus_end] += 1
                            
                        

    for clus in parametersvar:
        n_i = node(dag, clus)
        n_i.parameters.data = parametersvar[clus].merge()
        
       
    for clust_in in edges:
        for clust_out in edges[clust_in]:
            e_i = make_edge(node(dag,clust_in),node(dag,clust_out),edges[clust_in][clust_out])
            dag.edges += [e_i]

    
            
    dag.nb_signature = position
    return dag  

# end file
