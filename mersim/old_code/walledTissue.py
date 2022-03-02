#!/usr/bin/env python

"""walledTissue.py

Class containing the abstract tissue.

:version: 2006-07-28 12:01:15CEST
:author: szymon stoma
"""

import visual
##BEGIN DOC REMOVE
import networkx as nx
import pylab as pl
##END DOC REMOVE
import random
import merrysim as m
import math
import pqueue
from const import Mdata, TwoCellsConst
import sets
import tools
import copy

# BEGIN pickle visual vectors
import cPickle as pickle
import copy_reg
def dump_visual_vector( v ):
    return (visual.vector, ( v.x,v.y,v.z ) )
copy_reg.pickle(visual.vector, dump_visual_vector)
# END pickle visual vectors

class TissueTopology:
    """This is basic class to stores tissue topology information and
    basic topology editing algorithms.
    
    - wv: wall vertex
    
    Positions of wv are somehow separeted from properties. This is due
    to the fact that they need to be accessed faster than other properties -
    they are used in physical simulation.
    
    TODO:
    
    next time very important feature should be used:
    
    the cells2wvs should be replaced by cells2edges and edges2cells. all the 
    relation between the cells and its geometry should be between cell to wall edge
    and not like it is now cell to wall vertex. this will simplyfy many other rutines 
    and having a set of edges easily a set of ordered wvs can  be computed. 
    """
    def __init__( self, const = "!SetCorrectConstants!"  ):
        self._wvs = nx.Graph( name = 'CellWalls' )
        """#: to store the information about the cell wvs"""
        self._cells = nx.Graph( name = 'Cells' )
        """#: to store the information about the cell neigborhood relation"""
        self._cell2wv_list = {}
        """#: to store the relation between cells and *ordered* wv"""
        self._wv2cell_list = {}
        """#: to store the realation between walls and cells"""
        
        self._last_wv_id = 0
        """#: to store the free id for wv"""
        self._last_cell_id = 0
        """#: to store the free id for cell"""

        self.const = const
        """#: constants used in simulations."""
 
    def create( self, cell2wv_list = {} ):
        """Creates the WalledTissue structure from data.
            
            :param wv2pos: contains the mapping of ids of wallvertices to their position.
            :param cell2wv_list: contains the mapping of cell ids to ORDERED (in the sens of walls) wv ids.
            :type wv2pos: hash( wv -> pos )
            :type cell2wv_list: hash( cell -> wv_list )
            
            TODO: TEST!!!!!
        """
        
        # to get the cell neighborhood from shared walls
        wv_edges = {}
        for i in cell2wv_list.keys():
            shape = cell2wv_list[ i ]
            l = len( shape )
            for j in shape:
                if j not in self._wvs.nodes():
                    self.add_wv( j )
            self.add_cell( i )
            self.cell2wvs( cell=i, wv_list=cell2wv_list[ i ] )
            self._append_cell2wvs( wvs=cell2wv_list[ i ], c2=i )
            
            for j in range( l ):
                self.add_wv_edge( w1= shape[ j ], w2=shape[ (j+1)%l ] )
                if wv_edges.has_key( (shape[ j ], shape[ (j+1)%l  ] ) ):
                    wv_edges[ (shape[ j ], shape[ (j+1)%l  ] ) ] =  wv_edges[ (shape[ j ], shape[ (j+1)%l  ] ) ] .append( i )
                else:
                    wv_edges[ (shape[ j ], shape[ (j+1)%l  ] ) ] = [ i ] 
        
        for i in wv_edges.keys():
            #TODO we assume that the wall can be shared only between 2 cells
            (s, t) = i
            if len( wv_edges[ i ] ) == 2:
                self.add_cell_edge( wv_edges[ i ][ 0 ], wv_edges[ i ][ 1 ] )
            if wv_edges.has_key( (t,s) ):
                self.add_cell_edge( wv_edges[ i ][ 0 ], wv_edges[ (t,s) ][ 0 ] )
        self.initial_find_the_inside_of_tissue()

    
    def initial_find_the_inside_of_tissue( self ):
        """Changes the internal cell representation to keep cells with the same
        chirality (L or R). It was written to ease the computation of pressure force.
        The divide operation *should* keep this property.
        """
        fcell = self._cells.nodes()[ 0 ]
        already_searched = sets.Set()
        to_search = [fcell]
        already_searched.add( fcell )
        while len(to_search)>1:
            e = to_search.pop()
            cs = self.cell2wvs_edges_in_real_order( e )
            for i in self.cell_neighbors( cell = e ):
                if not i in already_searched:
                    already_searched.add( i )
                    to_search.append( i )
                    cs2 = self.cell2wvs_edges_in_real_order( i )
                    good_order = False
                    for j in cs2:
                        rj = (j[1],j[0])
                        if rj in cs:
                            good_order = True
                            break
                    if not good_order:
                        cs2.revers()
                        self.cell2wvs( i, cs2)
                        
                        
            
        
    def clear_all( self ):
        """ Clears the tissue. After this operation the structure is empty
        (cells and walls are removed).
        """
        self._cells.clear()
        self._wvs.clear()
        self._cell2wv_list = {}
        self._wv2cell_list = {}

    def add_cell( self, cell = None ):
        """ Adds new cell. If cell is given it is used to identify a
        cell. Otherwise the new one is generated using _new_cell_id. Currently
        no checking is done if the cell id is not already taken.
        
        :param cell: new cell id ( None to autoassign).
        :type cell:  cell id (currently int)
        """
        if cell == None:
            cell = self._new_cell_id()
        self._update_last_cell_id( cell )
        self._cells.add_node( cell )
        self._cell2wv_list[ cell ] = []
        return cell
    
    def add_wv( self, wv = None ):
        """Adds wall vertex with position. If wv is given it is used to identify a wall vertex.
        Otherwise the new one is generated using _new_wv_id. Currently
        no checking is done if the wv id is not already taken.
        
        :param wv: new wv id ( None to autoassign).
        :type wv:  wv id (currently int)
        """
        if wv == None:
            wv = self._new_wv_id()
        self._update_last_wv_id( wv )
        self._wvs.add_node( wv )
        self._wv2cell_list[ wv ] = [] 
        return wv

    def add_cell_edge( self, c1=None, c2=None):
        """Adds the edge between cells: c1 and c2.
         
        :raise KeyError: if the c1 or c2 does not exist.
        :param c1: first cell.
        :type c1:  cell id (currently int)
        :param c2: second cell.
        :type c2:  cell id (currently int)
        :return: id of added cell edge.
        :rtype: cell_edge id (currently ordered int 2tuple)
        """
        if not self._cells.has_node( c1 ) or not self._cells.has_node( c2 ):
            raise KeyError("No cell vertex.")
        else:
            self._cells.add_edge( c1, c2 )
            return self.cell_edge_id( (c1, c2 ) )
        
    def add_wv_edge( self, w1=None, w2=None):
        """Adds wall between w1 and w2. If w1 or w2 doesn't exist
        throw exception.

        :raise KeyError: if the w1 or w2 does not exist.
        :Parameters:
            `w1` : wv id (currently int)
                first wv.
            `w2` : wv id (currently int)
                second wv.
            
        :return: id of added wv_edge.
        :rtype: wv_edge id (currently ordered int 2tuple)
        """
        if not self._wvs.has_node( w1 ) or not self._wvs.has_node( w2 ):
            raise KeyError("No wall vertex.")
        else:
            self._wvs.add_edge( w1, w2 )
            return  self.wv_edge_id( (w1,w2) )       

    def cells( self ):
        """Returns collection of cells.
        """
        return self._cells.nodes()
    
    def cell_neighbors( self, cell = None ):
        """Returns neighbors of the cell.
        """
        try:
            return self._cells.neighbors( cell )
        except Exception:
            print " !cell neighbor does not exist.."
            return []
        
    def wvs( self ):
        """Returns collection of wvs.
        """
        return self._wvs.nodes()
    
    def cell_edges( self ):
        """Return the collection of cell edges.
        """
        #! it was not ordered..
        l = self._cells.edges()
        z = []
        for i in l:
            (i1, i2) = i
            if i1 < i2:
                z.append(i)
            else:
                z.append((i2,i1))
        return z

    def wv_edges( self ):
        """Returns the collection of cell edges.
        """
        return self._wvs.edges()

    def nth_layer_from_cell( self, cell=None, distance=1, smaller_than=False ):
        """Returns  the list of cells with discret (graph) distance from ``cell`` equal/smaller ``distance``.
        
        :Parameters:
            `cell` : ``cell`` id
                the cell from which distance is measured.
            `distance`: int
                distance ( default=1 )
            `smaller_than`: bool
                if True the cells which are <= are returned insted of = (default=False) 
        """
        l = nx.bfs_length( self._cells, cell )
        result = []
        for i in l.keys():
            if smaller_than:
                if l[ i ] <= distance:
                    result.append( i )
            else:                
                if l[ i ] == distance:
                    result.append( i )
        return result
    
    
    def cell2wvs( self, cell, wv_list = None):
        """Returns/Sets **ordered** list of vertices associated with the cell.
        
        :Parameters:
            `cell` : ``cell`` id
                ``cell`` to return/set the list of vertices.
            `wv_list` : ``list( wv )`` or ``None``
                if ``wv_list`` is  ``None`` the curent value for cell is returned. Otherwise it is set to ``wv_list``. 
        """
        if wv_list == None:
            return self._cell2wv_list[ cell ]
        else:
            self._cell2wv_list[ cell ] = wv_list
        return None

    def wv2cells( self, wv, cell_list = None ):
        """Returns/Sets list of cells associated with the wv.

        :Parameters:
            `cell_list` : ``list( cell )`` or ``None`` 
                ``cells`` to assign to ``wv``.
            `wv` :  wv
                if ``cell_list`` is  ``None`` the curent value for ``wv`` is returned. Otherwise it is set to ``cell_list``. 
        """
        if cell_list == None:
            return self._wv2cell_list[ wv ]
        else:
            self._wv2cell_list[ wv ] = cell_list
        return None


    def remove_cell( self, cell=None ):
        """Removes the cell.
        
        :param cell: cell to remove
        :type cell: ``cell`` id
        """
        #print "WT::remove_cell"
        #self.investigate_cell( cell )

        cell_shape = self.cell2wvs( cell )
        cell_shape_edges = self.cell2wvs_edges( cell )
        wv2del = []
        wv_edge2del = []
        for wv in cell_shape:
            if self.wv2cells( wv ) == [ cell ]:
                wv2del.append( wv )
        
        neighbors_edges = []
        for n in self.cell_neighbors( cell ):
            for e in self.cell2wvs_edges( n ):
                neighbors_edges.append( e )
        
        for e in cell_shape_edges:
            if not e in neighbors_edges:
                wv_edge2del.append( e )
                
        for wv in wv2del:
            self._remove_wv( wv )
        
        for wv_edge in wv_edge2del:
            self._wvs.delete_edge( wv_edge[ 0 ], wv_edge[ 1 ] )

        for wv in self.cell2wvs( cell ):
            try:
                self.wv2cells( wv, self.wv2cells( wv ).remove( cell ) )
            except ValueError:
                #TODO why??    
                pass
        self._cell2wv_list.pop( cell )
        self._cells.delete_node( cell )

        return {"removed_wv_edges": wv_edge2del, "removed_wv" : wv2del}

    def _clear_unasigned_wvs( self ):
        """Clears wvs which are not assigned to any cell
        """
        for wv in self.wvs(): 
            if self.wv2cells( wv ) == []:
                self._wv2cell_list.pop( wv )
                self._wvs.delete_node( wv )

    def _remove_wv( self, wv ):
        """Removes the wv from the tissue.
        
        Note: _cell2wv_list *IS NOT* updated
        """
        for c in self.wv2cells( wv ):
            self.cell2wvs( c, self.cell2wvs( c ).remove( wv ) )
        self._wv2cell_list.pop( wv )
        self._wvs.delete_node( wv )
    


    def _new_cell_id( self ):
        """Creates new id for a cell
        """
        self._last_cell_id += 1
        return self._last_cell_id

    def _new_wv_id( self ):
        """Creates new id for a wv 
        Note: i assume that it is never negative (i use it will 'testadding' new vertices while 
        new cell shape 'testcreating'..)
        """
        self._last_wv_id += 1
        return self._last_wv_id


    def _update_last_wv_id( self, id ):
        """Updates id for wv.
        """
        if self._last_wv_id < id:
            self._last_wv_id = id

    def _update_last_cell_id( self, id ):
        """Updates id for cell.
        """
        if self._last_cell_id < id:
            self._last_cell_id = id


    def calculate_cell_perimiter(self, c):
        """Calculates the perimiter of cell cell_id.
        """
        p = 0
        shape = self.cell2wvs( c )
        for i in range( len( shape )-1 ):
            #pgl p += pgl.norm( self.wv_pos( shape[i] ) - self.wv_pos( shape[i+1] ) )
            p += visual.mag( self.wv_pos( shape[i] ) - self.wv_pos( shape[i+1] ) )
        #print "cell perimiter: ", p
        return p

    def calculate_cell_surface( self, cell=None, refresh=False ):
        """Calculates cell c surface. Surface is created finding the baricenter,
        and adding the surfaces of triangles which are build up with edge (of the cell)
        and its edges to center. With caching.
        """
        if self.has_cell_property( cell=cell, property="surface") and not refresh:
            cs = self.cell_property( cell=cell, property="surface")
            if cs[ "time" ]  ==  self.time:
                return cs[ "surface" ]
            
        shape = self.cell2wvs( cell )
        wv2pos = self._wv2pos
        s = WalledTissue.calculate_cell_surfaceS( shape, wv2pos )
        self.cell_property( cell=cell, property="surface", value={"surface": s, "time": self.time})
        return s 


    def calculate_cell_surfaceS( shape, wv2pos ):
        s = 0
        #b = pgl.Vector3() 
        b = visual.vector() 
        ls = len( shape )
        for i in shape:
            b += wv2pos[ i ]
        b = b/ls
        for i in range( ls ):
            vi_vip = wv2pos[ shape[ (i+1)%ls ] ] - wv2pos[ shape[i] ] 
            vi_b = b - wv2pos[ shape[i] ]
            #pgl s += pgl.norm( pgl.cross( vi_vip, vi_b )/2 )
            s += visual.mag( visual.cross( vi_vip, vi_b )/2 )
        #print "surf:", s
        return s
    calculate_cell_surfaceS = staticmethod( calculate_cell_surfaceS )
    def wv_edge_id( self, wv_edge=None ):
        """Returns good id for wv_edge 
        
        :param id: id of the wv_edge
        :type id: 2tuple of wall_vertex_id (currenty int tuple)
        :return: correct id of the wv_edge
        :rtype: 2tuple of wall_vertex_id (currenty int tuple)"""

        w1, w2 = wv_edge
        if w1 > w2:
            return (w2, w1)
        else:
            return wv_edge

    def cell_edge_id( self, id ):
        """Returns good id for cell_edge 
        
        :param id: id of the cell_edge
        :type id: 2tuple of cell_id (currenty int tuple)
        :return: correct id of the cell_edge
        :rtype: 2tuple of cell_id (currenty int tuple)"""

        w1, w2 = id
        if w1 > w2:
            return (w2, w1)
        else:
            return id

    
    def investigate_cell( self, cell ):
        """Gives some data about cell internal representation. Mainly for debugging.
        """
        if self._cells.has_node( cell ):
            print "Cell id:", cell
            print "Shape:", self.cell2wvs( cell ) 
            print "Neighbors:", self._cells.neighbors( cell )
            #print "WV in this cell are also in:"
            #for w in self.cell2wvs( cell ):
            #    print " ", w, ": ", self.wv2cells( w )
            return True
        else:
            print "Cell",cell,"doesn't exist.."
            if (self._cell2wv_list.has_key( cell ) ):
                print "Problem in _cell2wv_list -- cell not cleared."
            return False


    def _create_shapes_for_new_cells( shape, v1, v2 ):
        """Create new cell shapes with a shape from old ones and the data from v1 and v2 (sx, tx. vxd).
        This is internal method. It was made from a piece
        of code which was used inside of _divide_cell, becouse it was needed for division 
        unaffecting the structures. Returns two lists filled with vertices (TODO make expression
        defining these lists). 
        """
        s1, t1, v1d = v1
        s2, t2, v2d = v2
        wvc1 = []
        wvc2 = []
        ls = len( shape )
       
        for i in range( ls ):
            wvc1.append( shape[ i%ls ] )
            stop = i
            if tools.upe( ( shape[ i%ls ], shape[ (i+1)%ls ] ), (s1, t1) ):
                break

        wvc1.append( v1d )
        wvc1.append( v2d )
        wvc2.append( v2d )
        wvc2.append( v1d )

        for i in range( (stop+1)%ls, ls ):
            wvc2.append( shape[ i%ls ] )
            stop = i
            if tools.upe( (shape[ i%ls ], shape[ (i+1)%ls ]), (s2, t2) ) : 
                break 

        for i in range( (stop+1), ls ):
            wvc1.append( shape[ i ] )
        return wvc1, wvc2
    _create_shapes_for_new_cells = staticmethod( _create_shapes_for_new_cells )
    def _test_divide_cell( self, cell, i1, i2 ):
        """Used to get test cell division -- one which *won't* modify the structure.
        """
        #!! exact copy of divide
        ( s1, t1 ) = i1
        ( s2, t2 ) = i2
        # finding good order of s1, t1 and s2, t2
        shape = self.cell2wvs( cell )
        # finding which edge is first
        #print s1, t1, shape
        s1, t1 = tools.find_edge_order( s1, t1, shape)
        s2, t2 = tools.find_edge_order( s2, t2, shape)
        s1, t1, p1, s2, t2, p2 = tools.find_edges_order( s1, t1, None, s2, t2, None, shape)
        
        # now we have assumptions:
        # -- for i in {1,2}: si, ti is in shape on positions: if shape[k_i]=si then shape[(k+1)_i]=ti
        # -- k_1 < k_2

        #!! END exact copy of divide
        
        #-1, -2 is used as fake descriptors, they should be never used as real ones..
        return WalledTissue._create_shapes_for_new_cells( shape, (s1, t1, -1), (s2, t2, -2) )
        
      
    
    def _divide_cell( self, cell, i1,  i2 ):
        """Internal cell division updating all the structures.
        """
        ( s1, t1, p1 ) = i1
        ( s2, t2, p2 ) = i2
        # finding good order of s1, t1 and s2, t2
        shape = self.cell2wvs( cell )
        # finding which edge is first
        s1, t1 = tools.find_edge_order( s1, t1, shape)
        s2, t2 = tools.find_edge_order( s2, t2, shape)
        s1, t1, p1, s2, t2, p2 = tools.find_edges_order( s1, t1, p1, s2, t2, p2, shape)
        
        # now we have assumptions:
        # -- for i in {1,2}: si, ti is in shape on positions: if shape[k_i]=si then shape[(k+1)_i]=ti
        # -- k_1 < k_2
        v1d = self.add_wv( None, p1 )
        v2d = self.add_wv( None, p2 )
        
        self.add_wv_edge( v1d, s1 )
        self.add_wv_edge( v1d, t1 )
        self.add_wv_edge( v2d, s2 )
        self.add_wv_edge( v2d, t2 )
        self.add_wv_edge( v1d, v2d )

        # the v1d, v2d must be added to neighbor cells
        for c in self._cells.neighbors( cell ):
            #print "self.cell_has_wall( c, (s1, t1 ) ):", c, (s1, t1)
            if self.cell_has_wall( c, (s1, t1 ) ):
                #print "ok"
                self._append_cell2wvs( [v1d], c )
                break
        for c in self._cells.neighbors( cell ):
            #print "self.cell_has_wall( c, (s1, t1 ) ):", c, (s2, t2)
            if self.cell_has_wall( c, (s2, t2 ) ):
                #print "ok"
                self._append_cell2wvs( [v2d], c )
                break

        wvc1, wvc2 = WalledTissue._create_shapes_for_new_cells( shape, (s1, t1, v1d), (s2, t2, v2d) )
        
        c1 = self.add_cell()
        c2 = self.add_cell()
        self.cell2wvs( c1, wvc1 )
        self.cell2wvs( c2, wvc2 )
        self.add_cell_edge( c1, c2 )
        
        c1n = []
        for wv in wvc1:
            c1n += self.wv2cells( wv )
        for c in dict(map(lambda a: (a,1), c1n)).keys(): 
            self.add_cell_edge( c, c1 )

        c2n = []
        for wv in wvc2:
            c2n += self.wv2cells( wv )
        for c in dict(map(lambda a: (a,1), c2n)).keys():
            self.add_cell_edge( c, c2 )
        
        for z in [c1, c2]:
            for wv in self.cell2wvs( z ):
                for c in self.wv2cells( wv ):
                    self.add_cell_edge( c, z )

        ##m_f
        neighbor_cells = []
        for i in [s1, t1, s2, t2]:
            neighbor_cells += self.wv2cells( i )
        neighbor_cells = dict(map(lambda a: (a,1), neighbor_cells)).keys()
        for c in neighbor_cells:
            self._exchange_wvs( c, (s1,t1), v1d )
            self._exchange_wvs( c, (s2,t2), v2d )
        
        self._wvs.delete_edge( s1, t1 )
        self._wvs.delete_edge( s2, t2 )

        self._append_cell2wvs( wvc1, c1)
        self._append_cell2wvs( wvc2, c2)

        ##m_f
        self.remove_cell( cell )

        #self.investigate_cell( c1 )
        #self.investigate_cell( c2 )
        
        # return format:
        # (v1d, v2d) - added vertices descriptors
        # (removed_wall1, removed_wall2
        #( v1d, s1 )
        #( v1d, t1 )
        #( v2d, s2 )
        #( v2d, t2 )
        #( v1d, v2d )
        return ( ( ( v1d, p1 ), (v2d, p2) ), ( ( v1d, s1 ), ( v1d, t1 ),( v2d, s2 ),( v2d, t2 ),( v1d, v2d ) ), {"removed_cell":cell, "added_cell1":  c1, "added_cell2": c2} )

    def cell_has_wall( self, c, (s, t)):
        """Returns True if cell contains wall (s, t).
        """
        shape = self.cell2wvs( c )
        ls = len( shape )
        for i in range( ls ):
            if ( s == shape[ i%ls ] and t == shape[ (i+1)%ls ] ) or ( t == shape[ i%ls ] and s == shape[ (i+1)%ls ] ): 
                return True
        return False


    def cell2wvs_edges( self, cell ):
        """ Return a list of wvs_edges which surround the cell. 
        
        """
        l = []
        shape = self.cell2wvs( cell )
        ls = len( shape )
        for i in range( ls ):
            if  shape[ i ] < shape[ (i+1)%ls ]:
                l.append( (shape[ i ], shape[ (i+1)%ls ]) )
            else:
                l.append( (shape[ (i+1)%ls ], shape[ i ]) )
        return l

    def cell2wvs_edges_in_real_order( self, cell ):
        """ Return a list of wvs_edges which surround the cell. 
        
        Note: returned ids *may not* be valid wall ids.
        """
        l = []
        shape = self.cell2wvs( cell )
        ls = len( shape )
        for i in range( ls ):
            l.append( (shape[ i ], shape[ (i+1)%ls ]) )
        return l

    def _append_cell2wvs( self, wvs, c2):
        """Sets wv2cells for each wv in wvs. 
        """
        if not self._cells.has_node( c2 ): raise Exception("Cell doesn't exist.") 
        for wv in wvs:
            t = self.wv2cells( wv )
            t.append( c2 )
            #filter
            self.wv2cells( wv, dict(map(lambda a: (a,1), t)).keys() )

    def _exchange_wvs( self, c, (s1,t1), v1d ):
        """Exchange the wall s1, t1 for cell c with two walls s1 v1d and v1d t1. Do nothing
        if the wall can not be found.
        """
        #TODO opt
        if not self.cell_has_wall( c, (s1, t1) ): return
        shape = self.cell2wvs( c )
        ls = len( shape )
        i = shape.index( s1 )
        if t1 == shape[ (i+1)%ls ]: 
            i += 1
            self.cell2wvs( c, shape[:i]+[v1d]+shape[i:])
        else:
             self._exchange_wvs( c, (t1,s1), v1d )

    def cfd_perimiter_rule(self):
        """Returns list of cells which should divide acording to perimiter rule"""
        to_divide = []
        for c in self.cells():
            if self.calculate_cell_perimiter( c ) > self.const.cs_peri_trashhold_perimiter_to_divide_cell: to_divide.append( c )
        return to_divide 

    def cfd_surface_rule(self):
        """Returns list of cells which should divide acording to surface rule"""
        to_divide = []
        for c in self.cells():
            if self.calculate_cell_surface( c ) > self.const.cs_surf_max_surface_before_division: to_divide.append( c )
        return to_divide 

    
    def ds_perimiter( self, dscs ):
        """Division strategy: Divides cells acording to perimiter rule."""
        divide_cells = self.cfd_perimiter_rule()
        l = []
        for c in divide_cells:
            l.append( self.divide_cell( c, dscs ) )
        return l

    def ds_surface( self, dscs ):
        """Division strategy: Divides cells acording to perimiter rule."""
        divide_cells = self.cfd_surface_rule()
        l = []
        for c in divide_cells:
            l.append( self.divide_cell( c, dscs ) )
        return l

    def _test_if_division_is_possible( self, shape ):
        """Returns True if cell can be divided. Currently the cell can't be divided if it has less than 3 walls. 
        """
        i = len( shape )
        if i < 3: 
            # TODO drop exception
            print "Skipping division of degenerated cell:", cell
            return False
        return True

    def dscs_shortest_wall( self, cell ):
        """Divide Single Cell Strategy: divides taking the shortest possible wall. TODO explain.
        """
        shape = self.cell2wvs( cell )
        self._test_if_division_is_possible( shape )
        dshape = shape+shape
        ls = len(shape)
        vmin = 100000000000000000000000;
        for i in range( ls ): 
            s1t = self.wv_pos( dshape[ i ] )
            t1t = self.wv_pos( dshape[ i+1 ] )
            s2t = self.wv_pos( dshape[ i+ls/2 ] )
            t2t = self.wv_pos( dshape[ i+1+ls/2 ] )
            p1t = t1t + (s1t-t1t)/2.
            p2t = t2t + (s2t-t2t)/2.
            #pgl if pgl.norm( p1t-p2t ) < vmin:
            if visual.mag( p1t-p2t ) < vmin:
                #pgl vmin = pgl.norm( p1t-p2t ) 
                vmin = visual.mag( p1t-p2t ) 
                p1 = p1t
                p2 = p2t
                s1 = dshape[ i ]
                t1 = dshape[ i+1 ]
                s2 = dshape[ i+int(ls/2) ]
                t2 = dshape[ i+1+int(ls/2) ]
        return ( (s1, t1, p1), (s2, t2, p2) ) 

    def dscs_shortest_wall_with_geometric_shrinking( self, cell ):
        """Divide Single Cell Strategy: divides taking the shortest possible wall and aditionaly shinks new wall. 
        """
        ( (s1, t1, p1), (s2, t2, p2) )=self.dscs_shortest_wall( cell )
        d = (p1 - p2) *0.1
        return ( (s1, t1, p1-d), (s2, t2, p2+d) )


    def dscs_first_wall( self, cell ):
        """Divide Single Cell Strategy: divides taking the first possible wall. TODO explain.
        """
        shape = self.cell2wvs( cell )
        i = len( shape )
        self._test_if_division_is_possible( shape ) 
        s1 = shape[0]
        t1 = shape[1]
        s2 = shape[ i/2 ]
        t2 = shape[ i/2+1 ]
        p1 = self.wv_pos( t1 ) + ( self.wv_pos( s1 ) - self.wv_pos( t1 ) )/2.
        p2 = self.wv_pos( t2 ) + ( self.wv_pos( s2 ) - self.wv_pos( t2 ) )/2.
        return ( (s1, t1, p1), (s2, t2, p2) ) 

    def dscs_shortest_wall_with_equal_surface( self, cell ):
        """Divide Single Cell Strategy: divides taking the shortest possible wall but dividing the cells
        into two parts of same surface. 
        """
        surfs = pqueue.PQueue()
        shape = self.cell2wvs( cell )
        self._test_if_division_is_possible( shape )
        dshape = shape+shape
        ls = len(shape)
        vmin = 100000000000000000000000;
        for i in range( ls ): 
            s1 = dshape[ i ] 
            t1 = dshape[ i+1 ] 
            s2 = dshape[ i+ls/2 ]
            t2 = dshape[ i+1+ls/2 ]
            s1t = self.wv_pos( s1 )
            t1t = self.wv_pos( t1 )
            s2t = self.wv_pos( s2 )
            t2t = self.wv_pos( t2 )
            
            # getting new cell shapes
            wvc1, wvc2 = self._test_divide_cell( cell, (s1, t1), (s2, t2) )

            # creating the position dict
            wv2pos = {}
            for wv in shape:
                  wv2pos[ wv ] = self.wv_pos( wv )

            #TODO exchange it with const
            # this loops divide the each wall into 6 segments
            z = self.const.dscs_shortest_wall_with_equal_surface_nbr_of_segments_in_wall
            for k in range( 1,z ):
                p1t = t1t + k*(s1t-t1t)/(z+1.)
                p2t = t2t + k*(s2t-t2t)/(z+1.)
                # adding new points coords to calculate area
                wv2pos[ -1 ] = p1t
                wv2pos[ -2 ] = p2t
        
                surf1 = WalledTissue.calculate_cell_surfaceS( wvc1, wv2pos ) 
                surf2 = WalledTissue.calculate_cell_surfaceS( wvc2, wv2pos ) 

                #if math.fabs( surf1 - surf2 ) < vmin:
                #    vmin = math.fabs( surf1 - surf2 ) 
                #    p1m = p1t
                #    p2m = p2t
                #    s1m = s1
                #    s2m = s2
                #    t1m = t1
                #    t2m = t2
                surfs.insert( math.fabs( surf1 - surf2 ), ( (s1, t1, p1t), (s2, t2, p2t) )  )
        
        # getting the shortest wall according to the dscs_shortest_wall strategy
        shortest_possible = self.dscs_shortest_wall( cell )
        ( (s1sp, t1sp, p1sp), (s2sp, t2sp, p2sp) ) = shortest_possible
        #pgl shortest_possible_len = pgl.norm( p1sp - p2sp )
        shortest_possible_len = visual.mag( p1sp - p2sp )

        # we try to find first good (int terms of shortness) dividing wall
        while len( surfs ):
            val, ( (s1m, t1m, p1m), (s2m, t2m, p2m) ) = surfs.pop()
            #pgl if 0.95*pgl.norm( p1m - p2m ) < shortest_possible_len: 
            if self.const.dscs_shortest_wall_with_equal_surface_length_tolerance*visual.mag( p1m - p2m ) < shortest_possible_len: 
                return ( (s1m, t1m, p1m), (s2m, t2m, p2m) )

        # none of the walls dividing the cell on two semiequal parts is short enought, so we take the shortest
        return shortest_possible

        #return ( (s1m, t1m, p1m), (s2m, t2m, p2m) ) 

    def divide_cell( self, cell, dscs):
        """Divides the cell with given strategy of the division.
        """
        ( (s1, t1, p1), (s2, t2, p2) ) = dscs( self, cell )
        return self._divide_cell( cell, (s1, t1, p1 ), (s2, t2, p2) )
    def find_degenerated_cells( self ):
        for i in self.cells():
            if len( self.cell2wvs( cell=i ) ) < 3:
                print " ! degenerated cell:", i, self.cell2wvs( cell=i )
        for i in self.wvs():    
            if len( self.wv2cells( wv=i ) ) != 3 and len( self.wv2cells( wv=i ) ) != 2:
                print " ! degenerated wv:", i, self.wv2cells( wv=i )


class WalledTissue(TissueTopology):
    """Gathers information (curently Topology+Physiology) about Tissue.
    This is main B{data structure} for storing Tissue related properties.
    It extends TissueTopology to store tissue physiology and basic
    physiology editing algorithms. It inherits because the physiology requires
    topology.
    
    The mechanism for setting cell properties:
    1/ in self.const.*_properties we can find an information describing
    all required * properties.
    2/ they are used in _init_*_properties to set a default values (taken from self.const...).
    3/ init should be run manually.
    
    Currently they are two ways of creating initialised WalledTissue:
    1/ create(..)
    This one should be used when the WT data are previousely prepared.
    2/_create_from..
    This one should not be used. It depands on Pierres code and old merrysim libraries.
    Anyway, when it is used it reads meristem .dat file (depanding on configuration in const),
    tries to load stack files to get z coords. In the future it should use create(..).
    
    Note: The [_]create* is not called from __init__.
    """

    def __init__( self, const=None ):
        """Basic constructor. Const is the configuration Class.
        """
        TissueTopology.__init__( self, const=const )
        
        self._wv_edge2properties={}
        """#: contains properties of wv_edge"""
        self._wv2properties={}
        """#: contains properties of wv"""
        self._cell2properties={}
        """#: contains properties of cell"""
        self._cell_edge2properties={}
        """#: contains properties of cell_edge"""
        self._wv2pos = {}
        """:# to store the positions"""
        self._tissue_properties = {}
        """:# to store information about the tissue"""
        
        # BEGIN GLOBAL TISSUE PROPERTIES
        self.time = -100.
        self._nbr_border_cell_last_refresh_time=-100.
        self._nbr_border_cell = 1
        """#: used to trace events in tissue"""
        # END GLOBAL TISSUE PROPERTIES
        
        self._init_tissue_properties()    

        self.tissue_center_ = visual.vector( )
        
    def create( self, wv2pos = {}, cell2wv_list = {} ):
        """Creates the WalledTissue structure from data.
            
            :param wv2pos: contains the mapping of ids of wallvertices to their position.
            :param cell2wv_list: contains the mapping of cell ids to ORDERED (in the sens of walls) wv ids.
            :type wv2pos: hash( wv -> pos )
            :type cell2wv_list: hash( cell -> wv_list )
        """
        self.clear_all()
        TissueTopology.create( self, cell2wv_list=cell2wv_list)
        
        for i in wv2pos.keys():
            self.add_wv( wv=i, pos=visual.vector( wv2pos[ i ].x, wv2pos[ i ].y, wv2pos[ i ].z ) )
        
    def _create_TissueTopologyFromSimulation( self ):
        self.clear_all()
        #TODO to be dropped
        # to load the data from supported format
        #!TODO ugly but currently are more important things to do
        _simulation = m.Simulation( self.const.meristem_data , 10, 0.1 )
        
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
                #pgl self.add_wv( v1Id, pgl.Vector3( v1.x, v1.y, v1.z ) )
                #pgl self.add_wv( v2Id, pgl.Vector3( v2.x, v2.y, v2.z ) )
                self.add_wv( v1Id, visual.vector( v1.x, v1.y, v1.z ) )
                self.add_wv( v2Id, visual.vector( v2.x, v2.y, v2.z ) )
                self.add_wv_edge( v1Id, v2Id )
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
                self.add_cell( v1Id )
                self.add_cell( v2Id )
                self.add_cell_edge( v1Id, v2Id )
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
                        self.cell2wvs( c, self.cell2wvs( c ).append( w ) ) 
                except Exception:
                    pass
        except StopIteration:
            pass
        
        # creating the wv2cell
        for c in self.cells():
            for w in self.cell2wvs( c ):
                if c not in self.wv2cells( w ):
                    self.wv2cells( w, self.wv2cells( w ).append( c ) )

        try:
            self._get_z_coords()
            pass
        except Exception:
            print "Loading of Z coords skipped"
            
        #for vw in self.wvs():
        #    self.wv_pos( vw, self.wv_pos( vw )*self.const.meristem_load_scale )
        ##finding inside
        #self.initial_find_the_inside_of_tissue()

    def wv_pos( self, wv=None, pos = None ):
        """Returns/Sets the position of wall vertex
        """
        if (pos == None):
            return self._wv2pos[ wv ]
        else:
            self._wv2pos[ wv ] = pos
        return None

 
    def add_cell_edge( self, c1=None, c2=None):
        """ Add the cell neighborhood between cells: c1 and c2.
        """
        c = TissueTopology.add_cell_edge( self, c1=c1, c2=c2 )
        self._init_cell_edge_properties(  c )
        self.cell_edge_property( cell_edge=c, property="creation_time", value=self.time )
        return c

    def add_cell( self, cell=None, shape=None):
        """ Adds the cell neighborhood between c1 and c2.
        If shape is given the microtubules orientation is set
        """
        if shape==None:
            cell_id = TissueTopology.add_cell( self, cell=cell )
            self._init_cell_properties( cell_id )
            self.cell_property( cell=cell_id, property="creation_time", value=self.time )
        else:
            self.cell2wvs( cell=cell, wv_list=shape )
            # insert microtubules orientation
                
        
        return cell_id
           
    def add_wv_edge( self, w1=None, w2=None):
        """Adds wall between w1 and w2. If w1 or w2 doesn't exist
        throw exception
        """
        w = TissueTopology.add_wv_edge( self, w1=w1, w2=w2 )
        self._init_wv_edge_properties(  w )
        self.wv_edge_property( wv_edge=w, property="creation_time", value=self.time )
        return w
 
    def add_wv( self, wv = None, pos = visual.vector() ):
        """Adds wall vertex with position.
        """
        wv_id = TissueTopology.add_wv( self, wv = wv )
        self._init_wv_properties( wv=wv_id )
        self.wv_property( wv=wv_id, property="creation_time", value=self.time )
        self.wv_pos( wv=wv_id, pos=pos )
        return wv_id

    def clear_all( self ):
        """Clears structure.
        """
        TissueTopology.clear_all( self )
        self._wv2pos = {}
        self._wv_edge2properties={}
        self._wv2properties={}
        self._cell2properties={}
        self._cell_edge2properties={}
        self._tissue_properties = {}

    
    # BEGIN Physiology related methods
    
    # BEGIN wv_edge properties
    def _init_wv_edge_properties( self, wv_edge=None):
        """Inits wv edge properties. All properties should be initialised here.
        """
        self._wv_edge2properties[ wv_edge ] = {}
        for i in self.const.wv_edge_properties:
            self._wv_edge2properties[ wv_edge ][ i ] = self.const.wv_edge_properties[ i ]

    def  wv_edge_property( self, wv_edge=None, property=None, value=None ):
        """Returns/sets property for wv_edge
        """
        if value == None:
            return self._wv_edge2properties[ self.wv_edge_id( wv_edge ) ][ property ]
        else:
            self._wv_edge2properties[ self.wv_edge_id( wv_edge ) ][ property ] = value
    
    # END wv_edge properties
    
    # BEGIN wv properties
    def _init_wv_properties( self, wv=None):
        """Inits wv properties. All properties should be initialised here.
        """
        self._wv2properties[ wv ] = {}
        for i in self.const.wv_properties:
            self._wv2properties[ wv ][ i ] = self.const.wv_properties[ i ]
 
    def  wv_property( self, wv=None, property=None, value=None ):
        """Returns/sets property for wv
        """
        if value == None:
            return self._wv2properties[ wv  ][ property ]
        else:
            self._wv2properties[ wv  ][ property ] = value
    
    # END wv properties
    
    # BEGIN cell properties
    def _init_cell_properties( self, cell=None):
        """Inits wv properties. All properties should be initialised here.
        """
        self._cell2properties[ cell ] = {}
        for i in self.const.cell_properties:
            self._cell2properties[ cell ][ i ] = self.const.cell_properties[ i ]
        
        ## auxin_level
        #self._cell2properties[ cell ][ "auxin_level" ] = 5*random.random()
        self._cell2properties[ cell ][ "auxin_level" ] = 0
        #TODO remove
        #if cell <= 10:
            #print "10"
        #    self._cell2properties[ cell ][ "auxin_level" ] = 20

        ## auxin_level_1
        self._cell2properties[ cell ][ "auxin_level_1" ] = 0
            
        ## identity
        self._cell2properties[ cell ][ "identity" ] = "normal"
        
        ## mtb_orientation
        self._cell2properties[ cell ][ "mtb_orientation_angle" ] = 0
 
        ## was_under_angular_stress
        self._cell2properties[ cell ][ "was_under_angular_stress" ] = False
        
    def  cell_property( self, cell=None, property=None, value=None ):
        """Returns/sets property for cell
        """
        if value == None:
            return self._cell2properties[ cell ][ property ]
        else:
            self._cell2properties[ cell  ][ property ] = value

    def has_cell_property( self, cell=None, property=None):
        """True iff property exists
        """
        return self._cell2properties[ cell ].has_key( property )

    # END cell properties
    
    # BEGIN tissue properties
    def _init_tissue_properties( self ):
        """Inits tissue properties. All properties should be initialised here.
        """
        for i in self.const.tissue_properties:
            self._tissue_properties[ i ] = self.const.tissue_properties[ i ]
    def  tissue_property( self, property=None, value=None ):
        """Returns/sets property for cell
        """
        if value == None:
            return self._tissue_properties[ property ]
        else:
            self._tissue_properties[ property ] = value

    def has_tissue_property( self, property=None):
        """True iff property exists
        """
        return self._tissue_properties.has_key( property )


    # END tissue properties
    
    # BEGIN cell edge properties
    def _init_cell_edge_properties( self, cell_edge=None):
        """Inits cell_edge properties. All properties should be initialised here.
        """
        self._cell_edge2properties[ cell_edge ] = {}
        for i in self.const.cell_edge_properties:
            self._cell_edge2properties[ self.cell_edge_id( cell_edge ) ][ i ] = copy.copy( self.const.cell_edge_properties[ i ] )

 
    def  cell_edge_property( self, cell_edge=None, property=None, value=None ):
        """Returns/sets property for cell_edge
        """
        if value == None:
            return self._cell_edge2properties[ self.cell_edge_id( cell_edge ) ][ property ]
        else:
            self._cell_edge2properties[ self.cell_edge_id( cell_edge ) ][ property ] = value
    
    # END cell edge properties
    
    # END Physiology related methods

    def show_cells( self, with_labels = False ):
        """Plot cells projection on XY plane (does not draw walls).
        """
        nx.draw_networkx( self._cells, self._pos2tuple_pos( self.cell_centers() ), with_labels=with_labels, style='dotted', node_size= self.const.cell_node_size )
        nx.draw_networkx_edges( self._wvs, self._pos2tuple_pos( self._wv2pos ), edge_color='r' )
        pl.show()

    def show_cells_with_wvs( self, with_labels = False ):
        """Plot cells projection on XY plane (draws walls).
        """
        nx.draw_networkx( self._cells, self._pos2tuple_pos( self.cell_centers() ), with_labels=with_labels, style='dotted', node_size= self.const.cell_node_size )
        nx.draw_networkx( self._wvs, self._pos2tuple_pos( self._wv2pos ), edge_color='r', with_labels=with_labels,node_size= self.const.wv_node_size )
        pl.show()

    def cell_center( self, cell = None ):
        """Return baricenter of cell.
        """
        #pgl center = pgl.Vector3() 
        center = visual.vector() 
        l = self.cell2wvs( cell )
        for w in l:
            center += self.wv_pos( w )
        # calculate the baricenter
        #
        return center/ len( l )

    def cell_centers( self):
        """Returns the vertex3 hash of cell 2 baricenter of the cell.
        """
        cc = {}
        for c in self._cells.nodes():
            cc[ c ] = self.cell_center( c ) 
        return cc
    
    def _pos2tuple_pos( self, cell2baricenter ):
        """Returns the hash cell 2 tuple x, y where the x, y are
        coordinats of the baricenter.
        """
        t = {}
        for c in cell2baricenter:
            t[ c ] = (cell2baricenter[ c ].x, cell2baricenter[ c ].y)
        return t


    def get_cell_normal( self, cell = None ):
        """Gets the normal for the cell by collecting the normals from all vertices.
        Note: obsolate. It uses pressure_center to find normals. Currently the WalledTissue is
        in L/R mode and this information should be used to get the normals.
        """
        t = []
        pressure_center=self.const.simple_pressure_center
        av_normal = visual.vector()
        for w in self.cell2wvs( cell = cell):
            lm = self._wvs.neighbors( w )
            if len( lm ) >= 3:
                normal = visual.cross( self.wv_pos( wv=lm[1] ) - self.wv_pos( lm[ 0 ] ), self.wv_pos( lm[2] ) - self.wv_pos( lm[ 1 ] ) )
                if visual.mag( (self.wv_pos( w ) +normal)  - pressure_center ) > visual.mag( (self.wv_pos( w ) - normal) -  pressure_center ):
                    av_normal += visual.norm( normal ) 
                else:
                    av_normal += visual.norm( -normal ) 
        return visual.norm( av_normal )




    def divide_cell( self, cell, dscs):
        """Divides a cell acording to dscs strategy.
        
        TODO: the cell divided in TissueTopology should not contain positions.
        """
        
        # saving mt
        shape = self.cell2wvs( cell = cell )
        s1 = shape[0]
        t1 = shape[1]
        s1pos = self.wv_pos( wv=s1 )
        t1pos = self.wv_pos( wv=t1 )
        middle_of_wall = t1pos + ( s1pos - t1pos )/2.
        center_of_cell = self.cell_center( cell = cell )
        axis = (middle_of_wall - center_of_cell).rotate( angle = self.cell_property( cell=cell, property="mtb_orientation_angle"), axis=visual.cross(s1pos-center_of_cell, t1pos-center_of_cell) ) 
        #
        
        #saving surface
        surf = self.calculate_cell_surface( cell = cell )
        cell_center = self.cell_center( cell = cell )

        #saving pin:
        pin_c2n={}
        pin_n2c={}
        for i in self.cell_neighbors( cell = cell ):
            pin_c2n[ i ] = self.pin( (cell, i) )
            pin_n2c[ i ] = self.pin( (i, cell) )
        
        #saving properties
        saved_prop = {}
        for cp in self._cell2properties[ cell ].keys():
            saved_prop[ cp ] = self.cell_property( cell, cp)
        
        r = TissueTopology.divide_cell( self, cell=cell, dscs=dscs )
        ( ( ( v1d, p1 ), (v2d, p2) ), ( ( v1d, s1 ), ( v1d, t1 ),( v2d, s2 ),( v2d, t2 ),( v1d, v2d ) ), dict )  =  r
        for i in ( dict[ "added_cell1"], dict[ "added_cell2" ] ):
            for cp in saved_prop.keys():
                    self.cell_property( i, cp, saved_prop[ cp ] )
        if saved_prop["PrC"]>0:
            # criterium of distance to the right path
            ##added_cell_1_center = self.cell_center( dict[ "added_cell1"] )
            ##added_cell_2_center = self.cell_center( dict[ "added_cell2"] )
            ##cell_init_pos = self.tissue_property( "primordiums" )[ saved_prop["PrC"] ][ "ini_pos" ]
            ##center = self.tissue_center()
            ##correct_path_direction = cell_init_pos - center
            ##a1 = visual.diff_angle( added_cell_1_center - center,correct_path_direction)  
            ##a2 = visual.diff_angle( added_cell_2_center - center,correct_path_direction)
            ##if a1 < a2:
            #if self.cell_center( cell=dict[ "added_cell1" ] ).z < self.cell_center( cell=dict[ "added_cell2" ] ).z :
            cs = self.cell2wvs( cell=dict[ "added_cell1" ] )
            prm=False
            for i in cs:
                if self.wv_property(wv=i, property="PrC") == saved_prop["PrC"]:
                    prm=True
            if prm:
                self.cell_property( cell=dict["added_cell1"], property="PrC", value= saved_prop["PrC"])
                self.cell_property( cell=dict["added_cell2"], property="PrC", value=0 )
            else:
                self.cell_property( cell=dict["added_cell2"], property="PrC", value= saved_prop["PrC"] )
                self.cell_property( cell=dict["added_cell1"], property="PrC", value=0 )

        # pumps
        added_cells = [dict["added_cell1"], dict["added_cell2"]]
        #print pin_c2n, added_cells
        for c in added_cells:
            for i in self.cell_neighbors( c ):
                if i not in added_cells:
                    #print c, i
                    if pin_c2n[ i ] >pin_c2n[ i ]:
                        self.pin( (c,i), pin_c2n[ i ] )
                        self.pin( (i,c), pin_n2c[ i ] )
                    else:
                        self.pin( (c,i), pin_c2n[ i ] )
                        self.pin( (i,c), pin_n2c[ i ] )
                else:
                    pass
                    # leave default value
                    
        ## automatic IC identity
        if saved_prop["IC"]:
            #self.cell_property( cell=dict["added_cell2"], property="IC", value="False" )

            if self.cell_center( cell=dict[ "added_cell1" ] ).z < self.cell_center( cell=dict[ "added_cell2" ] ).z :
                self.cell_property( cell=dict["added_cell1"], property="IC", value=False )
                self.cell_property( cell=dict["added_cell2"], property="IC", value=True )
            else:
                self.cell_property( cell=dict["added_cell2"], property="IC", value=False )
                self.cell_property( cell=dict["added_cell1"], property="IC", value=True )

        
        #for aux concentration:
        #self.cell_property( cell=dict["added_cell1"], property="auxin_level", value = saved_prop["auxin_level"]*self.calculate_cell_surface(cell=dict["added_cell1"], refresh=True)/surf ) 
        #self.cell_property( cell=dict["added_cell2"], property="auxin_level", value = saved_prop["auxin_level"]*self.calculate_cell_surface(cell=dict["added_cell2"], refresh=True)/surf )
        
        # setting new orientation to new cells:
        #for i in ( dict[ "added_cell1"], dict[ "added_cell2" ] ):
        #    axisn = visual.norm( axis )
        #    curent_axisn = visual.norm( self._get_mt_direction( i ) )
        #    steps =  180
        #    mindist = 1000000000000
        #    minteta = 0
        #    for z in range( steps ):
        #        teta=float(z)/steps*2*math.pi
        #        dist = visual.mag(visual.rotate( curent_axisn, teta, visual.cross( axisn, curent_axisn) ) - axisn)
        #        if dist < mindist:
        #            minteta = teta
        #    self.cell_property( i, "mtb_orientation_angle", minteta)
        return r

    def tissue_center( self ):
        return self.tissue_center_
    
    def calculate_average_cell_surface( self ):
        """Calculates the avarage cell surface for all cells in the tissue. Importatnt thing: check for degenerated cells
        before.
        """
        s = 0
        for c in self.cells():
            s += self.calculate_cell_surface( cell = c )
        return s/len( self.cells() )

    def center_group( self ):
        """Returns a group of cells which surrounds initial cell (a cell with IC==True)
        """
        for c in self.cells():
            if self.cell_property( cell=c, property="IC"):
                return [ c ]+self.cell_neighbors( c )

    def _get_z_coords( self, **keys):
        """Docs in Pierrs' code
        TODO: too much is hardcoded right now.
        """
        if self.const.reconstruct_3d_from_slices: 
            slices = m.graph.Slices(self.const.projection_path, 'red')
        print "2"
        z_mul = 6.1
        ratio = 3./4
        for vw in self.wvs():
            v1 = self.wv_pos( vw )
            if self.const.reconstruct_3d_from_slices: 
                z = slices.get_z(v1.x, -v1.y, z_mul, ratio)
            else:
                z = 0
            #pgl v1 = pgl.Vector3(v1.x, v1.y, z )
            v1 = visual.vector(v1.x, v1.y, z )
            self.wv_pos( vw, v1 )
            
    def remove_cell( self, cell=None ):
        """Removes the cell.
        
        :param cell: cell to remove
        :type cell: ``cell`` id
        """
        
        for n in self.cell_neighbors( cell = cell ):
            del self._cell_edge2properties[ self.cell_edge_id( (cell,n) ) ] 
        try:
            del self._cell2properties[ cell ]
        except:
            print "!properties does not exist.."
        return TissueTopology.remove_cell( self, cell = cell )
        
    def investigate_cell( self, cell ):
        """Gives some data about cell internal representation. Mainly for debugging.
        """
        r = TissueTopology.investigate_cell( self, cell )
        if r:
            t = self._cell2properties[ cell ]
            for i in t:
                print "  @",  i, ":", t[ i ]
            print "  @", "aux_conc",":", self.cell_property(cell, "auxin_level")/self.calculate_cell_surface( cell )
            return True
        else:
            return False
        
    def nbr_border_cells( self, refresh=False ):
        """
        Note: working correctly only if cells are beeing fixed. The method fix_cells should identify and mark
        cells identity.
        """
        if  not refresh and self._nbr_border_cell_last_refresh_time  ==  self.time:
            return self._nbr_border_cell

        nbr_border_cells=0
        for i in self.cells():
            if self.cell_property(cell=i, property="border_cell"):
                nbr_border_cells+=1
                
        self._nbr_border_cell_last_refresh_time=self.time
        self._nbr_border_cell = nbr_border_cells
        
        return self._nbr_border_cell
    
    def find_top_cell_by_z_coord( self ):
        cell2center = self.cell_centers()
        max = float("infinity")
        top_cell = self.cells()[ 0 ]
        for i in cell2center.keys():
            #print cell2center[ i ]
            if max < cell2center[ i ].z:
                max = cell2center[ i ].z
                top_cell = i
        return top_cell

        
    def find_top_cell_by_2d_distance_to_center( self ):
        """Finds top cell by making projection of all cell centers to 2d xy plane
        and finding the closest cell to the overall gravity center.
        
        :return: dict ("center_cell_id", "gravity_center")
        """
        cc = self.cell_centers()
        gc = visual.vector()
        for i in cc.values():
            gc += i
        gc = gc/len( cc )
        gc0 = visual.vector( gc )
        gc0.z = 0
        r = {}
        for i in cc:
            v = gc0 - cc[ i ]
            v.z = 0
            r[ visual.mag( v ) ] = i
        
        return {"center_cell_id": r[ min(r.keys()) ], "gravity_center":gc}
    
    def store_primordium_position( self, primordium=None):
        """Saves position of primordium in the tissue properties.
        
        Note: currently the gravity centre is used as one arm of the angle. This
        may lead to errors.
        """
        #for i in self.cells():
        #    if self.cell_property( cell=i, property="IC"):
        #        IC = i
        p = self.tissue_property( property = "primordiums" )
        pp = self.cell_center( cell=primordium )
        cp = self.find_top_cell_by_2d_distance_to_center()[ "gravity_center" ]
        #self.cell_center( cell=IC )
        if self.cell_property(cell=primordium, property="PrC") > 1:
            i = self.cell_property(cell=primordium, property="PrC")
            yi = self.tissue_center() - pp
            zi = self.tissue_center() - p[ i-1 ][ "ini_pos" ]
            dd = standarize_angle( get_angle_between_primordias( yi, zi) )
            print " #: current div. angle: ", dd
        p[ self.cell_property(cell=primordium, property="PrC") ] = {"time": self.time, "center_pos": cp, "ini_pos": pp}
        self.tissue_property( property = "primordiums", value=p )

    def store_primordium_position_wv( self, primordium_wv=None, number=-1):
        """Saves position of primordium in the tissue properties.
        
        Note: currently the gravity centre is used as one arm of the angle. This
        may lead to errors.
        """
        p = self.tissue_property( property = "primordiums" )
        pp = self.wv_pos( wv=primordium_wv )
        cp = self.find_top_cell_by_2d_distance_to_center()[ "gravity_center" ]
        #self.cell_center( cell=IC )
        if number >1:
            i = number
            yi = self.tissue_center() - pp
            zi = self.tissue_center() - p[ i-1 ][ "ini_pos" ]
            dd = standarize_angle( get_angle_between_primordias( yi, zi) )
            print " #: current div. angle: ", dd
        p[ number ] = {"time": self.time, "center_pos": cp, "ini_pos": pp}
        self.tissue_property( property = "primordiums", value=p )

        
    def visualise_primordium_information( self, center=None ):
        """Makes a plot of divergance angles.
        
        Remember to give the right center.
        
        TODO: change to DDS code
        """
        print " #: using predefined center"
        p = self.tissue_property( property="primordiums" )
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
                
            #yi = self.system.forces['radial_move'].center-p[ i ][ "ini_pos" ]
            #zi = self.system.forces['radial_move'].center-p[ i-1 ][ "ini_pos" ]
            yi.z = 0
            zi.z = 0
            dd = standarize_angle( get_angle_between_primordias( yi, zi) )
            #y.append( yi.diff_angle(zi)*360/(2*math.pi) )
            y.append( dd )
        pl.plot( x, y, "." )
        pl.show()
        
    def clear_properties( self ):
        self.clear_cell_properties()
        #self.clear_cell_edge_properties()
        self.clear_tissue_properties()
        #self.clear_wv_properties()
        #self.clear_wv_edge_properties()

    def clear_cell_properties( self ):
        for i in self.cells():
            self._init_cell_properties( i )

    def clear_tissue_properties( self ):
        self._init_tissue_properties()

    def pin( self, cell_edge, value=None ):
        if value == None:    
            s = self.cell_edge_property( cell_edge = self.cell_edge_id( cell_edge ), property="pin_level")  
            if cell_edge == self.cell_edge_id( cell_edge ):
                return s[ 0 ]
            else:
                return s[ 1 ]
        else:
            s = copy.copy( self.cell_edge_property( cell_edge = self.cell_edge_id( cell_edge ), property="pin_level")  )
            if cell_edge == self.cell_edge_id( cell_edge ):
                s[ 0 ]= value
            else:
                s[ 1 ]= value
            self.cell_edge_property( cell_edge = self.cell_edge_id( cell_edge ), property="pin_level", value= s )

def get_angle_between_primordias( yi, yj):
    """Return the angle between primordias.
    """
    d = yi.diff_angle(yj)
    if visual.mag( visual.rotate( yi, axis=(0,0,1), angle=d )- yj ) < 0.001:
        return d*360/(2*math.pi)
    else:
        return (2*math.pi-d)*360/(2*math.pi)

def standarize_angle( a ):
    """Angle standarisation.
    """
    if a > 180:
        return 360 - a 
    return a

    
if __name__ == '__main__':

    wt = WalledTissue( TwoCellsConst() )

    print "__ INIT CELL"
    for c in wt.cells(): wt.investigate_cell( c )
    for i in range(2):
        for c in wt.cells():
            print "__ DIVIDING CELL", c
            wt.divide_cell( c, TissueTopology.dscs_first_wall )
            for c in wt.cells(): wt.investigate_cell( c )
        wt.show_cells_with_wvs(True)
    for i in wt.cells():
        print "__ REMOVING CELL", i
        wt.remove_cell( i )
        wt.show_cells_with_wvs(True)

