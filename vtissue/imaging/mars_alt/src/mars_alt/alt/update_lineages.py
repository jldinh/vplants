# -*- python -*-
#
#       alt : update_lineages.py
#
#       Copyright 2010-2011 INRIA - CIRAD - INRA
#
#       File author(s): Christophe Pradal <christophe.pradal@cirad.fr>
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#       http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
#
#       OpenAlea WebSite : http://openalea.gforge.inria.fr
#
################################################################################

__license__= "Cecill-C"
__revision__ = " $Id$ "


""" A lineage  (parent cell, descendant cells)=(p,{d1,...,dp}) is added to the set
# if the following conditions are verified."""

from openalea.image.algo.analysis import SpatialImageAnalysis

###################################
# PER LINEAGE PREDICATE FUNCTIONS #
###################################
def predicate_has_descendant(parent, g):
    """
    Remove parent cells without descendant
    """
    return g.descendants(parent, 1).__len__() > 1


def predicate_growth_conservation(parent, g, threshold=0.97):
    """
    The volume of all descendant cells should be larger than the one of the parent cell.
    """
    return (g.vertex_property("volume")[parent] * threshold) <= sum([g.vertex_property("volume")[v] for v in g.descendants(parent, 1) - set([parent])])


def predicate_one_connected_component(parent, g):
    """
    The descendant cells must be adjacent together, i.e. they form one single connected
    component (if they are split in several components, it is probably an erroneous lineage).
    """
    kids = g.descendants(parent, 1) - set([parent])
    return check_connexity(kids, g)
    

def predicate_adjacencies_preserved(parent, g, nb_adj=2):
    """
    The descendant cells of a parent cell adjacent must be adjacent to the descendants
    {d1,...,dp} of p (adjacencies are preserved).
    """

    #g1 = tissue_parent.get_topology('graph_id')
    #g2 = tissue_descendant.get_topology('graph_id')

    children_neighborhood_list = [g.neighbors(child, "s") for child in g.descendants(parent, 1) - set([parent])]
    children_neighborhood = set()

    for n in children_neighborhood_list:
        children_neighborhood = children_neighborhood.union(n)
    
    n_failures = 0
    for neighbor in g.neighbors(parent):
        neighbor_descendant = g.descendants(neighbor, 1)
        if children_neighborhood.intersection(neighbor_descendant) == set():
            n_failures += 1

    return n_failures < nb_adj


def predicate_adjacencies_preserved2(parent, kids, mapping, reverse, analysis_parent, analysis_descendant, nb_adj=2):
    """
    Romain  Fernandez' algorithm.
        children (arbreFille)
        parent (arbre mere)
        mapping (cellMapping) c in mapping => dansMapping[c] = 1
        graph adjacency (tabAdjT0, T1)
    """
    #g1 = tissue_parent.get_topology('graph_id')
    #g2 = tissue_descendant.get_topology('graph_id')

    children1 = set(n1 for n1 in analysis_parent.neighbors(parent) if n1 in mapping)
    parent_child2 = set( reverse[n2] for v2 in mapping[parent] for n2 in analysis_descendant.neighbors(v2) if n2 in reverse)
    if parent in parent_child2:
        parent_child2.remove(parent)

    adjInterLigneeF = len(children1-parent_child2)

    if adjInterLigneeF > nb_adj:
        print 'cell ', parent, ' not adj to ',children1-parent_child2
        return False
    else:
        return True

#####################
# TOPOLOGICAL TOOLS #
#####################
def check_connexity( vertex_ids, g):
    """ Check if the vertices form a single connected component.

    Return True
    """
    if len(vertex_ids) == 0:
        return False
    vids = vertex_ids.copy()
    queue = set([vids.pop()])

    while queue:
        v = queue.pop()
        neigh = set(g.neighbors(v, "s"))
        # Store only the neighbors belonging to the vertices
        neigh = neigh.intersection(vids)

        # Update the queue with the neighbors and remove them from vids
        queue = queue.union(neigh)
        vids.difference_update(queue)

    return False if vids else True


#################################
# THE LINEAGE FILTERING PROCESS #
#################################
def old_update_lineage(mapping, high_confidence, analysis_parent, analysis_descendant, lineage_filters=None, start_label=2):
    """  Given a lineage `mapping`, filter it according to the set of rules described by `lineage_filters`

    :Parameters:
     - `mapping` (dict) - mapping to filter. Keys are parent labels and values are lists of child labels (unmodified).
     - `high_confidence` (dict) - mapping of high-confidence lineages to preserve
     - `tissue_parent` (openalea.celltissue.TissueDB) - Tissue database representing the parent tissue.
     - `tissue_descendant` (openalea.celltissue.TissueDB) - Tissue database representing the child tissue.
     - `lineage_filters` (list) - A list of `LineageFilterer` instances that will filter out the lineages.
     - `start_label` (int) - The value of the first cell label (excluding the background). It defaults to two
                             as often, the watershed reserves label 0 and label 1 is for the background.

    :Result:
     - a tuple (new dictionnary containing the updated mapping, dictionnary of mapping for each filter)
    """
    if lineage_filters is None:
        return mapping
    # -- In visualea, lineage_filters can be a LineageFilterer instead of a list.
    # fortunately, we're type-paranoid and we can test this! --
    #if isinstance(lineage_filters, LineageFilterer):
    #    lineage_filters = [lineage_filters]
    #else:
    #    assert isinstance(lineage_filters, (list, tuple))
    #    assert_list_types(lineage_filters, LineageFilterer)

    # -- transform filter params into actual functions --
    n_filter = len(lineage_filters)

    # -- working copy of the mapping: deletions will happen on this one --
    filtered = mapping.copy()
    # -- reverse mapping : needed for child to parent movements --
    reverse = dict( (v,k) for k,l in mapping.iteritems() for v in l)
    # -- a score map : returned for stats --
    scores   = {}
    # -- go! go! go! --
    for parent, kids in mapping.iteritems():
        if parent < start_label:
            continue
        # -- if the parent is the parent of a high confidence
        # lineage, skip as we don't want to prune it. --
        if parent in high_confidence:
            scores[parent] = float("inf")
            continue

        lineage_scores = [None]*n_filter
        for i, f in enumerate(lineage_filters):
            lineage_scores[i] = f(parent, kids, mapping, reverse, analysis_parent, analysis_descendant)

        scores[parent] = lineage_scores
        if False in lineage_scores:
            del filtered[parent]

    return filtered, scores


def update_lineage(mapping, high_confidence, segmented_image_0, segmented_image_1,
                   lineage_filters=None, start_label=2):
    """  Given a lineage `mapping`, filter it according to the set of rules described by `lineage_filters`

    :Parameters:
     - `mapping` (dict) - mapping to filter. Keys are parent labels and values are lists of child labels (unmodified).
     - `high_confidence` (dict) - mapping of high-confidence lineages to preserve
     - `tissue_parent` (openalea.celltissue.TissueDB) - Tissue database representing the parent tissue.
     - `tissue_descendant` (openalea.celltissue.TissueDB) - Tissue database representing the child tissue.
     - `lineage_filters` (list) - A list of `LineageFilterer` instances that will filter out the lineages.
     - `start_label` (int) - The value of the first cell label (excluding the background). It defaults to two
                             as often, the watershed reserves label 0 and label 1 is for the background.

    :Result:
     - a tuple (new dictionnary containing the updated mapping, dictionnary of mapping for each filter)
    """
    if lineage_filters is None:
        return mapping
    # -- In visualea, lineage_filters can be a LineageFilterer instead of a list.
    # fortunately, we're type-paranoid and we can test this! --
    #if isinstance(lineage_filters, LineageFilterer):
    #    lineage_filters = [lineage_filters]
    #else:
    #    assert isinstance(lineage_filters, (list, tuple))
    #    assert_list_types(lineage_filters, LineageFilterer)

    from vplants.tissue_analysis.growth_analysis import border_cells
    import numpy as np
    cell_list_0=list(set(np.unique(segmented_image_0))-set(border_cells(segmented_image_0)))
    cell_list_1=list(set(np.unique(segmented_image_1))-set(border_cells(segmented_image_1)))
    
    from openalea.image.algo.graph_from_image import graph_from_image
    graph_0=graph_from_image(segmented_image_0,labels=cell_list_0, default_properties = ['volume'])
    graph_1=graph_from_image(segmented_image_1,labels=cell_list_1, default_properties = ['volume'])
        
    from openalea.container import TemporalPropertyGraph
    g = TemporalPropertyGraph()
    g.extend([graph_0,graph_1],[mapping])

    # -- transform filter params into actual functions --
    n_filter = len(lineage_filters)
    filtered = mapping.copy()
    scores   = {}
    parents = [p for p in g.vertices() if g.vertex_property("index")[p]==0]
    print "graphs made, lets the game begin"
    for p in parents :
        if p < start_label:
            continue
        
        if p in high_confidence:
            scores[p] = float("inf")
            continue
        
        lineage_scores = [None]*n_filter
        for i, f in enumerate(lineage_filters):
            lineage_scores[i] = f(p, g)

        scores[p] = lineage_scores
        if False in lineage_scores:
            del filtered[p]

    return filtered, scores




######################
# Filterer FACTORIES #
######################
class LineageFilterer(object):
    """Base class for functors used to determine if a lineage (parent->children association) is valid.

    You mainly need to reimplement the __call__ function so that it returns True or False
    to the lineage it is submited.
    """

    def __call__(self,  parent, kids, mapping, reverse, tissue_parent, tissue_descendant):
        raise NotImplementedError


class _BuiltinPredicateFilterer(LineageFilterer):
    """A Subclass of LineageFilterer that wraps predicates.

    Keyword arguments are constructed by the *get_kwargs* method and passed on to the predicate
    """
    # -- a mapping from param name to predicate function --
    to_predicates = dict( (k.split("predicate_")[1],v) for k,v in globals().copy().iteritems() if k.startswith("predicate_") )

    def __init__(self, name):
        self.pred = _BuiltinPredicateFilterer.to_predicates[name]

    def __call__(self,  parent, kids, mapping, reverse, tissue_parent, tissue_descendant):
        return self.pred(parent, kids, mapping, reverse, tissue_parent, tissue_descendant)

    def get_kwargs(self):
        d = self.__dict__.copy()
        del d["pred"]
        return d

def has_descendant_filter():
    return _BuiltinPredicateFilterer("has_descendant")
has_descendant_filter.__doc__ = predicate_has_descendant.__doc__

def growth_conservation_filter(threshold=0.97):
    return _BuiltinPredicateFilterer("growth_conservation")
growth_conservation_filter.__doc__ = predicate_growth_conservation.__doc__

def one_connected_component_filter():
    return _BuiltinPredicateFilterer("one_connected_component")
one_connected_component_filter.__doc__ = predicate_one_connected_component.__doc__

def adjacencies_preserved_filter(nb_adj=2):
    par = _BuiltinPredicateFilterer("adjacencies_preserved")
    par.nb_adj = nb_adj
    return par
adjacencies_preserved_filter.__doc__ = predicate_adjacencies_preserved.__doc__

def adjacencies_preserved2_filter(nb_adj=2):
    par = _BuiltinPredicateFilterer("adjacencies_preserved2")
    par.nb_adj = nb_adj
    return par
adjacencies_preserved2_filter.__doc__ = predicate_adjacencies_preserved2.__doc__




#############
# Utilities #
#############

# copied from vplants.mars_alt.mars.reconstruction to avoid
# unreasonable dependency
def assert_list_types(theList, Type):
    """ Checks that the type of each element of a list
    is Type """
    for t in theList:
        assert isinstance(t, Type)




####################################################
# LINEAGE FILTERING FUNCTIONS COME NEXT.           #
# THEY FILTER A MAPPING USING THE PREDICATES ABOVE #
# AND RETURN AN UPDATED MAPPING                    #
####################################################
def has_descendant(mapping):
    """
    Remove parent cells without descendant
    """
    _mapping = mapping.copy()
    for k,v in mapping.iteritems():
        if not predicate_has_descendant(k,v, None, None, None, None):
            del _mapping[k]
    return _mapping


def growth_conservation(mapping, analysis_parent, analysis_descendant, threshold=0.97):
    """
    The volume of all descendant cells should be larger than the one of the parent cell.
    """
    _mapping = mapping.copy()
    for k,v in mapping.iteritems():
        if not predicate_growth_conservation(k,v, None, None, analysis_parent, analysis_descendant):
            del _mapping[k]
    return _mapping

def one_connected_component(mapping, analysis_descendant):
    """
    The descendant cells must be adjacent together, i.e. they form one single connected
    component (if they are split in several components, it is probably an erroneous lineage).
    """
    _mapping = mapping.copy()
    for k,v in mapping.iteritems():
        if not predicate_one_connected_component(k, v, mapping, None, None, analysis_descendant):
            del _mapping[k]
    return _mapping

def adjacencies_preserved(mapping, analysis_parent, analysis_descendant, nb_adj=2):
    """
    The descendant cells of a parent cell adjacent must be adjacent to the descendants
    {d1,...,dp} of p (adjacencies are preserved).
    """
    _mapping = mapping.copy()

    mother = dict( (v,k) for k,l in mapping.iteritems() for v in l)

    vids_rm = set()
    for parent_id, kids in mapping.iteritems():
        # traverse all the neighbors of child_id
        # belonging to the mapping
        if not predicate_adjacencies_preserved(parent_id, kids, mapping, mother,
                                               analysis_parent, analysis_descendant, nb_adj):
            vids_rm.add(parent_id)

    print 'Remove the vertices from the mapping :'
    print vids_rm

    for k in vids_rm:
        del _mapping[k]
    return _mapping

def adjacencies_preserved2(mapping, analysis_parent, analaysis_descendant, nb_adj=2):
    """
    Romain  Fernandez' algorithm.
        children (arbreFille)
        parent (arbre mere)
        mapping (cellMapping) c in mapping => dansMapping[c] = 1
        graph adjacency (tabAdjT0, T1)
    """
    _mapping = mapping.copy()

    mother = dict( (v,k) for k,l in mapping.iteritems() for v in l)

    vids_rm = []

    # Traverse all the cells of T0 present in the mapping
    for v1, kids in mapping.iteritems():
        if not predicate_adjacencies_preserved2(v1, kids, mapping, mother, analysis_parent, analysis_descendant, nb_adj):
            vids_rm.append(v1)

    print 'removed cells ',vids_rm
    for k in vids_rm:
        del _mapping[k]

    return _mapping


###############################################################
# ORIGINAL IMPLEMENTATIONS OF THE LINEAGE FILTERING FUNCTIONS #
# THEY WORK ON THE MAPPING AS A WHOLE AND DO NOT USE THE      #
# PREDICATE FUNCTIONS                                         #
###############################################################
def original_has_descendant(mapping):
    """
    Remove parent cells without descendant
    """
    _mapping = mapping.copy()
    for k,v in mapping.iteritems():
        if len(v) < 1:
            del _mapping[k]
    return _mapping


def original_growth_conservation(mapping, tissue_parent, tissue_descendant, threshold=0.97):
    """
    The volume of all descendant cells should be larger than the one of the parent cell.
    """
    _mapping = mapping.copy()
    volume0 = tissue_parent.get_property("V")
    volume1 = tissue_descendant.get_property("V")
    for k,v in mapping.iteritems():
        vp = volume0[k]
        vd = sum(volume1[value] for value in v)
        if vp * threshold > vd:
            del _mapping[k]
    return _mapping



#def original_one_connected_component(mapping, tissue_parent, tissue_descendant):
def original_one_connected_component(mapping, tissue_descendant):
    """
    The descendant cells must be adjacent together, i.e. they form one single connected
    component (if they are split in several components, it is probably an erroneous lineage).
    """
    _mapping = mapping.copy()
    g = tissue_descendant.get_topology('graph_id')
    for k,v in mapping.iteritems():
        is_connex = check_connexity(v, g)
        if not is_connex:
            del _mapping[k]

    return _mapping

def original_adjacencies_preserved(mapping, tissue_parent, tissue_descendant, nb_adj=2):
    """
    The descendant cells of a parent cell adjacent must be adjacent to the descendants
    {d1,...,dp} of p (adjacencies are preserved).
    """
    _mapping = mapping.copy()

    g1 = tissue_parent.get_topology('graph_id')
    g2 = tissue_descendant.get_topology('graph_id')

    mother = dict( (v,k) for k,l in mapping.iteritems() for v in l)

    vids_rm = dict()
    for child_id, parent_id in mother.iteritems():
        # traverse all the neighbors of child_id
        # belonging to the mapping
        for brother_id in g2.neighbors(child_id):
            if brother_id not in mother:
                continue
            pid = mother[brother_id]
            if pid == parent_id:
                continue
            if pid not in list(g1.neighbors(parent_id)):
                # parent_id do not preserve the adjacency
                vids_rm.setdefault(parent_id,0)
                vids_rm[parent_id]+=1
                break

    print 'Remove the vertices from the mapping :'

    vids_rm = dict((k,v) for k,v in vids_rm.iteritems() if v >= nb_adj)
    print vids_rm

    for k in vids_rm:
        del _mapping[k]

    return _mapping

def original_adjacencies_preserved2(mapping, tissue_parent, tissue_descendant, nb_adj=2):
    """
    Romain  Fernandez' algorithm.
        children (arbreFille)
        parent (arbre mere)
        mapping (cellMapping) c in mapping => dansMapping[c] = 1
        graph adjacency (tabAdjT0, T1)
    """
    _mapping = mapping.copy()

    g1 = tissue_parent.get_topology('graph_id')
    g2 = tissue_descendant.get_topology('graph_id')

    mother = dict( (v,k) for k,l in mapping.iteritems() for v in l)

    vids_rm = []

    # Traverse all the cells of T0 present in the mapping
    for v1 in mapping:
        children1 = set(n1 for n1 in g1.neighbors(v1) if n1 in mapping)
        parent_child2 = set( mother[n2] for v2 in mapping[v1] for n2 in g2.neighbors(v2) if n2 in mother)
        if v1 in parent_child2:
            parent_child2.remove(v1)

        adjInterLigneeF = len(children1-parent_child2)

        if adjInterLigneeF > nb_adj:
            print 'cell ', v1, ' not adj to ',children1-parent_child2
            vids_rm.append((v1,adjInterLigneeF) )

    print 'removed cells ',vids_rm
    for k,v in vids_rm:
        del _mapping[k]

    return _mapping
