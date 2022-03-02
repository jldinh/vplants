#! /usr/bin/env python
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

import cPickle
from scipy import zeros, ones, take, array
from scipy.signal import convolve
from os.path import join, isdir, isfile, basename 
from os import makedirs, getcwd

import openalea.fractalysis.fractutils.pgl_utils  as pgu
#import pgl_utils  as pgu

class MatrixLac:
  """
  This class allow to study various lacunarities of a n-dimensional square matrix. The values can be binary ( 1=presence / 0=abscence ) or a floating number representing a density or something... 
  
  """

  def __init__( self, name, points, size, vox_size, mass=None, spath = getcwd()):
    """
    The created matrix will be an n-dimensional array of the same size in any dimension.
    The size have to be specified whereas the dimension is embeded in the points list.
    
    :Parameters:
      - `name` : identifier used to generate result directory
      - `points` : list of n-dimensional vector 
      - `size` : grid size i.e. sudivision factor of initial bounding box
      - `mass` : (optional) `points`-shaped list of their associated weight

    :Types:
      - `name` : string
      - `points` : list
      - `size` : int
      - `mass` : array (default=None)

    """
    self.name = name
    self.points = points
    self.size = size
    self.vox_size = vox_size
    self.dim = len( self.points[ 0 ] )
    self.matrix= self._toMatrix(mass)
    self.save_path = spath

  def _toMatrix( self , mass):
    """
    Inner method : transform the points list into a valid n-dimensional matrix.
    If mass is ``None`` it will generate a binary matrix.

    :Parameters:
      - `mass` : the list of values to be used instead of usual presence/abscence ones. Its length must be identical to the instance ``points`` attribute (see `__init__`).

    :Types:
      - `mass` : list

    :returns: n-dimensional matrix generated from ``points``.
    :returntype: array

    """
    shape=[ self.size ]*self.dim

    if( mass==None ):
      m=zeros( shape, dtype=float )
      for pt in self.points:
        xyz = tuple(pt)
        m[xyz] = 1
    else :
      print "len mass : ", len( mass )
      print "len point : ", len( self.points )
      print "shape : ", shape
      m=zeros( shape, dtype=float  )
      for i in range( len( self.points ) ):
        xyz = tuple(self.points[i])
        m[xyz] = mass[i]
    return m
  
  def _get_convol( self, gb_radius, conv_mod = 'same'):
    """
    Inner method : convolve the matrix with a ones-matrix of given radius.
    The output size is determined by convolution mode.
    The output matrix is a representation of the mass distribution of a gliding-box f given radius, 
    if the convolution mode is set to 'valid' it is as if the gliding-box is bounded in within the matrix.
    
    :Parameters:
      - `gb_radius` : gliding-box radius, the size of the gliding-box is thus 2*`gb_radius`+1 so it's always odd.
      - `conv_mod` : convolution mode can take 3 values : 'valid', 'same' or 'full', see below for explanations.

    :Types:
      - `gb_radius` : int
      - `conv_mod` :  string in {'valid', 'same' or 'full'}

    :returns: The convolution matrix
    :returntype: array

    The diferents convolution modes :
      1. 'valid' : The output consists only of those elements that are computed by scaling the larger array with all the values of the smaller array.
      2. 'same' : The output is the same size as the largest input centered with respect to the 'full' output.
      3. 'full' : The output is the full discrete linear convolution of the inputs
    """

    gbSize = gb_radius*2 + 1

    save_path = join(join(self.save_path, self.name), 'size_'+str(self.size) )
    savefile = 'radius_' + str( gb_radius ) + '.convol'
    saveabs = join( save_path, savefile )
    
    if isfile( saveabs ):
      print "loading already computed convolution.."
      f = open(saveabs, 'r')
      radius, conv = cPickle.load(f)
      f.close()
    else:
      vect=[ gbSize ]*self.dim
      gb=ones( vect, dtype=float )
      conv=convolve(self.matrix, gb, mode=conv_mod )
      cs=conv.shape[ 0 ] 
      if cs > self.size: #in case of conv_mod = full need to be checked
        idx=( cs - self.size )/2
        for i in range( self.dim ):
          conv=take( conv, range( idx, cs-idx ), axis=i )
      if conv.shape != self.matrix.shape: # in case of conv_mod = valid should not be used
        print "matrix shape : ", self.matrix.shape
        print "convol shape : ", conv.shape
        #transform it to an original shaped matrix ?
  
      self._save_convol( gb_radius, conv )
    return conv

  def _save_convol( self, radius, convol_mat ):
    """
    Inner method : save the convolution matrix so it can be used again without computation.
    The file is saved in the result directory named after the name instance attribute (see `__init__`) as **radiusX.convol** where **X** is the ``radius`` value.

    :Parameters:
      - `radius` : radius of the convolution matrix i.e. the radius of the glinding box
      - `convol_mat` : the result convolution matrix tobe saved

    :Types:
      - `radius` : int
      - `convol_mat` : array

    :attention:
      If a convolution with same radius has already been saved it will **not** be overwriten.
    """
    save_path = join(join(self.save_path, self.name), 'size_'+str(self.size) )
    print "SaveDir = ", save_path

    if not isdir(save_path):
      makedirs(save_path)
    
    savefile = 'radius_' + str( radius ) + '.convol'
    print "saving ", savefile
    saveabs = join( save_path, savefile )
    
    if isfile( saveabs ):
      print "won't overwrite existing file"
    else:
      res = ( radius, convol_mat )
      f = open(saveabs, 'w')
      cPickle.dump(res, f, protocol=cPickle.HIGHEST_PROTOCOL)
      f.close()

  def _lacac( self, weight, gb_radius ):
    """
    Inner method : compute the **Allain and Cloitre lacunarity** from the ``weight`` matrix representing the mass distribution of the gliding boxes
    
    :Parameters:
      - `weight`: The gliding boxe mass distribution matrix
    
    :Types:
      - `weight`: A n-dimensional square matrix
    
    :returns: Triplet constitued of the number of gliding boxes, the first and the second moment of the gliding boxes mass distribution
    :returntype: ( int, float, float )

    """
    for i in range(self.dim):
      weight = weight.take( range(gb_radius, weight.shape[i]-gb_radius), axis = i)
    print "new shape : ", weight.shape
    nbBox=1.0
    for s in weight.shape:
      nbBox*=s
    print "nb box : ", nbBox

    Z1=weight/nbBox
    Z2=( weight*weight )/nbBox
    try :
      for i in range( self.dim ):
        Z1=sum( Z1 )
        Z2=sum( Z2 )
      return ( nbBox, Z1, Z2 )
    except TypeError:
      print "Error in Z1 and/or Z2 : ",Z1, Z2
      return (None, None, None)

   
  def _lacac_ext( self, weight, gb_radius ):
    """
    Inner method : compute the **Allain and Cloitre lacunarity** from the ``weight`` matrix representing the mass distribution of the gliding boxes
    
    :Parameters:
      - `weight`: The gliding boxe mass distribution matrix
    
    :Types:
      - `weight`: A n-dimensional square matrix
    
    :returns: Triplet constitued of the number of gliding boxes, the first and the second moment of the gliding boxes mass distribution
    :returntype: ( int, float, float )

    """
    nbBox=1.0
    for s in weight.shape:
      nbBox*=s

    Z1=weight/nbBox
    Z2=( weight*weight )/nbBox
    try:
      for i in range( self.dim ):
        Z1=sum( Z1 )
        Z2=sum( Z2 )
      return ( nbBox, Z1, Z2 )

    except TypeError:
      print "Error in Z1 and/or Z2 : ",Z1, Z2
      return (None, None, None)


  def _ctrdlac( self, weight, gb_radius ):
    """
    Inner method : compute the **Centered lacunarity** from the ``weight`` matrix representing the mass distribution of the gliding boxes
    
    :Parameters:
      - `weight`: The gliding boxe mass distribution matrix
    
    :Types:
      - `weight`: A n-dimensional square matrix
    
    :returns: 
      a triplet constitued with the number of gliding boxes, the first and the second moment of the gliding boxes mass distribution
    :returntype: ( int, float, float )
    
    """

    if weight.shape != self.matrix.shape:
      #modify the values of points to change origin position, should work for both bigger and smaller weight matrix
      diff = array([self.matrix.shape[i] - weight.shape[i] for i in range(len(weight.shape))])
      curPoints = [ array(pt) - diff for pt in self.points ] 
    else :
      curPoints = self.points

    nbBox = 0
    Z1=0
    Z2=0
    for pt in curPoints:
      try :
        xyz =  tuple(pt) 
        v=weight[xyz]
        Z1+=v
        Z2+=( v**2 )
        nbBox += 1
      except IndexError :
        pass

    Z1/=nbBox
    Z2/=nbBox
    return ( nbBox, Z1, Z2 )
    
  def one_scale_Lac( self, scale_radius , lac_type = None):
    """
    The given scale_radius define the gliding box size in that way 
    gliding box size = scale_radius*2+1 so it is always odd
    """
    if lac_type == None:
      lac_type = self._ctrdlac

    gbSize = scale_radius*2+1
    wght=self._get_convol( scale_radius )
    
    ( nbBox, Z1, Z2 ) = lac_type( wght, scale_radius )
    if nbBox != None :
      lac=Z2/( Z1**2 )
      return ( lac, self.vox_size*gbSize )
    else:
      return (None, None)
   
  def lacunarity( self, radius_stop, radius_start=1, radius_step=1, lac_type=None ):
    lac = []
    boxSize = []
    for sc in range( radius_start, radius_stop+1, radius_step ):
      ( l, s ) = self.one_scale_Lac( sc, lac_type )
      
      if l != None and s != None :
        lac.append( l )
        boxSize.append( s )
      
    return ( lac, boxSize )
 
############################ MatrixLac factory ########################################

def lactrix_fromScene( scene, file_name, gridSize, density=True, spath = getcwd()):
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
  #uncomment the line below to get the view phase
  #pgu.viewScene( scene )
  #tgl_list=pgu.surfPerTriangle( scene ) #a inclure dans scene2grid
  ( pts, m, s ) = pgu.scene2grid( scene, gridSize )
  if ( not density ):
    print "Density not taken into account..."
    mat=MatrixLac( name=file_name, points=pts, size=gridSize, vox_size = s, mass=None, spath = spath )
    #comment the 2 lines below to skip the view phase
    #print "generating visual representation..."
    #pgu.viewScene( pgu.toPglScene( mat.points) )
  else:
    print "Considering Density..."
    mat=MatrixLac( name=file_name, points=pts, size=gridSize, vox_size = s, mass=m, spath = spath )
    #comment the 2 lines below to skip the view phase
    #print "generating visual representation..."
    #pgu.viewScene( pgu.toPglScene( mat.points, m ) )
  return mat 


def lactrix_fromPix(image_pth, pix_width, savpth, th=245):
  """
  Generate a `MatrixLac` instance from a square image.

  :Parameters:
    - `image_pth` : absolute path to the PNG image (temporary restriction)
    - `pix_width` : pixel representing size defining the grid step
    - `savpth` : path to directory to save convolution results
    - `th` : threshold value to decide object pixels from void pixels

  :Types:
    - `image_pth` : string
    - `pix_width` : float
    - `savpth` : string
    - `th` : int
  
  :returns: `MatrixLac` instance generated from the image
  :returntype: `MatrixLac`

  """

  pts = []
  name = basename(image_pth).replace('.png', '')
  mat_size = 0
  try :
    import Image
    im = Image.open(image_pth).convert("L")
    pix = im.load()
    width, height = im.size
    assert width == height, "Image must be square"
    mat_size = width
    #finding points by inverting picture and removing grey levels
    for i in range(width):
      for j in range(height):
        if pix[i,j] > th:
          pix[i,j] = 0
        else :
          pts.append([i,j])
          pix[i,j] = 255
  except ImportError:
    print "Image module not found, MatrixLac generation from image unavailable"

  mat = MatrixLac(name=name, points=pts, size=mat_size, vox_size=pix_width, mass=None, spath=savpth) 
  return mat


