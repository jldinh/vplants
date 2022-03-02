
from openalea.image.all import *
from openalea.tissueshape import *
from openalea.celltissue import TissueDB
from openalea.core.path import path
from vtissuedata import get_shared_data

import numpy as np
from openalea.container import *


def check_dist(pt1, pt2, eps2=1e-4):
    def d2(p1,p2):
        return np.sum((p1-p2)**2)
    err = 0.
    for k in pt1:
        if k!=1:
            assert d2(pt1[k],pt2[k]) < eps2
            err = max(err, d2(pt1[k],pt2[k]))
    print 'ERREUR :',err

def check( d1, d2, eps=1e-5):
    for k in d1:
        if k!=1:
            assert abs(d1[k]-d2[k]) < eps, 'Cell %d: error %f'%(k,abs(d1[k]-d2[k]) )

def check_edge( d1, d2, eps=0.1):
    for s,t in d1:
        if s!=1:
            if abs(d1[s,t]-d2[s,t]) > eps:
                print  'Edge (%d, %d)'%(s,t) ,': error %f'%(abs(d1[s,t]-d2[s,t]) )

def test():
    fn =  get_shared_data('segmentation.inr.gz')
    im = imread(fn)

    tissue = create_graph_tissue(im)
    if path('data/tissue.pdb').isfile():
        tissue_ref = TissueDB()
        tissue_ref.read('data/tissue.pdb')
    else:
        tissue_ref = extract_graph_tissue(im)

    g1 = tissue.get_topology('graph_id')
    g2 = tissue_ref.get_topology('graph_id')

    assert g1.nb_vertices() == 358
    assert g1.nb_edges() == 2265

    assert g1.nb_vertices() == g2.nb_vertices(), '%d = %d'%(g1.nb_vertices(), g2.nb_vertices())

    #Check volumes
    V1 = tissue.get_property('V')
    V2 = tissue_ref.get_property('V')
    check(V1,V2)

    #nb1 = tissue.get_property('nb')
    #nb2 = tissue_ref.get_property('nb')
    #check(nb1,nb2)

    b1 = tissue.get_property('bary')
    b2 = tissue_ref.get_property('bary')
    check_dist(b1,b2, eps2=0.15)


    return tissue, tissue_ref

def test_wall_contact():
    tissue, tissue_ref = test()
    nb1 = tissue.get_property('nb')
    nb2 = tissue_ref.get_property('nb')

    return tissue, tissue_ref, nb1, nb2

def test_dynamic_graph():
    fn =  get_shared_data('segmentation.inr.gz')
    im = imread(fn)

    tissue = create_graph_tissue(im)
    g = tissue.get_topology('graph_id')
    V = tissue.get_property('V')
    S = tissue.get_property('S')
    bary = tissue.get_property('bary')

    g1 = PropertyGraph()
    Graph.extend(g1,g)

    g1.add_vertex_property('V')
    g1.vertex_property('V').update(V)

    g1.add_vertex_property('bary')
    g1.vertex_property('bary').update(bary)

    g1.add_edge_property('S')
    g1.edge_property('S').update(S)

    graph = TemporalPropertyGraph()
    graph.append(g1)
    return graph, tissue
    


if __name__ == '__main__':
    test()