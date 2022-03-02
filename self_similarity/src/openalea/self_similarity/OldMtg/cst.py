# -*- python -*-
# -*- coding: utf-8 -*-
#
#       Vplants.Self_similarity: Self_similarity tools package
#
#       Copyright 2010 LaBRI
#
#       File authors: Anne-Laure Gaillard <anne-laure.gaillard@labri.fr>
#                     Pascal Ferraro <pascal.ferraro@labri.fr>
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
# 
#       OpenAlea WebSite : http://openalea.gforge.inria.fr
#
################################################################################

'''
NEST algorithm, reduction, linearization and reconstruction.
'''

__license__= "Cecill-C"
__revision__=" $Id: cst.py 17111 2014-07-09 15:42:49Z azais $ "
__docformat__ = "restructuredtext en"

# to work with the new configuration of Mac
import sys
sys.path.append('../src/self_similarity')

from graph import *
from mtg2graph import *

################################################
# TO CLEAN!
################################################
def tree_reconstruction(graph):
    """
    Reconstruct a tree with a DAG reduction.

    Usage
    -----
    .. python ::
        tree_reconstruction_parametersXYZ(graph)

    Parameters
    ----------
        - `graph` (c_graph): the DAG to reconstruct.   
        
    Returns
    -------
        The tree relative to the reduction DAG.

    Details
    -------
        The DAG must be in postfix order.
    """    
    tree = c_graph()
    tree.nb_signature = nb_nodes(graph)
    tree.max_signature_edge = 0
    nb = 0
    tree_node = make_node("S"+str(nb))
    
    tree.sum_signature_edge = 0

 
    nb_e=0
    nb_e2=0
    node_list = [tree_node]
    edge_list = []
    signature = nb_nodes(graph)-1
    #signature = 0
    tree_node.signature = signature
    tree_list = [tree_node]

    
    while tree_list != []:
        #print len(tree_list)
        tree_node = tree_list.pop()
        signature = tree_node.signature
        n = node(graph,signature)
        
        for j in range(nb_edges(n)):
            e = edge(n,j)
            if e.end==n:
                nb_e2+=1
            if e.start == n:
                nb_e+=1
                if e.label>0:
                    tree.sum_signature_edge+=int(e.label)
                if e.label>tree.max_signature_edge:
                    tree.max_signature_edge=int(e.label)
                for k in range(int(e.label)):
                    nb += 1
                    n_i = make_node("S"+str(nb))
                    n_i.signature = e.end.signature
                    
                    node_list += [n_i]
                    e2 = make_edge(tree_node,n_i,str(1))
                    edge_list += [e2]
                    tree_list.append(n_i)

    tree.nodes = node_list
    tree.edges = edge_list
    print nb_e
    print nb_e2
    return tree
                 
def tree_reconstruction_params(graph):
    """
    Reconstruct a tree with a DAG reduction.

    Usage
    -----
    .. python ::
        tree_reconstruction_parametersXYZ(graph)

    Parameters
    ----------
        - `graph` (c_graph): the DAG to reconstruct.   
        
    Returns
    -------
        The tree relative to the reduction DAG.

    Details
    -------
        The DAG must be in postfix order.
    """    
    tree = c_graph()
    tree.nb_signature = nb_nodes(graph)
    tree.max_signature_edge = 0
    tree.sum_signature_edge = 0
    nb = 0
    tree_node = make_node("S"+str(nb))
    tree_node.parameters = parameter_manipulator2()
    tree_node.parameters.data = node(graph,nb_nodes(graph)-1).parameters.data.copy()
    if 'QtOrientation' not in tree_node.parameters.data.keys():
        tree_node.parameters.data['QtOrientation']={}
        n_i= node(graph,0)
        if 'QtOrientation' in n_i.parameters.data.keys():
            for v in range(4):
                tree_node.parameters.data['QtOrientation'][v]=0
                #ou tree_node.parameters.data['QtOrientation'][v]=n_i.parameters.data['QtOrientation'][v]
            
    
    node_list = [tree_node]
    edge_list = []
    signature = nb_nodes(graph)-1
    #signature = 0
    tree_node.signature = signature
    tree_list = [tree_node]

    
    while tree_list != []:
        #print len(tree_list)
        tree_node = tree_list.pop()
        signature = tree_node.signature
        n = node(graph,signature)
        
        for j in range(nb_edges(n)):
            e = edge(n,j)  
            if e.start == n:
                if e.label>0:
                    tree.sum_signature_edge+=int(e.label)
                if e.label>tree.max_signature_edge:
                    tree.max_signature_edge=int(e.label)
                for k in range(int(e.label)):
                    nb += 1
                    n_i = make_node("S"+str(nb))
                    n_i.signature = e.end.signature
                    n_i.parameters = parameter_manipulator2()
                    n_i.parameters.data = e.end.parameters.data.copy()
                    
                    
                    if k in e.parameters.data.keys():
                        n_i.parameters.data['QtOrientation']={}
                        #print '\n\n\n'
                        for v in range(4):
                            n_i.parameters.data['QtOrientation'][v]=e.parameters.data[k][v]
                            #print n_i.parameters.data    
                    else:
                        n_i.parameters.data['QtOrientation']={}
                        #print '\n\n\n'
                        for v in range(4):
                            n_i.parameters.data['QtOrientation'][v]=0
                            #print n_i.parameters.data   
                        
                    node_list += [n_i]
                    e2 = make_edge(tree_node,n_i,str(1))
                    edge_list += [e2]
                    tree_list.append(n_i)

    tree.nodes = node_list
    tree.edges = edge_list

    return tree
                 
################################################
# NEST
################################################

def signature_position(signature_list, signature):
    """
    Return the position of signature in signature_list.

    Usage
    -----
    .. python ::
        signature_position(signature_list, signature)

    Parameters
    ----------
        - `signature_list` (list<signature>): the list of the signatures in a
        graph.
        - `signature` (list<int>): the signature to test.        
        
    Returns
    -------
        Return the position of the signature.
        None if it's not in the list.

    Details
    -------
    """       
    if signature == [] :
        return 0
    else:
        signature.sort()
        for i in range(len(signature_list)):
            if signature_list[i]==signature :
                return i+1
        return None


def tree_reduction(tree):
    """
    Exact reduction of a tree to a DAG.

    Usage
    -----
    .. python ::
        tree_reduction(tree)

    Parameters
    ----------
        - `tree` (c_graph): the tree to reduct.   
        
    Returns
    -------
        The exact reduction DAG of the tree.

    Details
    -------
        The tree must be in postfix order.
    """    
    reduction_dag = c_graph()
    signature_list = []
    signature_value = 0
    n_i = make_node("I"+str(signature_value))
    n_i.signature = signature_value
    node_list = [n_i]
    edge_list = []
    for i in range(nb_nodes(tree)):
        n = node(tree,i)
        c_list = child_list(n)
        signature = []
        for son in c_list :
            signature += [son.signature]
        node_signature_position = signature_position(signature_list,signature)
        if node_signature_position == None :
            signature_value += 1
            n_i = make_node("I"+str(signature_value))
            # Change for approximative self-similarity
            n_i.signature = signature_value
            node_list += [n_i]
            i = 0
            while (i<len(signature)):
                nb_signature =0
                c = signature[i]
                while ((i<len(signature)) and
                (c == signature[i])) :
                    nb_signature += 1
                    i += 1
                e = make_edge(node_list[signature_value],node_list[c],str(nb_signature))
                edge_list += [e]
            node_signature_position = signature_value
            signature_list += [signature]
        n.signature = node_signature_position
    reduction_dag.nodes = node_list
    reduction_dag.edges = edge_list
    reduction_dag.set_nb_signature(nb_nodes(reduction_dag))
    print len(edge_list)
    return reduction_dag


def list_of_edge_value_at_max_height(g, height, node):
    """
    List of all value edges between a given node and at a maximum given height.
    If there is not an edge between two nodes, the value is equal to 0.

    Usage
    -----
    .. python ::
        list_of_edge_value_at_max_height(g, height, node)

    Parameters
    ----------
        - `g` (c_graph): the tree.
        - `height` (c_graph): the maximum height.
        - `node` (c_node): the start node.
        
    Returns
    -------
        The list of all value edges between a given node and a maximum height.

    Details
    -------
    """   
    value_list = []
    if height >= node.height :
        print "depth is too large !!!"
    else :
        l_desc = node_list_at_a_maximum_height(g,height)
        for l in l_desc :
            value_list += [int(edge_label(node,l))]
    value_list.reverse()
    return value_list
                

def complete_value_node(g, max_value, node, height):
    """
    Given a max_value, a node and a height, complete the value of
    edges for the node.

    Usage
    -----
    .. python ::
        complete_value_node(g, max_value, node, height)

    Parameters
    ----------
        - `g` (c_graph): the DAG to complete.
        - `max_value` (int): the maximum number of edges.
        - `node` (c_node): the node to complete.
        - `height` (int): the height to complete.
        
    Returns
    -------
        The list of the edges.

    Details
    -------
    """   
    l_ni = list_of_edge_value_at_max_height(g,height,node)
    ni_total = sum(l_ni)
    r = max_value - l_ni[0]
    if ni_total > max_value :
        i = 0
        r_tmp = r
        while r != 0:
            r_tmp = r
            l_ni[i] = 0
            i += 1
            r -= min(r,l_ni[i])
        #on sort car r == 0
        l_ni[0] = max_value
        l_ni[i] -= r_tmp
    else :
        l_ni[0] = max_value
        for i in range(1,len(l_ni)):
            l_ni[i]=0
    l_ni.reverse()
    return l_ni


def height_graph_update(dag, node, new_value, height):
    """
    Given a node and a list of value from a given height to 0, update the value
    of edges between the node and all nodes with a smaller height. If the value
    is greater than 0 verify if the edge exists in the graph (and add it if
    necessary, if the value is equal to 0 delete the edge if it exists in the
    graph.

    Usage
    -----
    .. python ::
        height_graph_update(dag, node, new_value, height)

    Parameters
    ----------
        - `dag` (c_graph): the DAG with height to update.
        - `node` (c_node): the node with height to update.
        - `new_value` (int): the new value.
        - `height` (int): the height.
        
    Returns
    -------

    Details
    -------
        Dag is modify.
    """   
    l_ni = node_list_at_a_maximum_height(dag,height)
    for i in range(len(l_ni)) :
        j = 0
        find = 0
        nb_edge = nb_edges(node)
        while j<nb_edge and find == 0:
            ed = edge(node,j)
            if ed.end == l_ni[i] :
                find = 1
                if new_value[i] != 0 :
                    ed.label = new_value[i]
                else :
                    destroy_e_edge(dag,node,l_ni[i])
            j += 1
        if find ==0 :
            if new_value[i] != 0 :
                make_edge(node,l_ni[i],new_value[i])


def complete_height(dag, height):
    """
    Linearize a current height.

    Usage
    -----
    .. python ::
        complete_height(dag, height)

    Parameters
    ----------
        - `dag` (c_graph): the DAG.   
        - `height` (int): the current height.   
        
    Returns
    -------

    Details
    -------
        Dag is modify.
    """   
    nodelist = node_list_at_given_height(dag,height)
    current_height = height-1
    while current_height >= 0:
        node_list_h_current_h = node_list_between_two_given_heights(dag,height,current_height)
        max_value = max_node_value_between_two_heights(dag,height,current_height)
        for current_node in nodelist:
            new_values = complete_value_node(dag,max_value,current_node,current_height)
            height_graph_update(dag,current_node,new_values,current_height)
        current_height -= 1
    #on enleve les noeuds a hauteur height sauf 1
    remove_equivalent_node_at_height(dag,height)
 
    
def remove_equivalent_node_at_height(dag, height):
    """
    Remove same nodes in the current height.

    Usage
    -----
    .. python ::
        remove_equivalent_node_at_height(dag, height)

    Parameters
    ----------
        - `dag` (c_graph): the DAG to reconstruct.  
        - `height` (int): the current height.  
        
    Returns
    -------

    Details
    -------
        The DAG is modify.
    """   
    to_remove_node_list = node_list_at_given_height(dag,height)
    keep_node = to_remove_node_list[0]
    for i in range(1,len(to_remove_node_list)):
        current_node = to_remove_node_list[i]
        parent_current_node = parent_list(current_node)
        for pa in parent_current_node :
            delete_edge_value = (edge_between(pa,current_node)).label
            if is_parent(keep_node,pa):
                edge_kept = edge_between(pa,keep_node)
                edge_kept.label = int(edge_kept.label)+int(delete_edge_value)
            else :
                make_edge(pa,keep_node,delete_edge_value)
        destroy_node(dag,current_node)  
    

def dag_linearization(dag): 
    """
    Linearize a DAG.

    Usage
    -----
    .. python ::
        dag_linearization(dag)

    Parameters
    ----------
        - `dag` (c_graph): the DAG to linearize.   
        
    Returns
    -------

    Details
    -------
        Modify the dag.
    """    
    max_height = height_of_graph(dag)
    for i in range(max_height):
         complete_height(dag,i)
    # update of node signature
    for i in range(nb_nodes(dag)):
        current_node = node(dag,i)
        current_node.signature = i

    
def is_linear(dag):
    """
    Test is the dag is linear. Return true if it is, false else.

    Usage
    -----
    .. python ::
        is_linear(dag)

    Parameters
    ----------
        - `dag` (c_graph): the DAG to test.   
        
    Returns
    -------
        True if the dag is linear, else false.

    Details
    -------
        The DAG must be in postoder notation.
    """
    # trivial
    if nb_nodes(dag)==1:
        return 1
    
    # if edge between father and child
    father = nb_nodes(dag) - 1
    child = nb_nodes(dag) - 2
    while child >= 0:
        n_father = node(dag,father)
        n_child = node(dag,child)

        # case of node multiple roots
        if not(edge_between(n_father,n_child)):
            for j in range(nb_edges(n_child)):
                e = edge(n_child, j)
                if e.end==n_child:
                    return 0
            child -= 1
        else:
            father = child
            child -= 1
    
    return 1

# end file
