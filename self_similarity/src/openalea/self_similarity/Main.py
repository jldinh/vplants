import sys
import os

from openalea.mtg import *
from openalea.lpy import *
from openalea.mtg.io import axialtree2mtg
from openalea.deploy.shared_data import shared_data
from openalea import self_similarity

from openalea.self_similarity.Cst import *
from openalea.self_similarity.Newmtg2graph import *
from openalea.self_similarity.Mtg2tulip import *

from datetime import datetime

# =========================================================

from openalea.tree_matching.mtgmatching import *

class MtgNodeCost(NodeCost):
    def getDeletionCost(self,a) : return 1
    def getInsertionCost(self,b) : return 1
    def getChangingCost(self,a,b) : return 0

# =========================================================

shared = shared_data(self_similarity)

# The full database is here: https://scm.gforge.inria.fr/svn/vplants/vplants/branches/SelfSimilarityDatabase.

path_out_default=shared+"/DataOut/"
path_in_default=shared+"/Database/"

# =========================================================

def create_mtg(name, path_in=path_in_default, mtg_extension=True):

    path=path_in+name

    if mtg_extension:
        # print "read the mtg file"
        ng=MTG(path)
    else:
        # print "read the str file"
        cstring = file(path).read()
        cstring = cstring.replace('#','_')
        cstring = cstring.replace('\r\n','')
        l = Lstring(cstring)
        ng = axialtree2mtg(l,{'T':1,'A':1,'K':1},None)

    return ng

# =========================================================

def compression(ng, path_out=path_out_default):

    # ===============================
    #roots = find_roots(ng)
    #r=roots[0]
    r=1
    # ===============================

    tree = mtg2graph(ng,3,r)
    dag = tree_reduction(tree)

    str_date=str(datetime.today()).replace(' ','_')
    path_tulip = path_out+"tulip"
    path_tmp_trees = path_out+"tmp_trees"
    save_tulip(dag,path_tulip+"/dag"+str_date+".tlp")

    tree_colored = tree_reconstruction(dag)
    dag_linearization(dag)
    nest = tree_reduction(dag)
    nest_tree = tree_reconstruction(dag)

    dag_linearization(dag)
    nest = tree_reduction(dag)
    nest_tree = tree_reconstruction(dag)

    save_tulip(nest,path_tulip+"/dag_nest"+str_date+".tlp")

    mtgheadfile(path_tmp_trees+"/TreeAndNest"+str_date+".mtg")
    graph2mtg(tree_colored,path_tmp_trees+"/TreeAndNest"+str_date+".mtg",0)
    graph2mtg(nest_tree,path_tmp_trees+"/TreeAndNest"+str_date+".mtg",1)

    mtgheadfile(path_tmp_trees+"/Tree"+str_date+".mtg")
    graph2mtg(tree_colored,path_tmp_trees+"/Tree"+str_date+".mtg",0)

    tree_mtg=MTG(path_tmp_trees+"/Tree"+str_date+".mtg")
    write_tlp_from_mtg(path_tulip+"/tree"+str_date+".tlp",tree_mtg,t0=2)

    mtgheadfile(path_tmp_trees+"/NEST"+str_date+".mtg")
    graph2mtg(nest_tree,path_tmp_trees+"/NEST"+str_date+".mtg",0)

    nest_mtg=MTG(path_tmp_trees+"/NEST"+str_date+".mtg")
    write_tlp_from_mtg(path_tulip+"/NEST"+str_date+".tlp",nest_mtg,t0=2)

    ng2 = MTG(path_tmp_trees+"/TreeAndNest"+str_date+".mtg")

    roots_to_compare = [v for v in ng2.VtxList(Scale=1)]

    a=ng2.sub_mtg(roots_to_compare[0])
    b=ng2.sub_mtg(roots_to_compare[1])

    cost = MtgNodeCost()
    m=MtgMatching(a,b,scale1=1,scale2=1,cost=cost)
    distance=m.match()

    return distance

# ====================================================

def basic_compression(ng):

    roots = find_roots(ng)
    r=roots[0]
    tree = mtg2graph(ng,3,r)
    dag = tree_reduction(tree)

    tree_colored = tree_reconstruction(dag)
    dag_linearization(dag)
    nest = tree_reduction(dag)
    nest_tree = tree_reconstruction(dag)

    dag_linearization(dag)
    nest = tree_reduction(dag)
    nest_tree = tree_reconstruction(dag)

    return dag, nest, nest_tree

# ====================================================