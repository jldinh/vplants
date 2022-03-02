#!/usr/bin/env python

"""Class containing the WalledTissue typical algorithms.

This class was designed to keep together the WalledTissue typical algorithms. 

:todo:
    Nothing.

:bug:
    None known.
    
:organization:
    INRIA

"""

# Module documentation variables:
__authors__="""Szymon Stoma    
"""
__contact__=""
__license__="Cecill-C"
__date__="pia mar 30 14:50:15 CEST 2007"
__version__="0.1"
__docformat__= "restructuredtext en"
__revision__="$Id: walled_tissue.py 7875 2010-02-08 18:24:36Z cokelaer $"

import visual
##BEGIN DOC REMOVE
import networkx as nx
import pylab as pl
##END DOC REMOVE

import math
import pqueue
import sets
import copy

#from openalea.mersim.tissue.walled_tissue_topology import TissueTopology
import openalea.mersim.tools.misc as tools
import openalea.plantgl.all as pgl
import walled_tissue_topology

def create( wt, wv2pos = {}, cell2wv_list = {} ):
    """Creates the WalledTissue structure from data.
        
        :param wv2pos: contains the mapping of ids of wallvertices to their position.
        :param cell2wv_list: contains the mapping of cell ids to ORDERED (in the sens of walls) wv ids.
        :type wv2pos: hash( wv -> pos )
        :type cell2wv_list: hash( cell -> wv_list )
    """
    wt.clear_all()
    walled_tissue_topology.create( wt, cell2wv_list=cell2wv_list)
    
    for i in wv2pos.keys():
        #wt.add_wv( wv=i, pos=visual.vector( wv2pos[ i ].x, wv2pos[ i ].y, wv2pos[ i ].z ) )
        #TODO thing if conversion is necessary
        wt.add_wv( wv=i, pos=pgl.Vector3( wv2pos[ i ].x, wv2pos[ i ].y, wv2pos[ i ].z ), call_inherited=False )
    
def create_tissue_topology_from_simulation( wt, get_z_coords=True, clear_all=True ):
    import merrysim as m
    if clear_all: wt.clear_all()
    #TODO to be dropped
    # to load the data from supported format
    #!TODO ugly but currently are more important things to do
    _simulation = m.Simulation( wt.const.meristem_data , 10, 0.1 )
    
    # loading the walls with coords
    wg = _simulation.get_tissue().wall_graph()
    ei = wg.edges()
    try:
        while (1):
            e = ei.next()
            v1Id = wg.source( e )
            v2Id = wg.target( e )
            v1 = wg.vertex_position( v1Id )
            v2 = wg.vertex_position( v2Id )
            #pgl wt.add_wv( v1Id, pgl.Vector3( v1.x, v1.y, v1.z ) )
            #pgl wt.add_wv( v2Id, pgl.Vector3( v2.x, v2.y, v2.z ) )
            #wt.add_wv( v1Id, visual.vector( v1.x, v1.y, v1.z ) )
            #wt.add_wv( v2Id, visual.vector( v2.x, v2.y, v2.z ) )
            wt.add_wv( v1Id, pgl.Vector3( v1.x, v1.y, v1.z ) )
            wt.add_wv( v2Id, pgl.Vector3( v2.x, v2.y, v2.z ) )
            wt.add_wv_edge( v1Id, v2Id )
    except StopIteration:
        pass
    
    # loading the cells
    wg = _simulation.get_tissue()
    ei = wg.edges()
    h = {}
    ei = wg.edges()
    try:
        while (1):
            e = ei.next()
            v1Id = wg.source( e )
            v2Id = wg.target( e )
            wt.add_cell( v1Id )
            wt.add_cell( v2Id )
            wt.add_cell_edge( v1Id, v2Id )
    except StopIteration:
        pass
    

    # loading the cell2wv
    wg = _simulation.get_tissue()
    ci = wg.vertices()
    try:
        while (1):
            c = ci.next()
            wv = wg.cell_association( c )
            try:
                while (1):
                    w = wv.next()
                    wt.cell2wvs( c, wt.cell2wvs( c ).append( w ) ) 
            except Exception:
                pass
    except StopIteration:
        pass
    
    # creating the wv2cell
    for c in wt.cells():
        for w in wt.cell2wvs( c ):
            if c not in wt.wv2cells( w ):
                wt.wv2cells( w, wt.wv2cells( w ).append( c ) )

    try:
        if get_z_coords:
            _get_z_coords( wt )
        pass
    except Exception:
        print "Loading of Z coords skipped"
        
    #for vw in wt.wvs():
    #    wt.wv_pos( vw, wt.wv_pos( vw )*wt.const.meristem_load_scale )
    ##finding inside
    walled_tissue_topology.initial_find_the_inside_of_tissue( wt )

def show_cells( wt, with_labels = False ):
    """Plot cells projection on XY plane (does not draw walls).
    """
    nx.draw_networkx( wt._cells, _pos2tuple_pos_revxy( cell_centers( wt ) ), with_labels=with_labels, style='dotted', node_size= wt.const.cell_node_size )
    nx.draw_networkx_edges( wt._wvs, _pos2tuple_pos_revxy( wt._wv2pos ), edge_color='r' )
    pl.show()

def show_cells_with_wvs( wt, with_labels = False ):
    """Plot cells projection on XY plane (draws walls).
    """
    nx.draw_networkx( wt._cells, _pos2tuple_pos_revxy( cell_centers( wt ) ), with_labels=with_labels, style='dotted', node_size= wt.const.cell_node_size )
    nx.draw_networkx( wt._wvs, _pos2tuple_pos_revxy( wt._wv2pos ), edge_color='r', with_labels=with_labels,node_size= wt.const.wv_node_size )
    pl.show()

def cell_center( wt, cell = None ):
    """Return baricenter of cell.
    """
    center = pgl.Vector3() 
    #center = visual.vector() 
    l = wt.cell2wvs( cell )
    for w in l:
        center += wt.wv_pos( w )
    # calculate the baricenter
    #
    return center/ len( l )

def cell_centers( wt):
    """Returns the vertex3 hash of cell 2 baricenter of the cell.
    """
    cc = {}
    for c in wt._cells.nodes():
        cc[ c ] = cell_center( wt, c ) 
    return cc

def _pos2tuple_pos( cell2baricenter ):
    """Returns the hash cell 2 tuple x, y where the x, y are
    coordinats of the baricenter.
    """
    t = {}
    for c in cell2baricenter:
        t[ c ] = (cell2baricenter[ c ].x, cell2baricenter[ c ].y)
    return t

def _pos2tuple_pos_revxy( cell2baricenter ):
    """Returns the hash cell 2 tuple x, y where the x, y are
    coordinats of the baricenter.
    """
    from openalea.plantgl.all import Matrix3, Vector3
    import math
    m = Matrix3().axisRotation((0,0,1),math.pi)
    t = {}
    for c in cell2baricenter:
        t[ c ] = m*cell2baricenter[ c ]
        t[ c ] = (-t[ c ].y, -t[ c ].x)
    return t

#def get_cell_normal( wt, cell = None ):
#    """Gets the normal for the cell by collecting the normals from all vertices.
#    Note: obsolate. It uses pressure_center to find normals. Currently the WalledTissue is
#    in L/R mode and this information should be used to get the normals.
#    """
#    t = []
#    pressure_center=wt.const.simple_pressure_center
#    av_normal = visual.vector()
#    for w in wt.cell2wvs( cell = cell):
#        lm = wt._wvs.neighbors( w )
#        if len( lm ) >= 3:
#            normal = visual.cross( wt.wv_pos( wv=lm[1] ) - wt.wv_pos( lm[ 0 ] ), wt.wv_pos( lm[2] ) - wt.wv_pos( lm[ 1 ] ) )
#            if visual.mag( (wt.wv_pos( w ) +normal)  - pressure_center ) > visual.mag( (wt.wv_pos( w ) - normal) -  pressure_center ):
#                av_normal += visual.norm( normal ) 
#            else:
#                av_normal += visual.norm( -normal ) 
#    return visual.norm( av_normal )

def tissue_center( wt ):
    return wt.tissue_center_

def calculate_average_cell_surface( wt ):
    """Calculates the avarage cell surface for all cells in the tissue. Importatnt thing: check for degenerated cells
    before.
    """
    s = 0
    for c in wt.cells():
        s += calculate_cell_surface( wt, cell = c )
    return s/len( wt.cells() )

def center_group( wt ):
    """Returns a group of cells which surrounds initial cell (a cell with IC==True)
    """
    for c in wt.cells():
        if wt.cell_property( cell=c, property="IC"):
            return [ c ]+wt.cell_neighbors( c )

def _get_z_coords( wt, **keys):
    """Docs in Pierrs' code
    TODO: too much is hardcoded right now.
    """
    import merrysim as m
    if wt.const.reconstruct_3d_from_slices: 
        slices = m.graph.Slices(wt.const.projection_path, 'red')
    z_mul = 6.1
    ratio = 3./4
    for vw in wt.wvs():
        v1 = wt.wv_pos( vw )
        if wt.const.reconstruct_3d_from_slices: 
            z = slices.get_z(v1.x, -v1.y, z_mul, ratio)
        else:
            z = 0
        v1 = pgl.Vector3(v1.x, v1.y, z )
        #v1 = visual.vector(v1.x, v1.y, z )
        wt.wv_pos( vw, v1 )

def investigate_cell( wt, cell ):
    """Gives some data about cell internal representation. Mainly for debugging.
    """
    r = walled_tissue_topology.investigate_cell( wt, cell )
    if r:
        t = wt._cell2properties[ cell ]
        for i in t:
            print "  @",  i, ":", t[ i ]
        #print "  @", "aux_conc",":", wt.cell_property(cell, "auxin_level")/wt.calculate_cell_surface( cell )
        return True
    else:
        return False
    
def nbr_border_cells( wt, refresh=False ):
    """
    Note: working correctly only if cells are beeing fixed. The method fix_cells should identify and mark
    cells identity.
    """
    if  not refresh and wt._nbr_border_cell_last_refresh_time  ==  wt.time:
        return wt._nbr_border_cell

    nbr_border_cells=0
    for i in wt.cells():
        if wt.cell_property(cell=i, property="border_cell"):
            nbr_border_cells+=1
            
    wt._nbr_border_cell_last_refresh_time=wt.time
    wt._nbr_border_cell = nbr_border_cells
    
    return wt._nbr_border_cell

def find_top_cell_by_z_coord( wt ):
    cell2center = wt.cell_centers()
    max = float("infinity")
    top_cell = wt.cells()[ 0 ]
    for i in cell2center.keys():
        #print cell2center[ i ]
        if max < cell2center[ i ].z:
            max = cell2center[ i ].z
            top_cell = i
    return top_cell

    
def find_top_cell_by_2d_distance_to_center( wt ):
    """Finds top cell by making projection of all cell centers to 2d xy plane
    and finding the closest cell to the overall gravity center.
    
    :return: dict ("center_cell_id", "gravity_center")
    """
    cc = wt.cell_centers()
    #gc = visual.vector()
    gc = pgl.Vector3()    
    for i in cc.values():
        gc += i
    gc = gc/len( cc )
    #gc0 = visual.vector( gc )
    gc0 = pgl.Vector3( gc )
    gc0.z = 0
    r = {}
    for i in cc:
        v = gc0 - cc[ i ]
        v.z = 0
        #r[ visual.mag( v ) ] = i
        r[ pgl.norm( v ) ] = i
    
    return {"center_cell_id": r[ min(r.keys()) ], "gravity_center":gc}

def store_primordium_position( wt, primordium=None):
    """Saves position of primordium in the tissue properties.
    
    Note: currently the gravity centre is used as one arm of the angle. This
    may lead to errors.
    """
    #for i in wt.cells():
    #    if wt.cell_property( cell=i, property="IC"):
    #        IC = i
    p = wt.tissue_property( property = "primordiums" )
    pp = wt.cell_center( cell=primordium )
    cp = wt.find_top_cell_by_2d_distance_to_center()[ "gravity_center" ]
    #wt.cell_center( cell=IC )
    if wt.cell_property(cell=primordium, property="PrC") > 1:
        i = wt.cell_property(cell=primordium, property="PrC")
        yi = wt.tissue_center() - pp
        zi = wt.tissue_center() - p[ i-1 ][ "ini_pos" ]
        dd = standarize_angle( get_angle_between_primordias( yi, zi) )
        print " #: current div. angle: ", dd
    p[ wt.cell_property(cell=primordium, property="PrC") ] = {"time": wt.time, "center_pos": cp, "ini_pos": pp}
    wt.tissue_property( property = "primordiums", value=p )

def store_primordium_position_wv( wt, primordium_wv=None, number=-1):
    """Saves position of primordium in the tissue properties.
    
    Note: currently the gravity centre is used as one arm of the angle. This
    may lead to errors.
    """
    p = wt.tissue_property( property = "primordiums" )
    pp = wt.wv_pos( wv=primordium_wv )
    cp = wt.find_top_cell_by_2d_distance_to_center()[ "gravity_center" ]
    #wt.cell_center( cell=IC )
    if number >1:
        i = number
        yi = wt.tissue_center() - pp
        zi = wt.tissue_center() - p[ i-1 ][ "ini_pos" ]
        dd = standarize_angle( get_angle_between_primordias( yi, zi) )
        print " #: current div. angle: ", dd
    p[ number ] = {"time": wt.time, "center_pos": cp, "ini_pos": pp}
    wt.tissue_property( property = "primordiums", value=p )

    
def visualise_primordium_information( wt, center=None ):
    """Makes a plot of divergance angles.
    
    Remember to give the right center.
    
    TODO: change to DDS code
    """
    print " #: using predefined center"
    p = wt.tissue_property( property="primordiums" )
    pln = len( p )
    x = range( 1, pln )
    y = []
    for i in range( 2, pln+1 ):
        if not center:
            yi = p[ i ][ "center_pos"] - p[ i ][ "ini_pos" ]
            zi = p[ i-1 ][ "center_pos"] - p[ i-1 ][ "ini_pos" ]
        else:
            yi = center - p[ i ][ "ini_pos" ]
            zi = center - p[ i-1 ][ "ini_pos" ]
            
        #yi = wt.system.forces['radial_move'].center-p[ i ][ "ini_pos" ]
        #zi = wt.system.forces['radial_move'].center-p[ i-1 ][ "ini_pos" ]
        yi.z = 0
        zi.z = 0
        dd = standarize_angle( get_angle_between_primordias( yi, zi) )
        #y.append( yi.diff_angle(zi)*360/(2*math.pi) )
        y.append( dd )
    pl.plot( x, y, "." )
    pl.show()

def wv_edge2cell_edge( wt, wv_edge ):
    cl1 = wt._wv2cell_list[ wv_edge[ 0 ] ]
    cl2 = wt._wv2cell_list[ wv_edge[ 1 ] ]    
    s = []
    for i in cl1:
        if i in cl2:
            s.append( i )
    #print s
    #raw_input()
    if len( s ) != 2:
        raise TypeError("Unable to convert from wv_edge to cell_edge")
    return tuple( s )

def cell_edge2wv_edge( wt, cell_edge ):
    cl1 = wt.cell2wvs_edges( cell=cell_edge[ 0 ] )
    cl2 = wt.cell2wvs_edges( cell=cell_edge[ 1 ] )
    s = []
    for i in cl1:
        if i in cl2:
            return tuple( i )

def pin_level( wtt, cell_edge=None, value=None ):
    wv_edge = cell_edge2wv_edge( wtt, cell_edge=cell_edge )
    #print cell_edge, wv_edge
    try:
        p = pin_level_wv_edge( wtt=wtt, wv_edge=wv_edge, cell_edge=cell_edge, value=value )
    except Exception:
        print " ! pin_level exception.."
        return 0.
    return p
    #if value == None:    
    #    s = wt.cell_edge_property( cell_edge = wt.cell_edge_id( cell_edge ), property="pin_level")  
    #    if cell_edge == wt.cell_edge_id( cell_edge ):
    #        return s[ 0 ]
    #    else:
    #        return s[ 1 ]
    #else:
    #    s = copy.copy( wt.cell_edge_property( cell_edge = wt.cell_edge_id( cell_edge ), property="pin_level")  )
    #    if cell_edge == wt.cell_edge_id( cell_edge ):
    #        s[ 0 ]= value
    #    else:
    #        s[ 1 ]= value
    #    wt.cell_edge_property( cell_edge = wt.cell_edge_id( cell_edge ), property="pin_level", value= s )

def pin_level_wv_edge( wtt, wv_edge=None, cell_edge=None, value=None ):
    ce = wtt.cell_edge_id( cell_edge )
    s = wtt.wv_edge_property( wv_edge = wtt.wv_edge_id( wv_edge ) , property="pin_level")
    if value == None:    
        #s = wtt.wv_edge_property( wv_edge = wtt.wv_edge_id( wv_edge ) , property="pin_level")  
        if ce == cell_edge:
            return s[ 0 ]
        else:
            return s[ 1 ]
    else:
        s=copy.copy(s)
        if ce == cell_edge:
            s[ 0 ] = value
        else:
            s[ 1 ] = value
        wtt.wv_edge_property( wv_edge = wtt.wv_edge_id( wv_edge ) , property="pin_level", value=s)
        #print "pin", s, wtt.wv_edge_property( wv_edge = wtt.wv_edge_id( wv_edge ) , property="pin_level")


def auxin_level( wt, cell=None, value=None ):
    if value==None:
        return wt.cell_property( cell=cell, property="auxin_level" )
    else:
        wt.cell_property( cell=cell, property="auxin_level", value=value )

def calculate_cell_perimiter(wtt, c):
    """Calculates the perimiter of cell cell_id.
    """
    p = 0
    shape = wtt.cell2wvs( c )
    for i in range( len( shape )-1 ):
        p += pgl.norm( wtt.wv_pos( shape[i] ) - wtt.wv_pos( shape[i+1] ) )
        #p += visual.mag( wtt.wv_pos( shape[i] ) - wtt.wv_pos( shape[i+1] ) )
    #print "cell perimiter: ", p
    return p

def calculate_cell_surface( wtt, cell=None, refresh=False ):
    """Calculates cell c surface. Surface is created finding the baricenter,
    and adding the surfaces of triangles which are build up with edge (of the cell)
    and its edges to center. With caching.
    """
    if wtt.has_cell_property( cell=cell, property="surface") and not refresh:
        cs = wtt.cell_property( cell=cell, property="surface")
        if cs[ "time" ]  ==  wtt.time:
            return cs[ "surface" ]
        
    shape = wtt.cell2wvs( cell )
    wv2pos = wtt._wv2pos
    s = calculate_cell_surfaceS( shape, wv2pos )
    wtt.cell_property( cell=cell, property="surface", value={"surface": s, "time": wtt.time})
    return s 


def calculate_wall_length( wt, wv_edge=None ):
    """Calculate the wall length.
           
    Calculate the wall length.
           
        :parameters:
            wt : `WalledTissue`
                Tissue which contains wall
            wv_edge : ``2tuple of int``
                The wall id.
        :rtype: `float`
        :return: Returns the length of wall
        :raise Exception: TODO
    """
    try:
        p = pgl.norm( wt.wv_pos( wv=wv_edge[ 0 ] ) - wt.wv_pos( wv=wv_edge[ 1 ] ) )
    except Exception:
        print " ! calculate_wall_length exception.."
        return 0.
    return p


def calculate_cell_surfaceS( shape, wv2pos ):
    s = 0
    b = pgl.Vector3() 
    #b = visual.vector() 
    ls = len( shape )
    for i in shape:
        b += wv2pos[ i ]
    b = b/ls
    for i in range( ls ):
        vi_vip = wv2pos[ shape[ (i+1)%ls ] ] - wv2pos[ shape[i] ] 
        vi_b = b - wv2pos[ shape[i] ]
        s += pgl.norm( pgl.cross( vi_vip, vi_b )/2 )
        #s += visual.mag( visual.cross( vi_vip, vi_b )/2 )
    #print "surf:", s
    return s
#calculate_cell_surfaceS = staticmethod( calculate_cell_surfaceS )


def clear_incorrect_neighborhood( wt=None ):
    """Clears wrong neighborhood (as an artifact of editing tools).
    
    <Long description of the function functionality.>
    
    :parameters:
        arg1 : `WalledTissue`
            tissue to be cleaned.
    :raise Exception: <Description of situation raising `Exception`>
    """
    for i in wt.cells():
        for j in wt.cell_neighbors( i ):
            if None==cell_edge2wv_edge( wt, cell_edge=(i,j) ):
                wt._cells.delete_edge(i,j)
                
def pyfunction(func_str):
    """ creates a function from a text string """

    if func_str:
        func_str = str(func_str)
        # Extract the function name
        l= func_str.split('\n')
        for line in l:
            if 'def ' in line:
                break
        name=line.split('def ')[1]
        name=name.split('(')[0]

        # local dictionary
        d = {}
        #print str(func_str)
        exec(str(func_str),d)
        
        return d.get(name,None)
    else:
        return None
    
    
def comparePIN_1( wt1=None, wt2=None, tol1=0., tol2=0 ):
    """<Short description of the function functionality.>
    
    <Long description of the function functionality.>
    
    :parameters:
        arg1 : `T`
            <Description of `arg1` meaning>
    :rtype: `T`
    :return: <Description of ``return_object`` meaning>
    :raise Exception: <Description of situation raising `Exception`>
    """
    con=0
    incon=0
    ce1=wt1.cell_edges()
    for (s,r) in ce1:
        #print i,j, pin_level(wt1, (i,j)),pin_level(wt2, (i,j)) 
        for (i,j) in [(s,r), (r,s)]:
            #print i,j, pin_level(wt1, (i,j)),pin_level(wt2, (i,j)) 
            if pin_level(wt1, (i,j)) > tol1:
                if pin_level(wt2, (i,j)) > tol2:
                    con+=1
            if pin_level(wt1, (i,j)) < tol1:
                if pin_level(wt2, (i,j)) < tol2:
                    con+=1
            (i,j) = (j,i)    
    return float(con)/float(len(ce1))/2.


def comparePIN_2( wt1=None, wt2=None, tol1=0., tol2=0 ):
    """<Short description of the function functionality.>
    
    <Long description of the function functionality.>
    
    :parameters:
        arg1 : `T`
            <Description of `arg1` meaning>
    :rtype: `T`
    :return: <Description of ``return_object`` meaning>
    :raise Exception: <Description of situation raising `Exception`>
    """
    con=0
    acon=0
    pos_pumps=0
    neg_pumps=0

    ce1=wt1.cell_edges()

    for (s,r) in ce1:
        #print i,j, pin_level(wt1, (i,j)),pin_level(wt2, (i,j)) 
        for (i,j) in [(s,r), (r,s)]:
            if pin_level(wt1, (i,j)) > tol1:
                if pin_level(wt2, (i,j)) > tol2:
                    con+=1
                pos_pumps+=1
            if pin_level(wt1, (i,j)) < tol1:
                if pin_level(wt2, (i,j)) < tol2:
                    acon+=1
                neg_pumps+=1
    
    if pos_pumps>0: x=float(con)/float(pos_pumps)
    else: x=1.
    if neg_pumps>0:  y=float(acon)/float(neg_pumps)
    else: y=1.
    if pos_pumps+neg_pumps>0: z=float(con+acon)/float(neg_pumps+pos_pumps)
    else: z=1.
    return x,y,z