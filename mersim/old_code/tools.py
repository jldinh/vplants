#!/usr/bin/env python
"""tools.py

Here different code tools should be gathered. In the future it should be split depanding on the function.

:version: 2006-11-07
:author:  szymon stoma
"""
import math


def permutation_lazy( str ):
    """Returns generator of permutations of the list str.
    """
    if len(str) <=1:
        yield str
    else:
        for perm in WalledTissue._all_perms( str[1:] ):
            for i in range(len(perm)+1):
                yield perm[:i] + str[0:1] + perm[i:]

def upe( p1, p2 ):
    """Unordered pair equal(upe) Returns true if 
    p1 = (s1, t1) and p2 = (s2, t2) and ( ( s1 = s2 and t1 = t2) or ( s1 = t2 and t1 = s2) ).
    """
    s1, t1 = p1
    s2, t2 = p2
    return ( s1 == s2 and t1 == t2) or ( s1 == t2 and t1 == s2)

def get_ordered_vertices( edge_list ):
    """By example: Gets the list of ordered edges written with **unordered** pair list and
    returns same edge list but with **ordered** pairs.
    input: [(1,2). (2,3), (3,4), (5,4), (6,5), (1,6)]
    output:[(1,2). (2,3), (3,4), (4,5), (5,6), (6,1)]
    """
    begin, end = edge_list[ 0 ]
    res = [ begin, end ]
    el = edge_list[1:]
    while len(el) != 0:
        for e in el:
            b = False
            for z in [0, 1]:
                if e[ z ] == begin:
                    res = [ e[ (z + 1) % 2 ] ] + res
                    begin = e[ (z + 1) % 2 ]
                    el.remove( e )
                    b = True
                    break
                if e[ z ] == end:
                    res = res + [ e[ (z + 1) % 2 ] ]
                    end = e[ (z + 1) % 2 ]
                    el.remove( e )
                    b = True
                    break
            if b: break
    return res


def find_edge_order( s1, t1, shape):
    """Returns the order of s1 and t1 based on the one in the list the list. If the pair 
    can not be found returns None.

    :Exception KeyError: If the edge is not found in shape.
    """
    ls = len( shape )
    for i in range( ls ):
        if shape[ i%ls ] == s1 and shape[ (i+1)%ls ] == t1:
            return s1, t1
        if shape[ i%ls ] == t1 and shape[ (i+1)%ls ] == s1:
            return t1, s1
    # like exception..
    KeyError("Edge not found in find_edge_order")

def find_edges_order( s1, t1, p1, s2, t2, p2, shape):
    """Returns the order of precedence of  s1, t1 and s2, t2 in the list.
    
    :Exception KeyError: If *both* pairs don't exist. It might be confusing with the situation
    when only one edge exists.
    """
    ls = len( shape )
    for i in range( ls ):
        if shape[ i%ls ] == s1 and shape[ (i+1)%ls ] == t1:
            return s1, t1, p1, s2, t2, p2
        if shape[ i%ls ] == s2 and shape[ (i+1)%ls ] == t2:
            return s2, t2, p2, s1, t1, p1
    raise KeyError("Vertices not found in find_edges_order")

def nearest_point( X, Y, (x,y) ):
    """Returns index of point which is nearest to (x,y). Checked points are: (X[i],Y[i]) 
    """
    minp=float("infinity")
    min_ind = 0
    for i in range(len( X ) ):
        z = math.sqrt( (X[i]-x)**2 + (Y[i]-y)**2 )
        if z < minp:
            minp=z
            min_ind=i
            
    #print minp, (X[min_ind],Y[min_ind]), (x,y)
    #raw_input()
    return min_ind


def create_grid_from_discret_values( X,Y,Z, sizeX=100, sizeY=100 ):
    """Creates a rectangular grid from a list of given values (x,y,z). A grid is rectangular
    and has the  coordinates (min(x),min(y)) -> (max(x),max(y)). The distance between
    nodes is equal and depands on the sizeX/Y parameter.
    
    TODO: not optimal. Slow.
    """
    
    from numpy import *
    xmin=min(X)
    xmax=max(X)
    ymin=min(Y)
    ymax=max(Y)
    xrange=xmax-xmin
    yrange=ymax-ymin
    
    #Zt = zeros(len(X))
    grid = zeros((sizeX,sizeY))
    
    for i in range(sizeX):
        for j in range(sizeY):
            grid[i][j] = Z[ nearest_point(X,Y, (xmin+i*xrange/sizeX,ymin+j*yrange/sizeY)) ]
    
    return (arange(xmin,xmax,xrange/sizeX),arange(ymin,ymax,yrange/sizeY),grid)

def plot_3d_height_map1( V ):
    X,Y,Z = [],[],[]
    for i in V:
        X.append(i.x)
        Y.append(i.y)
        Z.append(i.z)
    plot_3d_height_map( X, Y, Z )

def plot_3d_height_map_using_vtk( X,Y,Z ):
    from pylab import *
    from vtk_pylab import *
    X,Y=meshgrid(X,Y)
    mesh(X,Y,Z,1)
    vtkRender()
    vtkImage()
    imshow(im,None)
    show()

def plot_3d_height_map( X, Y, Z ):
    from numpy import *
    import pylab as p
    import matplotlib.axes3d as p3

    # in mplt3D change: 
    # levels, colls = self.contourf(X, Y, Z, 20)
    # to:
    # C = self.contourf(X, Y, Z, *args, **kwargs)
    # levels, colls = (C.levels, C.collections)
    
    fig=p.figure()
    ax = p3.Axes3D(fig)
    ax.contour(X,Y,Z)
    #ax.plot3D(X,Y,Z)
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    #fig.add_axes(ax)
    p.show()
    
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
