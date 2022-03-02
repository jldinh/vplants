import sys
from ColorFunction import *

#-------------------------------------------------------
#   DEFINITION OF GRAPH TYPE
#-------------------------------------------------------

class c_node:
    "a node of a graph"
    def __init__(self,label):
        self.label = label
        self.depth = 0
        self.height = 0
    def __repr__(self):
        return "<Node " + str(self.label) +">"
    def __str__(self):
        return str(self.label)


class c_edge:
    "an edge of a graph"
    def __init__(self,label):
        self.label = label
    def __repr__(self):
        return "<Edge " + str(self.label) +">"
    def __str__(self):
        return str(self.label)

class c_graph:
    "the graph itself"
    def __init__(self):
        self.nb_signature = 0
        self.nodes= []
        self.edges = []
    def get_nb_signature(self):
        return self.nb_signature
    def set_nb_signature(self,nb):
        self.nb_signature = nb
    def add_edge(self,edge):
        self.edges += [edge]

def label(object):
    return object.label


#-------------------------------------------------------
#   Functions to create a Graph
#-------------------------------------------------------

def make_node(label=None,signature=-1):
    n = c_node(label)
    n.nedges = []
    n.signature = signature
    n.height = 0
    return n

def make_edge(start_node, end_node, label="1"):
    e = c_edge(label)
    e.start = start_node
    e.end = end_node
    end_node.depth = max(end_node.depth,start_node.depth+1)
    start_node.nedges = start_node.nedges + [e]
    end_node.nedges = end_node.nedges + [e]
    return e

def make_edge_child(node_list,parent_node,list_child_nodes,label=None):
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

def set_signature (node,color):
    node.signature = signature

def delete_signature (node):
    node.signature = 0

def get_signature (node):
    return node.signature

def mark_node (node):
    node.mark = 1

def unmark_node (node):
    node.mark = 0

def node_marked (node):
    return node.mark

def mark_edge (edge):
    edge.mark = 1

def unmark_edge (edge):
    edge.mark = 0

def edge_marked (edge):
    return edge.mark


#-------------------------------------------------------
#   Functions to get Graph Properties
#-------------------------------------------------------

# Node Number
def nb_nodes (graph):
    return len(graph.nodes)

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

def edge_label(node1,node2):
    for j in range(nb_edges(node1)):
        e = edge(node1, j)
        if e.end == node2:
            return e.label
    return 0

def edge_between(node1,node2):
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

def node_position(g,a_node):
    for i in range(nb_nodes(g)):
        if node(g,i)== a_node:
            return i
    return -1


# return the position of an edge represented by its extremities on the list of edges of a node
# return -1 if node is not connected to the edge
def edge_position(node,start,end):
    i=0
    while i<nb_edges(node) :
        e = edge(node,i)
        if e.end==end and e.start==start :
            return i
        i+=1
    return -1

# return le numero de l'arc dans la liste des arcs de end qui commence par start
def edge_position_in_graph(g,start,end):
    for i in range(len(g.edges)):
        if start==g.edges[i].start and end==g.edges[i].end:
            return i
    return -1


#-------------------------------------------------------
#   Functions to destroy a graph
#-------------------------------------------------------

# deleting edge between in_node and out_node
def destroy_e_edge(g,in_node,out_node):
    pos_in = edge_position(in_node,in_node,out_node)
    pos_out = edge_position(out_node,in_node,out_node)
    del in_node.nedges[pos_in]
    del out_node.nedges[pos_out]
    e = edge_between(in_node,out_node)
    if g.edges != []:
        del g.edges[edge_position_in_graph(g,in_node,out_node)]
    
def destroy_edge(g,e):
    in_node = e.start
    out_node = e.end
    destroy_e_edge(g,in_node,out_node)
    
def destroy_node(g,node):
    for i in range(nb_edges(node)):
        e = edge(node,0)
        destroy_edge(g,e)
    del g.nodes[node_position(g,node)]

# determine if a node is a parent of another
def is_parent(id_node,parent):
    for i in range(nb_edges(id_node)):
        e = edge(id_node,i)
        if e.end == id_node and e.start == parent:
            return True
    return False
    
        
# Return the parent list of a node
def parent_list(node):
    parent = []
    for i in range(nb_edges(node)):
        e = edge(node,i)
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
        e = edge(node,i)
        if e.start == node:
            c_list += [e.end]
    return c_list

# Test if a node is a leaf
def is_leaf(node):
    leaf = True
    for i in range(nb_edges(node)):
        if edge(node,i).start == node :
            leaf = False
            return False
    return leaf

# List of leaves
def leaf_list(graphe):
    leaf_list = []
    for i in range (nb_nodes(graphe)):
        n = node(graphe,i)
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
        a_parent.height = max(a_parent.height,current_node.height+1)
        update_parent_height(a_parent)

# Parent list at a given height
def parent_list_at_given_height(current_node,height):
    parent = parent_list(current_node)
    return filter (lambda n : n.height == height,parent)

# Node list at a given height
def node_list_at_given_height(dag,height):
    nodelist = node_list(dag)
    return filter (lambda n : n.height == height,nodelist)

#  Node list between two given height
def node_list_between_two_given_heights(dag,height1,height2):
    nodelist = node_list(dag)
    return filter (lambda n : (n.height <= height1) and (n.height >= height2),nodelist)

#  Node list at a maximum given height
def node_list_at_a_maximum_height(dag,height):
    nodelist = node_list(dag)
    return filter (lambda n : (n.height <= height),nodelist)


# liste des labels des arcs entre les noeuds a height et le noeud a height1
def max_node_value_between_two_heights(dag,height,height1):
    nodelist = node_list_at_given_height(dag,height)
    node = node_list_at_given_height(dag,height1)[0]
    maxi = 0
    for l_node in nodelist:
        if maxi < int(edge_label(l_node,node)) :
            maxi = int(edge_label(l_node,node))
    return maxi


# return the height of a dag
def height_of_graph(dag):  
    max_height = 0
    compute_height(dag)
    return max([(n.height) for n in node_list(dag)])


#-------------------------------------------------------
#   Functions to Print/Save a graph
#-------------------------------------------------------
def print_graph(graph):
    for i in range (0, nb_nodes(graph)):
        n = node(graph, i)
        print "Edges From Node ", n.label
        for j in range(nb_edges(n)):
            e = edge(n, j)
            if e.start == n:
                print  n.label, " ---", e.label,"--->", e.end.label


def save_tulip(graph,name):
    source = open(name,"w")
    source.write("(nodes ")
    for i in range(0,nb_nodes(graph)):
        source.write(" %d " %(i+1))
    source.write(")\n")
    edge_nb = 0
    for i in range (0, nb_nodes (graph)):
        n = node(graph, i)
        for j in range(nb_edges(n)):
            e = edge(n, j)
            if e.start ==n:
                source.write("(edge %d "% (edge_nb+1))
                edge_nb += 1
                source.write("%s " % (i+1))
                source.write(" %s )\n"% (graph.nodes.index(e.end)+1))
# Color Property
    source.write("(property  0 color \"viewColor\"\n")
    source.write("(default \"(255,0,0,255)\" \"(0,0,0,255)\" )\n")
    nb_vertex = (nb_nodes(graph))
    nb_signature = graph.nb_signature
    if nb_signature!=0:
        for i in range(0,nb_vertex):
            signature = node(graph,i).signature
            source.write("(node %d \"(" %(i+1))
            source.write("%d ,"%red_color_vertex(signature,nb_signature))
            source.write("%d ,"%green_color_vertex(signature,nb_signature))
            source.write("%d , 255)\")\n"%blue_color_vertex(signature,nb_signature))
    source.write(")\n")
# Node position
##    source.write("(property  0 layout \"viewLayout\"\n")
##    source.write("(default \"(0,0,0)\" \"()\" )\n")
##    nb_vertex = (nb_nodes(graph))
##    nb_signature = graph.nb_signature
##    for i in range(0,nb_vertex):
##        source.write("(node %d \"(" %(i+1))
##        source.write("0 ,")
##        source.write("%d ,"%(50*i))
##        source.write("0)\")\n")
##    source.write(")\n")
    source.write("(property  0 size \"viewSize\"\n")
    source.write("(default \"(10,10,0)\" \"(0.125,0.125,10)\" )\n")
    source.write(") \n")
##    source.write("(displaying ")
##    source.write("(color \"backgroundColor\" \"(255,255,255,255)\")\n ")
##    source.write("(bool \"arrow\" true) \n")
##    source.write("(bool \"nodeLabel\" true)\n ")
##    source.write("(bool \"edgeLabel\" false) \n")
##    source.write("(bool \"metaLabel\" false)\n ")
##    source.write("(bool \"elementOrdered\" false)\n ")
##    source.write("(bool \"autoScale\" true) \n")
##    source.write("(bool \"incrementalRendering\" true) \n")
##    source.write("(bool \"edgeColorInterpolation\" false)\n ")
##    source.write("(bool \"edgeSizeInterpolation\" true) \n")
##    source.write("(bool \"edge3D\" false) \n")
##    source.write("(uint \"orthogonalProjection\" 1)\n ")
##    source.write("(uint \"fontType\" 1)\n ")
##    source.write("(int \"SupergraphId\" 0)\n ")
##    source.write("(coord \"cameraEyes\" \"(69.5,-12.5,833.04)\") \n")
##    source.write("(coord \"cameraCenter\" \"(69.5,-12.5,0)\") \n")
##    source.write("(coord \"cameraUp\" \"(0,1,0)\") \n")
##    source.write("(double \"cameraZoomFactor\" 0.5)\n ")
##    source.write("(double \"distCam\" 833.04) \n")
    source.write(") \n")
    source.close()


