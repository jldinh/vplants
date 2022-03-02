import sunDome as sd
import openalea.plantgl.all as pgl

from math import radians, pi

def azel2vect(az, el):
  v = -pgl.Vector3(pgl.Vector3.Spherical( 1., radians( az ), radians( 90 - el ) ) )
  v.normalize()
  return v


def diffuseInterception(scene):
  return  directionalInterception(scene, directions = sd.skyTurtle())

def directInterception(scene, lat=43.36, long=3.52, jj=221, start=7, stop=19, stp=30, dsun = 1, dGMT = 0):
  direct = sd.getDirectLight( latitude=lat , longitude=long, jourJul=jj, startH=start, stopH=stop, step=stp, decalSun = dsun, decalGMT = dGMT)
  return  directionalInterception(scene, directions = direct)

def totalInterception(scene, lat=43.36, long=3.52, jj=221, start=7, stop=19, stp=30, dsun = 1, dGMT = 0):
  diffu = sd.skyTurtle()
  direct =  sd.getDirectLight( latitude=lat , longitude=long, jourJul=jj, startH=start, stopH=stop, step=stp, decalSun = dsun, decalGMT = dGMT)
  all = direct + diffu
  return directionalInterception(scene, directions = all)

def directionalInterception(scene, directions):
  
  redrawPol = pgl.Viewer.redrawPolicy
  pgl.Viewer.redrawPolicy = False
  pgl.Viewer.frameGL.maximize(True)
  pgl.Viewer.widgetGeometry.setSize(600, 600)
  pgl.Viewer.frameGL.setSize(600,600)
  
  pgl.Viewer.camera.setOrthographic()
  pgl.Viewer.grids.set(False,False,False,False)
  bbox=pgl.BoundingBox( scene )
  d_factor = max(bbox.getXRange() , bbox.getYRange() , bbox.getZRange())
  cam_pos,cam_targ,cam_up = pgl.Viewer.camera.getPosition()
  shapeLight = {}

  for d in directions:
    az,el,wg = d
    if( az != None and el != None):
      dir = azel2vect(az, el)
    else :
      dir = -pgl.Viewer.camera.getPosition()[1]

    pgl.Viewer.camera.lookAt(bbox.getCenter() + dir*(-2.5)*d_factor, bbox.getCenter()) #2.5 is for a 600x600 GLframe

    values = pgl.Viewer.frameGL.getProjectionPerShape()
    if not values is None:
      nbpixpershape, pixsize = values
      pixsize = pixsize*pixsize
      for key,val in nbpixpershape:
        if shapeLight.has_key(key):
          shapeLight[key] += val*pixsize*wg
        else:
          shapeLight[key] = val*pixsize*wg
  #valist = [shapeLight[key] for key in shapeLight.keys() ]
  #print "Min value : ", min(valist)
  #print "Max value : ", max(valist)
  pgl.Viewer.camera.lookAt(cam_pos, cam_targ ) 
  pgl.Viewer.redrawPolicy = redrawPol
  return shapeLight

