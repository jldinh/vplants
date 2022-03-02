from openalea.core.alea import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *

pm = PackageManager()
pm.init(verbose=False)

app = QApplication([])

def test_demo_mtg_PlantFrame2():
    """ Test dataflow demo PlantFrame2 """
    res = run(('demo.mtg', 'PlantFrame2'), {}, pm=pm)
    assert res == []


def test_demo_mtg_multiplemtg():
    """ Test dataflow demo multiple MTG"""
    res = run(('demo.mtg', 'MTGActionOnMultipleMTGs'), {}, pm=pm)
    assert res == []


def test_demo_mtg_selection():
    """ Test dataflow demo Component Selection """
    res = run(('demo.mtg', 'MTGComponentSelection'), {}, pm=pm)
    assert res == []

def test_demo_mtg_extraction():
    """ Test dataflow demo MTG extraction """
    res = run(('demo.mtg', 'MTGExtraction'), {}, pm=pm)
    assert res == []

