import openalea.plantgl.all as pgl
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from nose import with_setup

import warnings
if not QCoreApplication.instance() is None:
    warnings.warn("A QApplication is already running")
else:
    app = QApplication([])
    pgl.Viewer.start()


red = pgl.Material(ambient=pgl.Color3(60,10,30),diffuse=3)
green = pgl.Material(ambient=pgl.Color3(30,60,10),diffuse=3)
blue = pgl.Material(ambient=pgl.Color3(10,30,60),diffuse=3)


def setup_func():
  sc = pgl.Scene()
  sc += pgl.Shape(pgl.Box(1,1,1), red, id=1)
  sc+= pgl.Shape(pgl.Translated(4,4,6,pgl.Sphere(1)), blue, id=2)
  sc+= pgl.Shape(pgl.Translated(2,3,-3,pgl.Cone(1,2)), green, id=3)
  sc+= pgl.Shape(pgl.Translated(-8,3,-2,pgl.Box(4,2,0.5)), blue, id=4)
  sc+= pgl.Shape(pgl.Translated(-4,-2,5,pgl.EulerRotated(3.14,2.7,0,pgl.Cone(2,5))), green, id=5)
  sc+= pgl.Shape(pgl.Translated(4,-3,-3,pgl.Sphere(2)), red,id=6)
  return sc


def test_projectionPerShape():
  sc = setup_func()
  pgl.Viewer.display(sc)
  nbPixSh, pixSize = pgl.Viewer.frameGL.getProjectionPerShape()
  idScene = [sh.id for sh in sc]
  idScene.sort()
  idProj = [pr[0] for pr in nbPixSh]
  idProj.sort()
  idProj.append(1)
  print idProj
  for s,p in zip(idScene,idProj):
    assert s == p
    print s,p


def test_onedirectionIntercept():
  import openalea.fractalysis.light.directLight as directlight
  sc = setup_func()
  #pgl.Viewer.display(sc)
  sl = directlight.diffuseInterception(sc)
  print sl

  idScene = [sh.id for sh in sc]
  idScene.sort()
  print idScene
  idProj =  sl.keys()
  idProj.sort()
  print idProj
  for s,p in zip(idScene,idProj):
    assert s == p
    print s,p

def test_diffuseIntercept():
  import openalea.fractalysis.light.directLight as directlight
  resTh = {1: 9.8448065580128272, 2: 5.0847243048578248, 3: 3.8538849231842898, 4: 39.798083007743848, 5: 19.153635763962416, 6: 19.071452238385543}
  # {1: 202.27221755458467, 2: 104.24717664386343, 3: 79.193779365397333, 4: 813.04898461736377, 5: 392.70741269083277, 6: 392.09196465811743}
  sc = setup_func()
  sl = directlight.diffuseInterception(sc)
  for k in sl.keys(): 
      if k <= len(resTh):
          assert abs(sl[k] - resTh[k]) < 0.5

if __name__ == "__main__":
  test_projectionPerShape()
  test_onedirectionIntercept()
  test_diffuseIntercept()


