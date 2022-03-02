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


"""
This module is relative to the graph creation and modification.
"""

__license__= "Cecill-C"
__revision__=" $Id: graph.py 17111 2014-07-09 15:42:49Z azais $ "
__docformat__ = "restructuredtext en"

# for mac usage
import sys
sys.path.append('../src/self_similarity')

from parameter_manipulator import *


# Node
class c_node:   
    """
    Definition of a node of a graph
    """
    def __init__(self, label):
        self.label = label
        self.depth = 0
        self.height = 0
        self.parameters = parameter_manipulator2()
        
    def set_params(self, param):
        self.parameters = param.copy()
        
    def __repr__(self):
        return "<Node " + str(self.label) +">"

    def __str__(self):
        return str(self.label)


# Edge
class c_edge:   
    """
    Definition of an edge of a graph
    """
    def __init__(self, label):
        self.label = label
        self.parameters = parameter_manipulator2()

    def set_params(self, param):
        self.parameters = param.copy()

    def __repr__(self):
        return "<Edge " + str(self.label) +">"

    def __str__(self):
        return str(self.label)


# Graph
class c_graph:   
    """
    Definition of a c_graph
    """
    def __init__(self):
        self.nb_signature = 0
        # for log compression computation
        self.max_signature_edge = 0
        self.sum_signature_edge = 0
        self.nodes= []
        self.edges = []
        
    def get_nb_signature(self):  
        return self.nb_signature
    
    def set_nb_signature(self, nb):
        self.nb_signature = nb
        
    def add_edge(self, edge):
        """
        Add one edge
        """
        self.edges += [edge]


def label(object):
    """
    Return the label of an object
    """
    return object.label


#-------------------------------------------------------
#   Functions to create a Graph
#-------------------------------------------------------

def make_node(label=None, signature=-1):
    """
    Make a new node with a given label and signature.

    Usage
    -----
    .. python ::
        make_node(label, signature)

    Parameters
    ----------
        - `label` (str): the label of the node.
        - `signature` (int): the signature of the node.
        
    Returns
    -------
        The new node.

    Details
    -------
    """   
    n = c_node(label)
    # define without edges
    n.nedges = []
    n.signature = signature
    # none height
    n.height = 0
    return n


def make_edge(start_node, end_node, label="1"):
    """
    Make a new edge with a given start, end and signature.

    Usage
    -----
    .. python ::
        make_edge(start_node, end_node, label)
    Parameters
    ----------
        - `start_node` (node): the start node of the edge.
        - `end_node` (node): the end node of the edges.
        - `label` (str): the label of the edge.
        
    Returns
    -------
        The new edge.

    Details
    -------
    """  
    e = c_edge(label)
    e.start = start_node
    e.end = end_node
    # update end node depth
    end_node.depth = max(end_node.depth,start_node.depth+1)
    # add edge in nodes
    start_node.nedges = start_node.nedges + [e]
    end_node.nedges = end_node.nedges + [e]
    return e


def make_edge_child(node_list, parent_node, list_child_nodes, label=None):
    """
    Make an edge between a father and a list of child.

    Usage
    -----
    .. python ::
        make_edge_child(node_list, parent_node, list_child_nodes, label)
        
    Parameters
    ----------
        - `node_list` (list<c_node>): 
        - `parent_node` (c_node): 
        - `list_child_nodes` (list<c_node>): 
        - `label` (int): 
        
    Returns
    -------
        The edge list with all the new edges.

    Details
    -------
    """  
    i = 0
    edge_list = []
    parent = node_list[parent_node]
    for child in list_child_nodes:
        e = make_edge(parent,node_list[child])
        edge_list += [e]
        i +=1
    return edge_list


#-------------------------------------------------------
#   Functions to label/unlabel nodes/edges
#-------------------------------------------------------

def set_signature (node, signature):
    node.signature = signature

def delete_signature (node):
    node.signature = 0

def get_signature (node):
    return node.signature

#def mark_node (node):
#    node.mark = 1

#def unmark_node (node):
#    node.mark = 0

#def node_marked (node):
#    return node.mark

#def mark_edge (edge):
#    edge.mark = 1

#def unmark_edge (edge):
#    edge.mark = 0

#def edge_marked (edge):
#    return edge.mark


#-------------------------------------------------------
#   Functions to get Graph Properties
#-------------------------------------------------------

# Node Number
def nb_nodes (graph):
    return len(graph.nodes)

# Max edge
def max_signature_edge (graph):
    return graph.max_signature_edge

# Edge Number
def edge_nb (graph):
    return len(graph.edges)

# Ieme noeud du graphe
def node (graph, i):
    return graph.nodes[i]

# Node list
def node_list(graph):
    l = []
    for i in range(nb_nodes(graph)):
        l += [node(graph,i)]
    return l

#-------------------------------------------------------
#   Functions to get Node Properties
#-------------------------------------------------------

def nb_edges (node):
    return len(node.nedges)

def edge (node, i):
    return node.nedges[i]

def edge_label(node1, node2):
    for j in range(nb_edges(node1)):
        e = edge(node1, j)
        if e.end == node2:
            return e.label
    return 0

def edge_between(node1, node2):
    for j in range(nb_edges(node1)):
        e = edge(node1, j)
        if e.end == node2:
            return e
    return 0

def follow_edge (node, edge):
    if edge.start == node:
        return edge.end
    else:
        return edge.start

def node_position(g, a_node):
    for i in range(nb_nodes(g)):
        if node(g,i) == a_node:
            return i
    return -1


# return the position of an edge represented by its extremities
# on the list of edges of a node
# return -1 if node is not connected to the edge
def edge_position(node, start, end):
    i=0
    while i<nb_edges(node) :
        e = edge(node,i)
        if e.end==end and e.start==start :
            return i
        i+=1
    return -1

# return le numero de l'arc dans la liste des arcs de end qui commence par start
def edge_position_in_graph(g, start, end):
    for i in range(len(g.edges)):
        if start==g.edges[i].start and end==g.edges[i].end:
            return i
    return -1




#-------------------------------------------------------
#   Functions to destroy a graph
#-------------------------------------------------------

# deleting edge between in_node and out_node
def destroy_e_edge(g, in_node, out_node):
    pos_in = edge_position(in_node, in_node, out_node)
    pos_out = edge_position(out_node, in_node, out_node)
    del in_node.nedges[pos_in]
    del out_node.nedges[pos_out]
    e = edge_between(in_node, out_node)
    if g.edges != []:
        del g.edges[edge_position_in_graph(g, in_node, out_node)]
    
def destroy_edge(g, e):
    in_node = e.start
    out_node = e.end
    destroy_e_edge(g, in_node, out_node)
    
def destroy_edge_same(g, e):
    in_node = e.start
    destroy_e_edge_same(g, in_node)
    
def destroy_e_edge_same(g, in_node):
    pos_in = edge_position(in_node, in_node, in_node)
    del in_node.nedges[pos_in]
    e = edge_between(in_node, in_node)
    if g.edges != []:
        del g.edges[edge_position_in_graph(g, in_node, in_node)]   
    
def destroy_node(g, node):
    for i in range(nb_edges(node)):
        e = edge(node, 0)
        destroy_edge(g, e)
    del g.nodes[node_position(g, node)]

# determine if a node is a parent of another
def is_parent(id_node, parent):
    for i in range(nb_edges(id_node)):
        e = edge(id_node, i)
        if e.end == id_node and e.start == parent:
            return True
    return False
    
        
# Return the parent list of a node
def parent_list(node):
    parent = []
    for i in range(nb_edges(node)):
        e = edge(node, i)
        if e.end == node:
            parent += [e.start]
    return parent

def tree_root(tree):
    for v in node_list(tree):
        if parent_list(v)==[]:
            return v
    return None


# return the list of children of a node
def child_list(node):
    c_list = []
    for i in range(nb_edges(node)):
        e = edge(node, i)
        if e.start == node:
            c_list += [e.end]
    return c_list

# Test if a node is a leaf
def is_leaf(node):
    leaf = True
    for i in range(nb_edges(node)):
        if edge(node, i).start == node :
            leaf = False
            return False
    return leaf

# List of leaves
def leaf_list(graphe):
    leaf_list = []
    for i in range (nb_nodes(graphe)):
        n = node(graphe, i)
        if is_leaf(n):
            leaf_list += [n]
    return leaf_list

# Compute the height of each node of dag
# (0 for a leaf max height for the root)
def compute_height(DAG) :
    for a_leaf in leaf_list(DAG) :
        update_parent_height(a_leaf)

def update_parent_height(current_node):
    parent = parent_list(current_node)
    for a_parent in parent:
        a_parent.height = max(a_parent.height, current_node.height+1)
        update_parent_height(a_parent)

# Parent list at a given height
def parent_list_at_given_height(current_node, height):
    parent = parent_list(current_node)
    return filter (lambda n : n.height == height, parent)

# Node list at a given height
def node_list_at_given_height(dag, height):
    nodelist = node_list(dag)
    return filter (lambda n : n.height == height, nodelist)

#  Node list between two given height
def node_list_between_two_given_heights(dag, height1, height2):
    nodelist = node_list(dag)
    return filter (lambda n : (n.height <= height1) and (n.height >= height2),nodelist)

#  Node list at a maximum given height
def node_list_at_a_maximum_height(dag,height):
    nodelist = node_list(dag)
    return filter (lambda n : (n.height <= height), nodelist)


# liste des labels des arcs entre les noeuds a height et le noeud a height1
def max_node_value_between_two_heights(dag, height, height1):
    """
    Print the graph in standard output.

    Usage
    -----
    .. python ::
        print_graph(graph)

    Parameters
    ----------
        - `graph` (c_graph): the graph to print.
        
    Returns
    -------

    Details
    -------
    """  
    nodelist = node_list_at_given_height(dag, height)
    node = node_list_at_given_height(dag, height1)[0]
    maxi = 0
    for l_node in nodelist:
        if maxi < int(edge_label(l_node, node)) :
            maxi = int(edge_label(l_node, node))
    return maxi


def height_of_graph(dag):
    """
    Return the height of a given dag.

    Usage
    -----
    .. python ::
        height_of_graph(dag)

    Parameters
    ----------
        - `dag` (c_graph): the dag to compute the height.
        
    Returns
    -------
        The height of the dag.

    Details
    -------
    """  
    max_height = 0
    compute_height(dag)
    return max([(n.height) for n in node_list(dag)])


def print_graph(graph):
    """
    Print the graph in standard output.

    Usage
    -----
    .. python ::
        print_graph(graph)

    Parameters
    ----------
        - `graph` (c_graph): the graph to print.
        
    Returns
    -------

    Details
    -------
    """    
    for i in range (0, nb_nodes(graph)):
        n = node(graph, i)
        print "Edges From Node ", n.label
        print "Signature",n.signature
        for j in range(nb_edges(n)):
            e = edge(n, j)
            if e.start == n:
                print  n.label, " ---", e.label,"--->", e.end.label

# end file
