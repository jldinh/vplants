#! /usr/bin/env python
# -*- python -*-
#
#       OpenAlea.Fractalysis : OpenAlea fractal analysis library module
#
#       Copyright or (C) or Copr. 2006-2009 INRIA - CIRAD - INRA  
#
#       File author(s): Da SILVA David <david.da_silva@cirad.fr>
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
# 
#       OpenAlea WebSite : http://openalea.gforge.inria.fr
#


__doc__="""
fractalysis.light nodes
"""

__license__= "Cecill-C"
__revision__=" $Id: light_nodes.py 7873 2010-02-08 18:17:47Z cokelaer $ "

import openalea.fractalysis.light as lit
import openalea.plantgl.all as pgl

from openalea.fractalysis.fractutils.pgl_utils import centerScene

opacities = {'Pinus':0.89, 'Sorbus':0.88, 'Betula':0.89, 'Carpinus':0.967, 'Quercus':0.967, 'Malus':0.948, 'Misc':0.85, 'Populus':0.918, 'trunk_mat':1, 'houppier_mat':0.935, 'Wall':0.8
            }

def create_MSS( name, scene, scale_table=None, hull_type='Cvx Hull', opac={} ):
  scc = centerScene( scene )
  if scale_table==None:
    scale_table=[{1:[long(sh.id) for sh in scc]}]
    ss = lit.ssFromDict( name, scc, scale_table, hull_type)
    l=ss.get1Scale(2)
    for i in l:
      n = ss.getNode(i)
      specie = n.shape.appearance.name
      for k in opac.keys():
        opacities[k] = opac[k]
      n.globalOpacity = opacities.get(specie, 0.935)
      g = n.shape.geometry
      try:
        while (not isinstance(g, pgl.Cylinder)):
          g =g.geometry
        n.opak=True
      except AttributeError :
        pass
  else:
    ss = lit.ssFromDict( name, scc, scale_table, hull_type)
  #ss.checkFactor(150,150,8,0)
  return ss

def light_intercept(mss, light_direction, distr, img_size, save_path):
  distSize = {"100x100":(100,12), "150x150":(150,8), "200x200":(200,7), "300x300":(300,4), "600x600":(600,2.5)} 
  azimuth = light_direction[0]
  elevation = light_direction[1]
  weight = light_direction[2]
  if img_size in distSize.keys():
    wth = distSize[img_size][0]
    hth = distSize[img_size][0]
    distfactor = distSize[img_size][1]
  else:
    wth = 150
    hth = 150
    distfactor = 8

  if distr != None:
    cdist = [distr]
  else:
    distr = ['A']*(mss.depth - 1)
    cdist = None

  res = mss.computeDir(az=azimuth, el=elevation, wg=weight, distrib=cdist, width=wth, height=hth, d_factor=distfactor, pth=save_path)

  return res['Star_turbid'], res['Star_'+str(distr)], res['Pix_'+str(distr)]

def light_received(mss, scl, light_direction, mod, img_size, save_path):
  distSize = {"100x100":(100,12), "150x150":(150,8), "200x200":(200,7), "300x300":(300,4), "600x600":(600,2.5)} 
  azimuth = light_direction[0]
  elevation = light_direction[1]
  weight = light_direction[2]
  if img_size in distSize.keys():
    wth = distSize[img_size][0]
    hth = distSize[img_size][0]
    distfactor = distSize[img_size][1]
  else:
    wth = 150
    hth = 150
    distfactor = 8

  res, sc = mss.received_light(scale=scl, az=azimuth, el=elevation, wg=weight, mode=mod, width=wth, height=hth, d_factor=distfactor, pth=save_path)
  lit.prepareScene(sc, 300, 300, azimuth, elevation,4)
  return res, sc

def generate_pix(mss, light_direction, distrib, img_size, save_path):
  distSize = {"100x100":(100,12), "150x150":(150,8), "200x200":(200,7), "300x300":(300,4), "600x600":(600,2.5)} 
  globScene = mss.genGlobalScene()
  #for i in range(1,mss.depth):
  #  globScene.add(mss.genScaleScene(i+1))

  az = light_direction[0]
  el = light_direction[1]
  dir = lit.azel2vect(az, el)


  if img_size in distSize.keys():
    width = distSize[img_size][0]
    height = distSize[img_size][0]
    distfactor=distSize[img_size][1]
  else:
    width=300
    height=300
    distfactor=4

  lit.prepareScene(globScene, width, height, az, el, distfactor)
  
  b=mss.loadBeams(az, el, save_path)
  if b != None:
    print "beams loaded..."
  else :
    print "computing beams..."
    b=pgl.Viewer.frameGL.castRays2(pgl.Viewer.getCurrentScene())
    mss.saveBeams(az, el,b, save_path)
  mss.beamsToNodes(dir, b)

  sproj=mss.loadSproj(az, el, save_path)
  if sproj != None:
    print "projected surface loaded..."
    mss.sprojToNodes(dir, sproj)
  else :
    print "computing projections..."
    sproj=mss.computeProjections( dir )
    mss.saveSproj(az, el, sproj, save_path)
 
  root_id = mss.get1Scale(1)[0]
  matrix = mss.probaImage(root_id, dir, distrib, width, height)
  pix = mss.makePict(az, el, distrib, matrix, width, height, save_path)
 
  return pix,
 
def light_direction(direct=True, lat=43.3643, long=3.5238, day=172, hstart=7, hstop=19, hstep=30, turtle=True, sun_shift=1, GMT_shift=0):
  sunlight = []
  if direct:
    sunlight += lit.sunDome.getDirectLight(lat, long, day, hstart, hstop, hstep, sun_shift, GMT_shift)

  if turtle:
    sunlight += lit.sunDome.skyTurtle()
  
  if not direct and not turtle:
    sunlight += (45.,45.,0.1)
  return sunlight



