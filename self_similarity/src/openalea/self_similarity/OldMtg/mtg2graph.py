# -*- parameters -*-
# -*- coding: utf-8 -*-
#
#       Vplants.Self_similarity: Self_similarity tools package
#
#       Copyright 2010 LaBRI
#
#       File authors: Anne-Laure Gaillard <anne-laure.gaillard@labri.fr>
#                     Pascal Ferraro <pascal.ferraro@labri.fr>
#                       
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
# 
#       OpenAlea WebSite : http://openalea.gforge.inria.fr
#
################################################################################


"""
This module convert a MTG file to a graph and a graph to a MTG file.
"""

__license__= "Cecill-C"
__revision__=" $Id: mtg2graph.py 17111 2014-07-09 15:42:49Z azais $ "
__docformat__ = "restructuredtext en"

# for mac usage
import sys
sys.path.append('../src/self_similarity')

from graph import *
from openalea.aml import *
from parameter_manipulator import *


def create_edge_father_son(edge_list, father, nodeListVertex, nodeList):
    """ Create an edge between a father node and sons.
    
    When create a graph with an open MTG file create the sons of a father node,
    create an edge between a father node and his relative sons in the mtg.
    With an edge_list (the edges already created), the father (of new sons),
    a nodeListVertex (the node in the graph) and a nodeList.

    Usage
    -----
      create_edge_father_son(edge_list, father, nodeListVertex, nodeList)

    :Parameters:
      - `edge_list` (list<c_edge>) - list of the edges in the graph.
      - `father` (c_node) - the father node.
      - `nodeListVertex` (list<c_node>) - the list of vertex in the mtg.
      - `nodeList` (list<c_node>) - the list of the nodes in the graph.
        
    :Returns:
      None
        
    :Examples:
      TO DO
      
    .. warning:: Must have an open MTG, use amlPy.
    ------------
    
    .. todo:: Examples in this doc, do not use amlPy.
    ---------
        
    """
    # list of all the sons of the father
    # use amlPy for MTG reading
    son_list = Sons(father)
    # take the father mtg's id in the node list
    index_father = nodeListVertex.index(father)
    # create edge between father and son
    for son in son_list :
        # the son mtg's id in the node list
        index_son = nodeListVertex.index(son)
        edge_list += [make_edge(nodeList[index_father],nodeList[index_son],'1')]
        create_edge_father_son(edge_list, son, nodeListVertex, nodeList)


def mtg2graph(scale=1, root=1, param={}):   
    """ Read a MTG and create the relative c_graph.
    
    Create the c_graph python from an open MTG, the scale and the root.
    For adding parameters like geometry give a param dict.
    param{MTG'd id} = parameters (must be a python dictionnary).

    Usage
    -----
      mtg2graph(scale, root, parameters)

    :Parameters:
      - `scale` (int) - the scale of the tree to create.
      - `root` (int) - the current root to consider.
      - `param` (dict) - the parameters (geometry,...).
        
    :Returns:
      The c_graph relative to the MTG file.
        
    :Examples:
      from openalea.aml import *
      mtg_filename = '../example/agraf.mtg'
      g = MTG(mtg_filename)
      tree = mtg2graph(3, 3)
      
    .. warning:: Must have an open MTG, use amlPy.
    ------------
    
    .. todo:: Do not use amlPy.
    ---------
        
    """
    # graph creation
    gr = c_graph()
    # in creation all nodes with -1 as signature
    gr.set_nb_signature(1)
    # nodes creation
    nb_nodes = len(Descendants(root, Scale=scale))

    # create node and vertex lists
    nodeList = []
    nodeListVertex = []
    # for node label
    comp = 0
    # all mtg nodes from the root
    # use amlPy for MTG reading
    for i in Descendants(root,Scale=scale):
        n_i = make_node(comp)
        comp += 1
        # geometry update
        n_i.parameters.init_parameter(param, i)
        # for amelioration with branching studies
        n_i.relation = EdgeType(i, Father(i))
        # signature not define
        n_i.signature = -1
        nodeList += [n_i]
        nodeListVertex += [i]

    # for postorder notation
    nodeList.reverse()
    nodeListVertex.reverse()
    gr.nodes = nodeList
    gr.edges = []
    # create edges
    create_edge_father_son(gr.edges, root, nodeListVertex, nodeList)
    return gr

 

def mtg2graph_params(scale=1, root=1):   
    """ Read a MTG and create the relative c_graph.
    
    Create the c_graph python from an open MTG, the scale and the root.
    For adding parameters like geometry give a param dict.
    param{MTG'd id} = parameters (must be a python dictionnary).

    Usage
    -----
      mtg2graph(scale, root, parameters)

    :Parameters:
      - `scale` (int) - the scale of the tree to create.
      - `root` (int) - the current root to consider.
      - `param` (dict) - the parameters (geometry,...).
        
    :Returns:
      The c_graph relative to the MTG file.
        
    :Examples:
      from openalea.aml import *
      mtg_filename = '../example/agraf.mtg'
      g = MTG(mtg_filename)
      tree = mtg2graph(3, 3)
      
    .. warning:: Must have an open MTG, use amlPy.
    ------------
    
    .. todo:: Do not use amlPy.
    ---------
        
    """
    param={}
    param['AnchorT'] ={}
    param['Length'] ={}
    param['Diameter'] ={}
    param['QtOrientation'] = {}
    
    for v in Descendants(root,Scale=scale):
        param['Diameter'][v]=Feature(v,'Diameter')
        param['Length'][v]=Feature(v,'Length')
        param['AnchorT'][v]=Feature(v,'AnchorT')
        val_quater = Quaternion(Feature(v,'Q1'),Feature(v,'Q2'),Feature(v,'Q3'),Feature(v,'Q4'))
        param['QtOrientation'][v]=val_quater
        
    # graph creation
    gr = c_graph()
    # in creation all nodes with -1 as signature
    gr.set_nb_signature(1)
    # nodes creation
    nb_nodes = len(Descendants(root, Scale=scale))

    # create node and vertex lists
    nodeList = []
    nodeListVertex = []
    # for node label
    comp = 0
    # all mtg nodes from the root
    # use amlPy for MTG reading
    for i in Descendants(root,Scale=scale):
        n_i = make_node(comp)
        comp += 1
        # geometry update
        n_i.parameters.init_parameter(param, i)
        # for amelioration with branching studies
        n_i.relation = EdgeType(i, Father(i))
        # signature not define
        n_i.signature = -1
        nodeList += [n_i]
        nodeListVertex += [i]

    # for postorder notation
    nodeList.reverse()
    nodeListVertex.reverse()
    gr.nodes = nodeList
    gr.edges = []
    # create edges
    create_edge_father_son(gr.edges, root, nodeListVertex, nodeList)
    return gr

       
def graph2mtg(tree, name, i=0, maxSize=0, p=1):
    """  Write a graph in a MTG files.
   
    Write the tree in a MTG file in path name, i the tree number in the MTG.
    The c_graph must be a tree.
    All the nodes are write with a '+' relation.
    There is two scales. Nodes are in scale 2.
    If there is more than one tree need the same parameters.

    Usage
    -----
      graph2mtg(tree, name, i)

    :Parameters:
      - `tree` (c_graph) - the tree to write.
      - `name` (str) - the filename of the MTG.
      - `i` (int) - the number of this tree in the file (default: 0).
      - `maxSize` (int) - the maximum lenght of trees in mtg (default: 0).
      - `p` (bool) - write parameters in mtg file (default: false).
        
    :Returns:
      None
        
    :Examples:
      TO DO
      
    .. warning:: Must have written permission on name file.
    ------------
    
    .. todo:: Examples in this doc.
    ---------
        
    """
    # the root must contain all parameters
    root = tree_root(tree)
    compute_height(tree)
    size=maxSize
    if size==0:
        size = height_of_graph(tree)
    # write header if not already did
    if i==0:
        # if exists delete name file
        try:
            source = open(name,'w')
        except IOError:
            sys.exit('Could not open '+ name)    
        # write
        source.write('#\n')
        source.write('#\n')
        source.write('CODE:\tFORM-A\n')    
        source.write('CLASSES:\n')
        source.write('SYMBOL\tSCALE\tDECOMPOSITION\tINDEXATION\tDEFINITION\n')
        source.write('$\t0\tFREE\tFREE\tIMPLICIT\n')
        source.write('T\t1\tFREE\tFREE\tEXPLICIT\n')
        source.write('S\t2\tFREE\tFREE\tEXPLICIT\n\n')
        source.write('DESCRIPTION :\n')
        source.write('LEFT\tRIGHT\tRELTYPE\tMAX\n')
        source.write('S\tS\t<\t?\n')
        source.write('S\tS\t+\t?\n\n')
    
        # feature with parameters
        source.write('FEATURES:\n')
        source.write('NAME\tTYPE\n\n')
        # entity_code with parameters
        if p:
            source.write(root.parameters.parameters2mtg_feature())
        source.write('MTG:\n')
        if p:
            source.write(root.parameters.parameters2mtg_entity_code(size))
        # without parameters
        if (len(root.parameters) == 0) or (not p):
            source.write('TOPO\n')
    # do not errase the file if not the first tree
    else:
        try:
            source = open(name,'a')
        except IOError:
            sys.exit('Could not open '+ name)      
    # first write the root with scale 1    
    source.write('/T'+str(i)+'\n'+'^/S0')
    # write parameters
    if p:
        source.write(root.parameters.parameters2mtg(size+1))
    source.write('\n')
    
    # others nodes
    print_sons(root,1,source,size,p)
    source.close()


def print_sons(node, depth, source, size, p=1):
    """  Write the sons of node in a MTG files.
   
    Write the sons of a node in a MTG file in path name.
    The c_graph must be a tree.
    All the nodes are write with a '+' relation.
    Nodes are in scale 2.
    All nodes in the tree need same parameters.

    Usage
    -----
      print_sons(node, depth, nb, source)

    :Parameters:
      - `node` (c_node) - the current node.
      - `depth` (int) - the depth of the node.
      - `source` (str) - the filename of the MTG.
      - `size` (str) - the max lenght of the trees in mtg.
      - `p` (boolean) - true if print parameters, false if not.

        
    :Returns:
      None
        
    :Examples:
      TO DO
      
    .. warning:: Must have written permission on name file.
    ------------
    
    .. todo:: Examples in this doc.
    ---------
        
    """
    
    for n in child_list(node):
        # correct indentation for depth
        for t in xrange(depth):
            source.write('\t')
        try:
            int(n.label)
            source.write('+S'+str(n.label))
            
        except ValueError:
            source.write('+'+str(n.label))
        # write parameters
        if p:
            source.write(n.parameters.parameters2mtg(size-depth+1))
        source.write('\n')
        print_sons(n, depth+1, source, size,p)
    
# end file
