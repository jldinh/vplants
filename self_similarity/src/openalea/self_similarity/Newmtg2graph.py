import sys
from Graph import *


# =========================================================================
def create_edge_father_son(ng , edge_list , father , nodeListVertex , nodeList):
    son_list = ng.Sons(father)
    index_father = nodeListVertex.index(father)
    for son in son_list :
        index_son = nodeListVertex.index(son)
        edge_list += [make_edge(nodeList[index_father],nodeList[index_son],"1")]
        create_edge_father_son(ng , edge_list , son,nodeListVertex,nodeList)
# =========================================================================


# =========================================================================
def mtg2graph(ng , scale=1,root=1,signature_list=[]):
    gr = c_graph()
    gr.set_nb_signature(1)
    nb_nodes = len(ng.Descendants(root,scale))

    nodeList = []
    nodeListVertex = []

    for i in ng.Descendants(root,scale):
        n_i = make_node(i)
        if i in signature_list:
            n_i.signature = 0
        else :
            n_i.signature = -1
        nodeList += [n_i]
        nodeListVertex += [i]

    nodeList.reverse()
    nodeListVertex.reverse()
    gr.nodes = nodeList
    gr.edges = []
    create_edge_father_son(ng , gr.edges , root , nodeListVertex , nodeList)
    return gr
# =========================================================================



# =========================================================================
def find_roots(ng,scale=1):
    roots = []
    for v in ng.VtxList(Scale = scale):
        if ng.Class(v)=='T': # Warning #
        #if ng.Class(v)=='': # Warning #
            roots+=[ng.Sons(v)[0]]
    return roots
# =========================================================================


# =========================================================================
def printSons(node,depth,nb,source):
    i=0
    for n in child_list(node):
        for t in range(depth):
            source.write( "\t")
        source.write("+"+str(n.label)+"\n")
        i+=1
        printSons(n,depth+1,nb+1,source)
# =========================================================================



# =========================================================================
def mtgheadfile(name):
    source = open(name,"w")
    #source.write("#\n")
    #source.write("#\n")
    source.write("CODE:	FORM-A\n")    
    source.write("CLASSES:\n")
    source.write("SYMBOL	SCALE	DECOMPOSITION	INDEXATION	DEFINITION\n")
    source.write("$ 	0	FREE	FREE	IMPLICIT\n")
    source.write("T 	1	FREE	FREE	EXPLICIT\n")
    source.write("S 	2	FREE	FREE	EXPLICIT\n\n")
    source.write("DESCRIPTION :\n")
    source.write("LEFT	RIGHT	RELTYPE	MAX\n")
    source.write("S \t S	<	?\n")
    source.write("S S	+	?\n\n")
    source.write("FEATURES:\n")
    source.write("NAME	TYPE\n")
    source.write("state  real\n\n")
    source.write("MTG:\n")
    source.write("TOPO\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t state\n")
    source.close()
# =========================================================================



# =========================================================================
def graph2mtg(tree,name,i):
    source = open(name,"a")
    root = tree_root(tree)
    source.write("/T"+str(i)+"/S0\n")
    printSons(root,1,1,source)
    source.close()
# =========================================================================