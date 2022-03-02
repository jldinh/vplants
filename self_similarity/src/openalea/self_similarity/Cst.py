import sys
from Graph import *

def signature_position(signature_list,signature):
    if signature == [] :
        return 0
    else:
        signature.sort()
        for i in range(len(signature_list)):
            if signature_list[i]==signature :
                return i+1
        return None


def tree_reduction(tree):
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
        reduction_dag.nodes = node_list
        reduction_dag.edges = edge_list
        n.signature = node_signature_position
    reduction_dag.set_nb_signature(nb_nodes(reduction_dag))
    return reduction_dag


def tree_reconstruction(graph):
    tree = c_graph()
    tree.nb_signature = nb_nodes(graph)
    nb = 0
    tree_node = make_node("S"+str(nb))
    node_list = [tree_node]
    edge_list = []
    signature = nb_nodes(graph)-1
    #signature = 0
    tree_node.signature = signature
    tree_list = [tree_node]
    while tree_list != []:
        tree_node = tree_list.pop()
        signature = tree_node.signature
        n = node(graph,signature)
        for j in range(nb_edges(n)):
            e = edge(n,j)
           # print e.label
            if e.start == n:
                for k in range(int(e.label)):
                    nb += 1
                    n_i = make_node("S"+str(nb))
                    n_i.signature = e.end.signature
                    node_list += [n_i]
                    e = make_edge(tree_node,n_i,str(1))
                    edge_list += [e]
                    tree_list.append(n_i)
    tree.nodes = node_list
    tree.edges = edge_list
    return tree


def list_of_edge_value_at_max_height(g,height,node):
    value_list = []
    if height >= node.height :
        print "depth is too large !!!"
    else :
        l_desc = node_list_at_a_maximum_height(g,height)
        for l in l_desc :
            value_list += [int(edge_label(node,l))]
    value_list.reverse()
    return value_list
                

def complete_value_node(g,max_value,node,height):
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
        l_ni[0] = max_value
        l_ni[i] -= r_tmp
    else :
        l_ni[0] = max_value
        for i in range(1,len(l_ni)):
            l_ni[i]=0
    l_ni.reverse()
    return l_ni


def height_graph_update(dag,node,new_value,height):
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


def complete_height(dag,height):
    nodelist = node_list_at_given_height(dag,height)
    current_height = height-1
    while current_height >= 0:
        node_list_h_current_h = node_list_between_two_given_heights(dag,height,current_height)
        max_value = max_node_value_between_two_heights(dag,height,current_height)
        for current_node in nodelist:
            new_values = complete_value_node(dag,max_value,current_node,current_height)
            height_graph_update(dag,current_node,new_values,current_height)
        current_height -= 1
    remove_equivalent_node_at_height(dag,height)
 

    

def remove_equivalent_node_at_height(dag,height):
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
    max_height = height_of_graph(dag)
    for i in range(max_height):
         complete_height(dag,i)
    for i in range(nb_nodes(dag)):
        current_node = node(dag,i)
        current_node.signature = i
