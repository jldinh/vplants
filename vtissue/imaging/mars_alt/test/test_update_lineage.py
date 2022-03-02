import numpy as np
from openalea.image.serial.basics import imread
from vplants.mars_alt.alt import update_lineages as upd_lin
from vplants.mars_alt.alt import optimal_lineage as opt_lin
from vplants.mars_alt.alt.mapping import lineage_from_file
from vplants.mars_alt.alt.candidate_lineaging import equal_lineages
from openalea.tissueshape import *

# create the mapping
mapping = {}
def get_mapping():
    execfile('data/map_dict.py', globals())
    return mapping

def test1():
    mapping = get_mapping()
    im1 = imread('data/seg_1_ok.inr.gz')
    im2 = imread('data/seg_2_ok.inr.gz')
    tissue1 = create_graph_tissue(im1)
    tissue2 = create_graph_tissue(im2)

    new_mapping = upd_lin.has_descendant(mapping)

    assert len(new_mapping) == 323

    new_mapping1 = upd_lin.growth_conservation(new_mapping, tissue1, tissue2)

    print 'growth remove ',len(new_mapping)-len(new_mapping1),' cells'
    assert len(new_mapping)-len(new_mapping1) == 41

    final_mapping = upd_lin.adjacencies_preserved2(new_mapping1, tissue1, tissue2)

    print 'Final mapping : ', len(final_mapping)
    return final_mapping

def test_predicate_and_original_equivalence():
    mapping = get_mapping()
    im1 = imread('data/seg_1_ok.inr.gz')
    im2 = imread('data/seg_2_ok.inr.gz')
    tissue1 = create_graph_tissue(im1)
    tissue2 = create_graph_tissue(im2)

    v1_new_mapping = upd_lin.has_descendant(mapping)
    v1_new_mapping0 = upd_lin.one_connected_component(v1_new_mapping, tissue2)
    v1_new_mapping1 = upd_lin.growth_conservation(v1_new_mapping0, tissue1, tissue2)
    v1_final_mapping = upd_lin.adjacencies_preserved2(v1_new_mapping1, tissue1, tissue2)
    v1_final_mapping_bis = upd_lin.adjacencies_preserved(v1_new_mapping1, tissue1, tissue2)

    v2_new_mapping = upd_lin.original_has_descendant(mapping)
    v2_new_mapping0 = upd_lin.original_one_connected_component(v2_new_mapping, tissue2)
    v2_new_mapping1 = upd_lin.original_growth_conservation(v2_new_mapping0, tissue1, tissue2)
    v2_final_mapping = upd_lin.original_adjacencies_preserved2(v2_new_mapping1, tissue1, tissue2)
    v2_final_mapping_bis = upd_lin.original_adjacencies_preserved(v2_new_mapping1, tissue1, tissue2)

    assert equal_lineages(v1_new_mapping, v2_new_mapping)
    assert equal_lineages(v1_new_mapping0, v2_new_mapping0)
    assert equal_lineages(v1_new_mapping1, v2_new_mapping1)
    assert equal_lineages(v1_final_mapping, v2_final_mapping)
    assert equal_lineages(v1_final_mapping_bis, v2_final_mapping_bis)


    return

def test_update_lineages():
    mapping = get_mapping()
    expert  = lineage_from_file("data/mapping_init.txt")
    im1 = imread('data/seg_1_ok.inr.gz')
    im2 = imread('data/seg_2_ok.inr.gz')

    tissue1 = create_graph_tissue(im1)
    tissue2 = create_graph_tissue(im2)

    # release early ;)
    del im1, im2

    fin_lin, scores = upd_lin.update_lineage(mapping, {}, tissue1, tissue2, [upd_lin.has_descendant_filter(),
                                                                                 upd_lin.growth_conservation_filter(),
                                                                                 upd_lin.adjacencies_preserved2_filter()])
    print 'Final mapping : ', len(fin_lin)
    return fin_lin
