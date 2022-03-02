from openalea.aml import *


def test_mtg():

    m = MTG("data/stand.mtg")
    assert m


# def test_agraf():

#     g  = MTG("agraf.mtg")
#     dr1 = DressingData("agraf.drf")
#     f1 = PlantFrame(1, Scale=3, DressingData=dr1)
#     #Plot(f1)

#     assert g and dr1 and f1



def test_drf():

    mtg = MTG("data/testdrf.mtg")
    drf = DressingData("data/testdrf.drf")
    pf = PlantFrame (0, DressingData=drf)
    
