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
"""
:Authors:
  - Da SILVA David
:Organization: Virtual Plants
:Contact: david.da_silva:cirad.fr
:Version: 1.0
:Date: December 2005
:requires:
  - pylab

Module for computing n-dimensional lacunarity using n-dimensional matrix. The non-zero values of the matrix representing either the presence (binary 0/1 matrix) or a quantity/density.

"""

__docformat__ = "restructuredtext en"



__doc__="""
fractalysis.engine nodes
"""

__license__= "Cecill-C"
__revision__=" $Id: engine_nodes.py 7873 2010-02-08 18:17:47Z cokelaer $ "

from copy import deepcopy
from scipy import log, array
from os.path import basename, splitext
from openalea.core import *
import openalea.plantgl.all as pgl
#import openalea.fractalysis.engine as engine
from openalea.fractalysis.engine import computeGrids
from openalea.fractalysis.engine.lac_engine import MatrixLac
from openalea.fractalysis.fractutils.pgl_utils import surfPerTriangle, gridIndex, color, scene2grid, toPglScene
from openalea.fractalysis.engine.MSTgenerator import MST
from openalea.fractalysis.engine.twosurfaces import TwoSurfaces

def genMST(dim, depth, scale_gen, allScale=False):
  if allScale:
    return MST(dim=dim, depth=depth, all_scale=scale_gen)
  else:
    return MST(dim=dim, depth=depth, scales=scale_gen)

def MSTfromDict(dico):
  return MST(**dico)

def MST2Pix(mst, pixname, savepth):
  return mst.toImage(filename=pixname, pth=savepth)

def MST2PglScene(mst, geometry=None):
  return mst.toPglScene(geometry=geometry)

class BCM( Node ):
  """
  Box Method a.k.a counting intercepted voxel at each scale

  :Parameters:
    - `Scene` : PlantGL scene
    - `Stop Factor` : final subdivision factor > 2

  :Types:
    - `Scene` : Pgl scene
    - `Stop Factor` : int

  :returns:
    - `Scales` : array of voxels size
    - `Intercepted Voxels` : array of number of intercepted voxels

  :returntype: 
    - `Scale` : [ float ]
    - `Intercepted Voxels` : [ int ]
  """

  def __init__( self, inputs, outputs ):

    Node.__init__( self, inputs, outputs )

  def __call__( self, inputs ):
        #scene = pgl.Scene(self.get_input( 'scene' ))
        scene = self.get_input( 'Scene' ) 
        res = computeGrids( scene , self.get_input( 'Stop Factor' ) )
        
        sc=[]
        iv = []
        for r in res:
            sc.append( r[ 1 ] )
            iv.append( r[ 0 ] )
        #scales =  log( 1./ array( sc ) )
        #interVox = log( array( iv ) )
        scales =   1./ array( sc ) 
        interVox =  array( iv ) 
        return ( scales, interVox )

class Voxels(object):

    def __init__(self, size, centers, density=None):

        self.size = size
        self.centers = centers
        self.density = density

    def __repr__(self):
        
        return "Voxels size : " + str(self.size) + "\n Voxels centers : " + str(self.centers) + "\n Voxels density : " + str(self.density)


def voxelize(scene, gridSize, density=True ):
  """
  Generate the scene resulting of grid discretization
  
  :Parameters:
    - `Scene` : PlantGL scene
    - `Division Factor` : Division factor of the bounding box
    - `Density` : Taking density into account

  :Types:
    - `Scene` : Pgl scene
    - `Division Factor` : int 
    - `Density` : boolean

  :returns:
    - `Voxel size` : List of intercepted voxels size
    - `Centers` : List of intercepted voxels centers
    - `Densities` : List of intercepted voxels densities
    - `VoxScene` : Scene of intercepted voxels

  :returntype:
    - `Voxel size` : [ float ] 
    - `Centers` : [ ( float ) ]
    - `Densities` :  [ float ]
    - `VoxScene` : Plg scene
  """

  #scene = pgl.Scene(sceneFile)
  bbox = pgl.BoundingBox(scene)
  epsilon = pgl.Vector3( 0.01, 0.01, 0.01 )
  origin = bbox.lowerLeftCorner - epsilon
  step = ( bbox.getSize() + epsilon )*2 / ( gridSize )
  origin_center = origin + step/2.
  
  tgl_list = surfPerTriangle( scene )

  grid = {}
  for tgl in tgl_list:
    pos = gridIndex( tgl[ 0 ] - origin, step )
    assert( pos[ 0 ] < gridSize and pos[ 1 ] < gridSize and pos[ 2 ] < gridSize )

    if grid.has_key(  pos  ):
      grid[  pos  ] += tgl[ 1 ]
    else:
      grid[  pos  ] = tgl[ 1 ]

  kize = grid.keys()
  kize.sort()
  pts=[]
  mass=[]
  for k in kize:
    pts.append(  list( k )  )
    mass.append( grid[ k ] )
    
  massort = deepcopy( mass )
  massort.sort()
  qlist=[25, 50, 75]
  quants = [massort[int(len(massort)*q/100.0)] for q in qlist]
  
  voxSize = step/2.
  vox = pgl.Box( voxSize )
  vox.setName( 'voxel' )
  
  mat1 = color( 47,255,0, trans=True , name='c_green')
  mat2 = color( 255,255,0, trans=True , name='c_yellow')
  mat3 = color( 255,170,0, trans=True , name='c_orange')
  mat4 = color( 255,0,0, trans=True , name='c_red')

  #sc = pgl.Scene()
  ctrs = []
  for i in xrange( len( pts ) ):
    pt = pts[ i ]
    vect = pgl.Vector3( origin_center.x + ( pt[ 0 ] * step.x ) , origin_center.y + ( pt[ 1 ] * step.y ) ,origin_center.z + ( pt[ 2 ] * step.z ) )
    ctrs.append(vect)
    geometry = pgl.Translated( vect, vox )
    if( density ):
      if ( mass[ i ] < quants[ 0 ] ) :
        sh = pgl.Shape( geometry, mat1, i )
      elif ( mass[ i ] < quants[ 1 ] ) :
        sh = pgl.Shape( geometry, mat2, i )
      elif ( mass[ i ] < quants[ 2 ] ) :
        sh = pgl.Shape( geometry, mat3, i )
      else :
        sh = pgl.Shape( geometry, mat4, i )
    else:
      sh = pgl.Shape( geometry, mat1, i )
    scene.add( sh )
  
  vxls = Voxels( voxSize, ctrs, mass ) 

  #return (vxls, scene)
  return ( voxSize, ctrs, mass, scene ) 


def lactrix_fromScene( scene, file_name, gridSize, spath, density):
  """
  Generate a `MatrixLac` instance from a PlantGL scene.

  :Parameters:
    - `file` : name of geom/bgeom scene file, without extension
    - `gridSize` : subdivision factor of the bonuding box defining the grid step
    - `density` : when True each non-empty voxel is associated with a proper value (e.g. leaf area density inside each voxel)

  :Types:
    - `file` : string
    - `gridSize` : int
    - `density` : boolean
  
  :returns: `MatrixLac` instance generated from the scene
  :returntype: `MatrixLac`

  """
  ( pts, m, s ) = scene2grid( scene, gridSize )
  if ( not density ):
    print "Density not taken into account..."
    mat=MatrixLac( name=file_name, points=pts, size=gridSize, vox_size = s, mass=None, spath = spath )
    visu = toPglScene( mat.points) 
  else:
    print "Considering Density..."
    mat=MatrixLac( name=file_name, points=pts, size=gridSize, vox_size = s, mass=m, spath = spath )
    visu = toPglScene( mat.points, m ) 
  return mat, visu 

try :
  import Image

  def lactrix_fromPix(image_pth, pix_width, savpth, pixname, th=245):
    """
    Generate a `MatrixLac` instance from a square image.

    :Parameters:
      - `image_pth` : absolute path to the PNG image or PIL image (temporary restriction)
      - `pix_width` : pixel representing size defining the grid step
      - `savpth` : path to directory to save convolution results
      - `pixname` : name of directory to be used to save convolution results
      - `th` : threshold value to decide object pixels from void pixels

    :Types:
      - `image_pth` : string
      - `pix_width` : float
      - `savpth` : string
      - `pixname` : string
      - `th` : int
    
    :returns: `MatrixLac` instance generated from the image
    :returntype: `MatrixLac`

    """

    pts = []
    if isinstance(image_pth, str):
      name = basename(splitext(image_pth)[0])
      im = Image.open(image_pth).convert("L")
    else:
      im = image_pth
      name = pixname

    pix = im.load()
    width, height = im.size
    #finding points by inverting picture and removing grey levels
    for i in xrange(width):
      for j in xrange(height):
        if pix[i,j] > th:
          pix[i,j] = 0
        else :
          pts.append([i,j])
          pix[i,j] = 255

    mat = MatrixLac(name=name, points=pts, size=width, vox_size=pix_width, mass=None, spath=savpth) 
    return mat, im

except ImportError:
  print "Image module not found, MatrixLac generation from image unavailable"

class lacunarity( Node ):
  """
  Compute the lacunarity of a n-dimensional matrix
   
  :Parameters:
    - `Matrix` : matrix for lacunarity computation
    - `Type` : type of lacunarity
    - `Start` : starting subdivision factor
    - `Stop` : ending subdivision factor

  :Types:
     - `Matrix`: `MatrixLac`
     - `Type` : string
     - `Start` : int
     - `Stop` : int
     
  :returns:
    - `Lacunarity` : List of lacunarity values as a function of subvoxel sizes
    - `Box sizes` : List of subvoxel sizes

  :returntype:
    - `Lacunarity` : [ float ] 
    - `Box sizes` :  [ float ]
  """

  lac_func =  { "Centered" : "_ctrdlac",
                "A & C extended" : "_lacac_ext",
                "Allain & Cloitre" : "_lacac",
              }

  def __init__(self):

    Node.__init__(self)
    funs = self.lac_func.keys()
    funs.sort()
    self.add_input( name = "Matrix", interface=None,)
    self.add_input( name = "Type", interface = IEnumStr(funs), value=funs[-1])
    self.add_input( name = "Start", interface = IInt(min = 0) )
    self.add_input( name = "Stop", interface = IInt(min = 0) )
    self.add_output( name = "Lacunarity", interface = ISequence)
    self.add_output( name = "Box sizes", interface = ISequence)

  def __call__(self, inputs):
    func_name = self.get_input("Type")
    f = self.lac_func[func_name]
    self.set_caption(func_name)
    mat = self.get_input("Matrix")
    lac, boxes = mat.lacunarity(  radius_start = self.get_input("Start"),
                                  radius_stop = self.get_input("Stop"),
                                  lac_type = getattr(mat,f),
                                )
    #if isinstance(boxes[0], pgl.Vector3):
    #  box_size = [(b[0]*b[1]*b[2])**(1/3.) for b in boxes]
    #else :

    return lac, boxes
