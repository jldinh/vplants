#!/usr/bin/env python
"""filename.py

Desc.

:version: 2006-05-15 15:21:06CEST
:author:  szymon stoma
"""


from springTissueModel import *
from const import *
import PlantGL as pgl
import merrysim as m
import visual

const = PlantGLTissueTest()
s = TissueSystem( const = const  )
s.tissue._create_TissueTopologyFromSimulation()

## loading slices
#slices = m.graph.Slices(s.const.projection_path, 'red')
#z_mul = 6.1
#ratio = 3./4
#for vw in s.tissue.wvs():
#    v1 = s.tissue.wv_pos( vw )
#    print v1
#    z = slices.get_z(v1.x, -v1.y, z_mul, ratio)
#    v1 = visual.vector(v1.x, v1.y, z )
#    s.tissue.wv_pos( vw, v1 )
## end of loading slices
#s.tissue._get_z_coords()


def interpolate_color( color1=None, color2=None, range=None, value=None):
    """Returns the interpolated RGB value between color1 and color2.
    assumptions:
    * color?= (r,g, b)
    * range = (x1, x2)
    * x1 < x2
    * value is in range
    """
    try:
        r,b,g = color1
        r2,b2,g2 = color2
        s0, s1 = range
        p = (value-s0) / (s1-s0) 
        dr = float( r2 - r )
        dg = float( g2 - g )
        db = float( b2 - b )
        c = (r+p*dr, b+p*db , g+p*dg)
    except ZeroDivisionError:
        return color1
    return c 
        


def tv2p( v ):
    return pgl.Vector3( v.x, v.y, v.z )


green = pgl.Material( name="green", ambient=pgl.Color3(0,210,0) )
green2 = pgl.Material( name="green2", ambient=pgl.Color3(0,240,0) )
green3 = pgl.Material( name="green3", ambient=pgl.Color3(0,160,0) )
red = pgl.Material( name="red", ambient=pgl.Color3(210,0,0) )

pgl.Viewer.frameGL.setBgColor( pgl.Color3(0,0,0 ) )
scene = pgl.Scene()
# could be shared..
wv = pgl.Sphere( radius=1 )
wv.name = "wall vertex"
for i in s.tissue.wvs():
    v1p = s.tissue.wv_pos( i )
    trans_wall = pgl.Translated( pgl.Vector3( v1p.x, v1p.y, v1p.z ),  wv)
    shape = pgl.Shape( trans_wall, green )
    scene.add( shape )

wall = pgl.Cylinder( radius=0.3 )
wall.name = "wall"
for i in s.tissue.wv_edges():
    (v1,v2) = i
    v1p = s.tissue.wv_pos( v1 )
    v2p = s.tissue.wv_pos( v2 )
    vaxis = v2p-v1p
    axis = pgl.Vector3( vaxis.x, vaxis.y, vaxis.z )
    # test the parallel of OZ and axis!
    scale_rot = pgl.Scaled( pgl.Vector3( 1,1,mag(vaxis) ), wall )
    axis_rot = pgl.AxisRotated( -pgl.cross( axis, pgl.Vector3.OZ ), pgl.angle( axis, pgl.Vector3.OZ ), scale_rot )
    trans_wall = pgl.Translated( pgl.Vector3( v1p.x, v1p.y, v1p.z ), axis_rot )
    shape = pgl.Shape( trans_wall, green2 )
    scene.add( shape )

cell=pgl.Sphere( radius=1 )
cell.name = "cell"
z = []
for i in s.tissue.cells():
    l = []
    cs = s.tissue.cell2wvs( i )
    v = s.tissue.cell_center( i )
    l.append( tv2p( v ) ) 
    z.append( tv2p(v).z )
    for j in cs: 
        l.append( tv2p( s.tissue.wv_pos( j ) ))
    il = [ pgl.Index3(0,j,j+1) for j in range( 1,len( cs ) ) ]+[pgl.Index3(0,len( cs ),1)]
    cellts = pgl.TriangleSet( )
    #cellts.ccw=False
    cellts.pointList = pgl.Point3Array(l)
    cellts.indexList = pgl.Index3Array(il )
    col = interpolate_color((0,255,0), (255,0,0), [-150,0], v.z )
    mat = pgl.Material(  ambient=pgl.Color3(int(col[0]), int(col[1]),int(col[2])) )
    scene += pgl.Shape(  cellts,mat )
    trans_cell = pgl.Translated( tv2p( v ), cell )
    scene += pgl.Shape( trans_cell, red )
max(z)
min(z)    
        
    
pgl.Viewer.display( scene )
