#!/usr/bin/python
# -*- python -*-
#
#       vplants.mars_alt.alt.flow_graph
#
#       Copyright 2006-2011 INRIA - CIRAD - INRA
#
#       File author(s): Daniel Barbeau <daniel.barbeau@sophia.inria.fr>
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
#
#       OpenAlea WebSite : http://openalea.gforge.inria.fr
#
###############################################################################

__license__= "Cecill-C"
__revision__ = " $Id: optimal_lineage.py 12685 2012-08-24 12:13:53Z chakkrit $ "


from openalea.core.logger import get_logger
myLogger = get_logger(__name__)




def optimal_lineage(maxLabel0,
                    maxLabel1,
                    candidates=None,
                    expert_lineage=None,
                    ndiv=8,
                    optimization_method="rf_flow"):
    """ Given two images of an organ at t0 and t1, tries to find cell lineages.

    .. note:: Image labels are expected to start from 2 (1 being the background)

    :Parameters:
      - `maxLabel0` (int) -  the highest label for mothers
      - `maxLabel1` (int) -  the highest label for children
      - `candidates` (dict) - a dictionnary mapping mother labels to a list of child labels+scores. Labels should start at 2, 1 being the background.
      - `expert_lineage` (dict) - a dictionnary mapping mother labels to a list of child labels. Labels should start at 2, 1 being the background.
      - `ndiv` :  an limit to the number of divisions a cell can have between the two images
      - `optimization_method` : name of the flow graph solving. "rf_flow" is the original published implementation by Romain Fernandez.
         "nx_simplex" is the simplex method provided by networkx.

    :Returns:
        A dictionnary mapping mothers to children.
    """
    if None in [maxLabel0, maxLabel1]:
        myLogger.error("Lineaging got null input image")
        return (None,)

    # don't put default container arguments
    # as they are shared between instances and bring in MANY side effects:
    if candidates is None:
        candidates = {}

    if expert_lineage is None:
       expert_lineage = {}
    candidates = merge_expert_and_candidates(expert_lineage, candidates)

    # maxLabel0 = im_0.max()
    # maxLabel1 = im_1.max()

    # -- label 0 is reserved for watershed,
    # label 1 is background, labels start at 2 --
    # nMothers  = maxLabel0-1 #-2+1 as we count from 0
    # nChildren = maxLabel1-1 #-2+1 as we count from 0

    if optimization_method=="rf_flow":
        ffunc = rfernandez_flow_solving
    elif optimization_method=="nx_simplex":
        ffunc = nx_flow_solving
    elif optimization_method=="basic_solve":
        ffunc = basic_optimal_lineage
    else:
        raise Exception("unknown optimization method: " + optimization_method)

    return ffunc(ndiv, candidates, maxLabel0, maxLabel1)#, nMothers, nChildren)

    
#########################################
# A basic optimal vertex cover solution #
########################################

def basic_optimal_lineage(ndiv, candidates, maxLabel0, maxLabel1):
    """Build a dict of a "good" solution of the lineaging problem 
    
    :Parameters:
    - `candidates` (dict) : a mapping of mothers-to-children-and-score as returned by
    vplants.mars_alt.alt.candidate_lineaging.candidate_lineaging.
    :Returns:
        A dictionnary mapping mothers to children.
    """

    # here we take the inverse dict
    inv_candidates={}
    for m in candidates.iterkeys():
        for k in candidates[m][:]:
            inv_candidates.setdefault(k[0], []).append((k[1], m))

    # here we had the virtual mother
    for k in inv_candidates.iterkeys():
        inv_candidates[k].append((-50, "virt"))

    final_candidates={}
    #minitab=[]

    for k in inv_candidates.iterkeys():
        maxi=max(inv_candidates[k])
        #minitab.append(mini)
        if maxi[0]>-50.0: final_candidates.setdefault(maxi[1], []).append(k)
    return final_candidates

    
    
    
    
########################################################################
# A mapping solver that uses numpy, scipy and networkX implementations #
########################################################################
import networkx as nx

def nx_flow_solving(ndiv, candidates, maxLabel0, maxLabel1, with_prime_sink=False):
    """Build and solve lineage flow graph from candidates lineage.

    .. note:: Image labels are expected to start from 2 (1 being the background)

    We use networkX' simplex graph solver.

    Here are the rules to build the graph:
      * one source node, one sink node
      * one virtual mother node to connect cells in t1 that have no mom in t0
      * one virtual child node to connect cells in t0 that have no child in t1
      * a set of real mothers, each of them receiving flow from source node
      * a set of real children, each of them receiving flow from one real mother node
        and sending flow to sink
      * sink sends back flow to source


    The flow bounds (min&max capacities) are:
      * mother->candidate child : 0 <= flow <= 1
      * source->real mothers : 1 <= flow <= ndivmax (ndiv)
      * source->virt mother  : 0 <= flow <= count(real children) aka Nj
      * real child->sink : flow == 1
      * virt child->sink : 0 <= flow <= count(real mothers) aka Ni
      * sink -> source : max(Nj,Ni) <= flow <= Nj + Ni

    The flow costs are:
      * mother->candidate child : cost=1-Score(Mother->Child)
      * mom/child->virtual : cost=2

    NOTE: minimal capacities are represented by equal demands
    on the node after the edge.

    :Parameters:
        - `ndiv` (int) :  a limit to the number of divisions a cell can have between two images.
        - `candidates` (dict) : a mapping of mothers-to-children-and-score as returned by
           vplants.mars_alt.alt.candidate_lineaging.candidate_lineaging.
        - `maxLabel0` (int) :  the highest label for mothers
        - `maxLabel1` (int) :  the highest label for children
        - `nMothers`  (int - to be discarded) : number of mothers  (can be inferred from maxLabel0).
        - `nChildren` (int - to be discarded) : number of children (can be inferred from maxLabel1).

    :Returns:
        A dictionnary mapping mothers to children.
    """

    # -- identify orphans and childless mothers. --
    childless_mothers = set(range(2, maxLabel0+1)) - set(candidates.iterkeys())
    motherless_childs = set(range(2, maxLabel1+1)) - \
                        set(chLab[0] for kids in candidates.itervalues() for chLab in kids) # -- power!

    nMothers  = maxLabel0-1 #-2+1 as we count the background too.
    nChildren = maxLabel1-1 #-2+1 as we count the background too.
    print "nMothers=", nMothers
    print "nChildren=", nChildren

    # -- build the simplex
    # in the following code, mom nodes are prefixed
    # with "m" and child nodes are prefixed with "k" (kids) --
    g = nx.DiGraph()
    # - some remarkable nodes -
    virtMother = "vMom"
    virtChild  = "vChi"
    source     = "src"
    sink       = "sink"

    if with_prime_sink:
        sink_p     = "sink_p"

    prohibitiveCost = 2
    costSum=0
    g.add_node( source, demand=-nMothers-2*nChildren )
    g.add_node( sink,   demand=nChildren)
    g.add_node( virtMother, demand=0 )
    g.add_node( virtChild, demand=0 )
    if(with_prime_sink):
        g.add_node( sink_p, demand=nChildren) #FIX DEMAND HERE

    # - connect source and sink to virtual dudes -
    g.add_edge(source,    virtMother, capacity=nChildren)
    if not with_prime_sink:
        g.add_edge(virtChild, sink,       capacity=nMothers)
    else:
        g.add_edge(virtChild, sink_p,     capacity=nMothers) #FIX CAPACITIES HERE
        g.add_edge(sink,      sink_p,     capacity=max(nChildren, nMothers))

    # - connect candidate moms and kids -
    """
    for mom, kids in candidates.iteritems():
        if mom==1: #background
            continue
        mom = "m"+str(mom)
        g.add_node(mom, demand=1)
        costSum+=1
        g.add_edge(source, mom, capacity=ndiv)
        
        # mother-to-virtchild
        g.add_edge(mom, virtChild, capacity=1, weight=prohibitiveCost)
        if mom == "m48" : print mom
        for k in kids: 
            kLabel = "k"+str(k[0])
            kDist  = k[1]
            if not kLabel in g : 
                g.add_node(kLabel, demand=1)
                costSum+=1
                if kLabel=="k46" : print kLabel
            # mom-to-child edge:
            g.add_edge(mom, kLabel, capacity=1, weight=kDist)
            # child-to-sink edge:
            g.add_edge(kLabel, sink, capacity=1)
            # virt-mother-to-child
            g.add_edge(virtMother, kLabel, capacity=1, weight=prohibitiveCost)
    if not with_prime_sink:
        g.add_edge(sink, source, capacity=nMothers+nChildren)
    else:
        g.add_edge(sink_p, source, capacity=nMothers+nChildren) #FIX CAPACITY HERE!

    for mom in childless_mothers:
        mom = "m"+str(mom)
        g.add_node(mom, demand=1)
        costSum+=1
        g.add_edge(source, mom, capacity=nChildren)
        g.add_edge(mom, virtChild, capacity=1, weight=prohibitiveCost)

    for k in motherless_childs:
        k = "k"+str(k)
        g.add_edge(virtMother, k, capacity=1, weight=prohibitiveCost)
        g.add_edge(k, sink, capacity=1)
        """

    #New Version To Make The Graph (it seems to work ...) !! (LEO)
    children=[]
    for i in range(2, maxLabel0+1):
        mom="m"+str(i)
        g.add_node(mom, demand=1)
        g.add_edge(source, mom, capacity=ndiv)
        g.add_edge(mom, virtChild, capacity=1, weight=prohibitiveCost)
        if i in candidates:
            for k in candidates[i][:]:
                kLabel="k"+str(k[0])
                kDist=k[1]
                if not kLabel in g:
                    g.add_node(kLabel, demand=1)
                    children.append(k[0])
                g.add_edge(mom, kLabel, capacity=1, weight=kDist)
                g.add_edge(kLabel, sink, capacity=1)
                g.add_edge(virtMother, kLabel, capacity=1, weight=prohibitiveCost)
    
    for i in range(2, maxLabel1+1):
        if not i in children:
            kLabel="k"+str(i)
            g.add_node(kLabel, demand=1)
            g.add_edge(kLabel, sink, capacity=1)
            g.add_edge(virtMother, kLabel, capacity=1, weight=prohibitiveCost)

    if not with_prime_sink:
        g.add_edge(sink, source, capacity=nMothers+nChildren)
    else:
        g.add_edge(sink_p, source, capacity=nMothers+nChildren) #FIX CAPACITY HERE!
    
    print "mommies' demands", sum(g.node["m"+str(v)]["demand"] for v in range(2, maxLabel0))
    print "source's demand", g.node[source]["demand"]
    print "sink's demand", g.node[sink]["demand"]
    print "demand sum", sum(d["demand"] for v, d in g.nodes(data = True) if "demand" in d)

    #flowdict = nx.min_cost_flow(g)
    flowdict = nx.network_simplex(g, weight=True)
    
    #return flowdict
    
    # Looks like another nice call to me:
    # flowdict = nx.max_flow_min_cost(g, source, sink)

    #we need to filter the flowdict a little bit to just obtain the mother->child mappings
    #and to convert the "mXXX" and "kXXX" nodes to ints. This is voodoo.
    return dict( [(eval(m[1:]), [eval(k[1:]) for k,flow in kids.iteritems() if k[0]=="k" and flow==1]) \
                  for m, kids in flowdict[1].iteritems() if m[0]=="m" ] )

nx_flow_solving.distances_as_scores = False









#########################################
# The original solver wrapped in ctypes #
#########################################
import ctypes
import struct
import numpy as np
from openalea.core.ctypes_ext import find_library


def rfernandez_flow_solving(ndiv, candidates, maxLabel0, maxLabel1):#, nMothers, nChildren):
    """Build and solve lineage flow graph from candidates lineage.

    Look at the `Nature Methods paper <http://www-sop.inria.fr/asclepios/biblio/REP/publi.php?name=Author/FERNANDEZ-R.html>`
    for details concerning this implementation.

    Careful: Image labels are expected to start from 2 (1 being the background)

    :Parameters:
        - `ndiv` (int) :  a limit to the number of divisions a cell can have between two images.
        - `candidates` (dict) : a mapping of mothers-to-children-and-score as returned by
           vplants.mars_alt.alt.candidate_lineaging.candidate_lineaging.
        - `maxLabel0` (int) :  the highest label for mothers
        - `maxLabel1` (int) :  the highest label for children
        - `nMothers`  (int - to be discarded) : number of mothers  (can be inferred from maxLabel0).
        - `nChildren` (int - to be discarded) : number of children (can be inferred from maxLabel1).

    :Returns:
        A dictionnary mapping mothers to children.
    """
    # -- configure the ctypes lib --
    lin = ctypes.CDLL(find_library("lineage"))
    CT_UINT_P   = ctypes.POINTER(ctypes.c_uint)
    CT_DOUBLE_P = ctypes.POINTER(ctypes.c_double)
    CT_CHAR_P   = ctypes.POINTER(ctypes.c_char)
    lin.compute_lineage_mapping.argtypes = [ctypes.c_uint,
                                            ctypes.c_uint,
                                            ctypes.c_uint,
                                            CT_UINT_P,
                                            CT_UINT_P,
                                            CT_DOUBLE_P,
                                            CT_CHAR_P]


    nMothers  = maxLabel0-1 #-2+1 as we count the background too.
    nChildren = maxLabel1-1 #-2+1 as we count the background too.

    # We need to bump these numbers again since romain's code uses
    # std::vectors to index the labels, and labels start at 2.
    momVectSize = nMothers + 2
    kidVectSize = nChildren + 2

    nPairs = sum(len(kids) for kids in candidates.itervalues())
    moms = np.zeros(nPairs, dtype=np.uint)
    kids = np.zeros(nPairs, dtype=np.uint)
    scor = np.zeros(nPairs, dtype=np.double)

    i = 0
    # TODO : we might need to sort the candidates by mom labels?
    for m, ks in candidates.iteritems():
        for k, d in ks:
            moms[i] = m
            kids[i] = k
            scor[i] = d
            i+=1

    moms_ptr = moms.ctypes.data_as(CT_UINT_P)
    kids_ptr = kids.ctypes.data_as(CT_UINT_P)
    scor_ptr = scor.ctypes.data_as(CT_DOUBLE_P)

    sz = kidVectSize*ctypes.sizeof(ctypes.c_uint)
    returnedChildren = ctypes.create_string_buffer(long(sz))
    
    print "hello"
    lin.compute_lineage_mapping(momVectSize, kidVectSize, nPairs,
                                moms_ptr, kids_ptr, scor_ptr,
                                returnedChildren)
    print "there"
    fmtString = str(kidVectSize)+"I"
    rezData = struct.unpack_from(fmtString, returnedChildren)

    retTuples = [(v,i) for i,v in enumerate(rezData)]
    ret       = {}
    #ret       = {i:[] for i in xrange(momVectSize)}
    for m, k in retTuples:
        ret.setdefault(m, []).append(k)
        # ret[m].append(k)
    return ret

rfernandez_flow_solving.distances_as_scores = True






###################
# Utility Methods #
###################
def merge_expert_and_candidates(expert, candidates):
    """Merges an expert lineaging and a candidate lineaging
    into one candidate lineaging."""
    candidates = candidates.copy()
    # expert doesn't have distance yet
    expert = dict((mom,[(chLab, 0.0) for chLab in kids]) \
                      for mom, kids in expert.iteritems())
    # overwrite mother to children mappings, this is what romain does
    candidates.update(expert)
    # discard children that are in expert mapping from all other mappings
    # brute force (because I want to go to bed)
    for exp_mom, exp_kids in expert.iteritems():
        exp_kids = set(k for k,d in exp_kids)
        for cand_mom, cand_kids in candidates.iteritems():
            if exp_mom != cand_mom :
                #the mom wasn't updated
                for kid_n_dist in cand_kids[:]:
                    kid = kid_n_dist[0]
                    if kid in exp_kids:
                        cand_kids.remove(kid_n_dist)
    return candidates
