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

"""


import Image
import os
import random
from scipy import array

import openalea.plantgl.all as pgl


def MSTfrom_file(filepath):
  """
  Read the file containing generation information as a dictionnary and build
  the MST accordingly
  """
  if( os.path.isfile( filepath ) ):
    f=open(filepath, 'r')
    dico = eval(f.read()) #this should be changed
    return MST(**dico)  

  else:
    raise IOError, "No such file"

class MST:
  """
  :Abstract: The *Multi scaled Thing* module generate a fractal object according to the rules given by a chosen *.mst* file
  """

  def __init__( self, dim, depth, **kwds ):
    self.dim = dim
    self.depth = depth
    self.root = Node(self.dim)

    if kwds.has_key( 'all_scale' ):
      scales = kwds[ 'all_scale' ]*self.depth
      self.scales = scales
    else:
      self.scales = kwds.get( 'scales', [(3,0.5)]*self.depth )
    #print "Dico : ", self.dico 
    self.generateComponents( src=self.root )

  def generateComponents( self, src ):
    """
    Generates subcomponents of src, i.e. the next scale
    """
    scale = src.getScale()
    div = self.scales[ scale ][ 0 ]
    pos = self.scales[ scale ][ 1 ]
    
    if isinstance( pos, float ):
      proba = pos
      pos = self.posFromProba( div, proba )
      
    components=[]
    for p in pos:
      n = Node( self.dim )
      n.setPos( p )
      n.setScale( scale + 1 )
      if n.getScale() < self.depth:
        self.generateComponents( n )
      components.append( n )
    src.setComponents( components, div )

  def posFromProba( self, div, proba ):
    """
    Generates random positioning according to subdivision factor and 
    proba which is equivalent in this case to normalized density
    """
    totalElmt = div**self.dim
    selectElmt = int( round( proba*totalElmt ) )
    l=[ 1 ]*selectElmt + [ 0 ]*( totalElmt - selectElmt )
    random.shuffle( l )
    indexList=[]
    for i in range( len( l ) ):
      if l[ i ]==1:
        indexList.append( i )
    posList=[]

    for idx in indexList:
      rest=idx
      pos=[]
      for j in range( 1, self.dim ):
        valeur = div**( self.dim-j ) 
        p = rest / valeur
        rest =  rest % valeur 
        pos.append(p)

      pos.append( rest )
      pos.reverse()
      posList.append( pos )
    return posList

  def absolutePos( self ):
    """
    Generate the list of absolute positions of the last scale components
    """
    pointList=[]
    size=0
    for elmt in self.root.components:
      sc1=elmt.absPos()
      pointList+=sc1[ 'list' ]
      if sc1[ 'unit' ] > size:
        size = sc1[ 'unit' ]
    size*=self.root.div
    return ( pointList, size )
  
  def toImage( self, filename='MST', pth = os.path.abspath(os.curdir) ):
    """
    Generate an image of the MST and save it under the filename in the pth 
    directory, also return the image (PIL)
    """
    if self.dim  < 3:
      data = self.absolutePos()
      ptList=data[ 0 ]
      size=( data[ 1 ], data[ 1 ] )
      img=Image.new( "L", size, color=255 )
      pix = img.load()
      for pt in ptList:
        pix[pt[0], pt[1]] = 0
        #img.putpixel( tuple( pt ), 0 )
      filepth= os.path.join(pth, filename+".bmp")
      img.save( filepth )
      return img
    else:
      print "wrong dimension"
      return None
  
#  def toImage2( self, filename='MST' ):
#    data = self.absolutePos()
#    ptList=data[ 0 ]
#    size=( data[ 1 ], data[ 1 ] )
#    img=Image.new( "L", size, color=255 )
#    draw=ImageDraw.Draw( img )
#    for pt in ptList:
#      draw.point( tuple( pt ), fill=0 )
#    filename=filename+".bmp"
#    img.save( filename )

  def toPglScene( self, geometry=None ):
    """
    Generate a PlantGL scene of the MST with the given geometry which size
    must be normalized ( < 1), default is a box
    """
    if self.dim < 4:
      scene = pgl.Scene()
      if geometry == None:
        geometry = pgl.Box(0.4)
      ( ptList, size ) = self.absolutePos()
      #x = y = z = 0
      for pt in ptList :
        try:
          x = pt[ 0 ]
        except IndexError:
          x = 0
        try:
          y = pt[ 1 ]
        except IndexError:
          y = 0
        try:
          z = pt[ 2 ]
        except IndexError:
          z = 0
        scene.add( pgl.Translated( (x, y, z), geometry ))
    else:
      print "Bad dimension"

    return scene

  def view( self ):
    """
    Visualize the MST using PlantGL viewer
    """
    pgl.Viewer.display( self.toPglScene() )


class Node:
  """
  :Abstract: This module define a multiscale space partitionning node based on regular subdivision
  """

  def __init__(self, dim=1):
    """
    Generate a node of the given dimension that is to be a representant of the given scale and will be subdivided along each of its dimension acording to the div parameter.
    """

    self.dim = dim
    self.scale = 0
    self.div = 1
    self.components = None
    self.position = None
    
  def setScale( self, s ):
    """
    Define the scale of the node
    """
    self.scale=s
    
  def getScale( self ):
    """
    Get the scale of the node
    """
    return self.scale
    
  def setComponents( self, component_list, div ):
    """
    Define the node components and the subdivision factor that goes along
    """
    self.components=component_list
    self.div=div
#    for elmt in self.components:
#      elmt.setScale( self.scale +1 )
      
  def getComponents( self ):
    """
    Get the components of a node
    """
    return self.components

  def setPos( self, pos ):
    """
    Define the relative position of the node regarding the subdivised space
    of its complex (== scale father)
    """
    if len( pos ) == self.dim :
      self.position=pos
    else :
      raise ValueError, "Node dimension and position vector dimension are not identical"

  def getPos ( self ):
    """
    Get the relative position of the node
    """
    return self.position

  def absPos( self ):
    """
    Generate the list of absolute positions of the last scale components
    of this node
    """
    if self.is_composed():
      list=[]
      for elmt in self.components:
        apos = elmt.absPos()
        unit = self.div*apos[ 'unit' ]
        mypos = unit * array( self.getPos() )
        for p in apos[ 'list' ]:
          point=mypos + array( p )
          list.append( point.tolist() )
      return {'list':list, 'unit':unit}
    else:
      return { 'list':[ self.getPos() ], 'unit':self.div }

  def is_composed( self ):
    """
    Return True if the Node has components
    """
    return self.components != None

  def getDensity( self ):
    """
    Return the ratio between occuped and total slots of a composed
    Node, 1 if the node has no components
    """
    if self.is_composed():
      compo_dens=0
      for elmt in self.components:
        compo_dens += elmt.getDensity()
      return 1.0*compo_dens/( self.div**self.dim )
    else:
      return 1
    
