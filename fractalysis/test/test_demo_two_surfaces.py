from openalea.core.alea import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *
pm = PackageManager()
pm.init(verbose=False)

app = QApplication([])

def test_demo_two_surfaces():
    """ Test dataflow demo TwoSurfaces"""
    res = run(('Demo.TwoSurfaces', 'TwoSurfaces'), {}, pm=pm)
    assert res == []



