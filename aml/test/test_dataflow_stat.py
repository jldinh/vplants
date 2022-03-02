from openalea.core.alea import *


pm = PackageManager()
pm.init(verbose=False)

def test_demo_corsican():
    """ Test changepoint demo corsican  """
    res = run(('Demo.ChangePoint (gnuplot and aml)','Corsican pine change point'),{},pm=pm)
    assert res == []

def test_demo_dycorinia():
    """ Test dataflow demo dycorinia """
    res = run(('Demo.ChangePoint (gnuplot and aml)','Dycorinia change point'),{},pm=pm)
    assert res == []


if __name__ == "__main__":
    test_demo_corsican()
    test_demo_dycorinia()

