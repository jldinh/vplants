#!/usr/bin/env python
"""The serialisation mechanism using openalea.celltissue.serial routines.

No details.

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
__date__="<Timestamp>"
__version__="0.1"
__docformat__= "restructuredtext en"
__revision__="$Id: walled_tissue.py 8407 2010-03-08 07:53:28Z pradal $"

from openalea.celltissue.serial.tissue_pickle import TissuePickleWriter, TissuePickleReader
#TODO it is changed due to the pickling properties 
from celltissue.serial.io_property import *
from celltissue.geometry import Point

from openalea.mersim.tissue.walled_tissue import WalledTissue
from openalea.mersim.tissue.algo.walled_tissue import create, investigate_cell
from openalea.mersim.tissue.algo.walled_tissue_topology import initial_find_the_inside_of_tissue
from openalea.mersim.tools.misc import IntIdGenerator, get_ordered_vertices_from_unordered_shape
import  openalea.plantgl.all as pgl
from openalea.mersim.const.const import TissueConst

def write_walled_tissue( tissue=None, name=None, desc="default description" ):
        wtp = WalledTissuePickleWriter( name, mode="w",
                               tissue=WalledTissue2IOTissue(tissue, id=IntIdGenerator( tissue.wv_edges() )),
                               tissue_properties=WalledTissue2IOTissueProperties( tissue  ),
                               cell_properties=WalledTissue2IOCellPropertyList( tissue  ),
                               wv_properties=WalledTissue2IOEdgePropertyList( tissue ),
                               wv_edge_properties=WalledTissue2IOWallPropertyList( tissue, id=IntIdGenerator( tissue.wv_edges() ) ),
                               description=desc )
        wtp.write_all()
        return wtp

def read_walled_tissue( file_name=None, const=None ):
        wtpr = WalledTissuePickleReader( file_name, mode="r")
        wtpr.read_tissue()
        if const==None:
                from openalea.mersim.const.const import TissueConst
                const=TissueConst()
        wt=IOTissue2WalledTissue( wtpr.tissue, wtpr.wv_properties[ "_positions" ], const=const )
        #print wt.const.cell_properties.keys(),wt.const.wv_edge_properties.keys(),wt.const.tissue_properties.keys()
        for i in wt.const.cell_properties.keys()+wt.const.wv_edge_properties.keys()+wt.const.tissue_properties.keys():
                #print "reading: ", i
                wtpr.read_property( i )
        for i in wt.cells():
                for j in wt.const.cell_properties.keys():
                        wt.cell_property( cell=i, property=j, value=wtpr.cell_properties[ j ][ i ] )
        for i in wt.const.tissue_properties.keys():
                wt.tissue_property( i, wtpr.tissue_properties[ i ] )
        
        for j in wt.const.wv_edge_properties.keys():
                for i in wtpr.tissue.scale_relations[1]:
                    wt.wv_edge_property( wv_edge=tuple(wtpr.tissue.scale_relations[1][i]), property=j, value=wtpr.wv_edge_properties[ j ][ i ] )
        return wt

class WalledTissuePickleWriter ( TissuePickleWriter ):
	def __init__ (self, tissuename, mode="w", tissue=IOTissue(), tissue_properties={},
		      cell_properties={}, wv_properties={},
		      wv_edge_properties={}, description=None ) :
		"""
		try to create a tissuefile
		for writing 'w'
		"""
		TissuePickleWriter.__init__( self, tissuename, mode )
		self.tissue = tissue
		self.tissue_properties = tissue_properties
		self.cell_properties = cell_properties
		self.wv_properties = wv_properties
		self.wv_edge_properties = wv_edge_properties
		self.description = description
			
	def write_tissue(self ) :
		TissuePickleWriter.write_tissue( self, tissue=self.tissue )
		TissuePickleWriter.write_property( self, self.wv_properties[ "_positions" ], "_positions" )
		TissuePickleWriter.write_description( self, self.description, "_desc" )
		
	def write_all( self ):
		TissuePickleWriter.write( self, tissue=self.tissue )
		if self.description != None:
			self.write_description( self.description, "_desc" )
		for i in self.cell_properties:
			self.write_property( self.cell_properties[ i ] , i )
		for i in self.wv_properties:
			self.write_property( self.wv_properties[ i ], i )
		for i in self.wv_edge_properties:
			self.write_property( self.wv_edge_properties[ i ], i )
		for i in self.tissue_properties:
			self.write_property( self.tissue_properties[ i ], i)

class WalledTissuePickleReader ( TissuePickleReader ):
	def __init__ (self, tissuename, mode="w", tissue=IOTissue(), tissue_properties={},
		      cell_properties={}, wv_properties={},
		      wv_edge_properties={}, description=None ) :
		"""
		try to create a tissuefile
		for writing 'w'
		"""
		TissuePickleReader.__init__( self, tissuename, mode )
		self.tissue = tissue
		self.tissue_properties = tissue_properties
		self.cell_properties = cell_properties
		self.wv_properties = wv_properties
		self.wv_edge_properties = wv_edge_properties
		self.description = description
		
			
	def read_property (self, property_name) :
		p = TissuePickleReader.read_property( self, property_name )
		if p.scale==-1:
			self.tissue_properties[ property_name ] = p
		elif p.scale==1:
			self.wv_edge_properties[ property_name ] = p
		elif p.scale==2:
			self.wv_properties[ property_name ] = p
		elif p.scale==0:
			self.cell_properties[ property_name ] = p
		else:
			raise IOError("Read unknown property..")
	
	def read_description (self, description_name="_desc") :
		try:
			self.description = TissuePickleReader.read_description( self, description_name )
		except Exception(): self.description="" 
			
	def read (self, name=None) :
		if self._mode!='r' :
			raise IOError("file not open in the right mode %s" % self._mode)
		if name is None :
			self.tissue = self.read_tissue()
		else :
			if path.exists(path.join(self._dirname,name)) :
				return self.read_external_file(name)
			elif path.exists(path.join(self._dirname,"%s.tip" % name)) :
				self.read_property( property_name=name)
			elif path.exists(path.join(self._dirname,"%s.txt" % name)) :
				self.description = self.read_description(self,name)
			else :
				raise IOError("unable to read %s" % name)
	
	def read_tissue( self ):
		self.read_description()
		self.tissue=TissuePickleReader.read_tissue( self )
		self.wv_properties[ "_positions" ] = TissuePickleReader.read_property( self, "_positions" )



                
                
def IOTissue2WalledTissue( it = None, pos={}, const=None):
        """<Short description of the function functionality.>

        <Long description of the function functionality.>

        :parameters:
            it : `IOTissue`
                Tissue to be converted.
        :rtype: `WalledTissue`
        :return: Converted tissue
        :raise Exception: <Description of situation raising `Exception`>
        """
        if const==None:
                const = TissueConst()
        cell_walls=None
        wall_edges=None
        for i in it.scale_relations:
                if i.scale == 0:
                        cell_walls = i
                elif i.scale == 1:
                        wall_edges = i
        if len( it.scale_relations ) != 3 or not (cell_walls and wall_edges):
                raise Exception("Tissue incompatible")
        #print it.scale_relations
        #transformation of pid into eid
        pid_to_eid={}
        for eid,geom in it.geometry.iteritems() :
                pid,=geom
                pid_to_eid[pid]=eid
        for pid,vec in pos.items() :
                pos[pid_to_eid[pid]]=vec
        #vcreation of shapes
        cell2wv_list = {} #cell to ordered list of wv
        for c in cell_walls.keys():
            cellshape=[]
            for w in cell_walls[ c ]:
                cellshape.append( wall_edges[ w ] )
            cell2wv_list[ c ] = get_ordered_vertices_from_unordered_shape( cellshape )

        from openalea.mersim.const.const import WalledTissueTest
        wt = WalledTissue(const=const) #TODO const
        for i in pos:
                if len( pos[ i ] ) == 1:
                        pos[ i ] = pgl.Vector3(pos[ i ][ 0 ], 0., 0.)
                if len( pos[ i ] ) == 2:
                        pos[ i ] = pgl.Vector3(pos[ i ][ 0 ], pos[ i ][ 1 ], 0.)
                if len( pos[ i ] ) == 3:
                        pos[ i ] = pgl.Vector3(pos[ i ][ 0 ], pos[ i ][ 1 ], pos[ i ][ 2 ])
                else:
                        raise Exception("Problem in position retrival..")
        create( wt, wv2pos=pos, cell2wv_list=cell2wv_list)
        #initial_find_the_inside_of_tissue( wt )
        return wt

def WalledTissue2IOTissue( wt = None, id=IntIdGenerator() ):
        """<Short description of the function functionality.>

        <Long description of the function functionality.>

        :parameters:
            wt : `WalledTissue`
                Tissue to be converted.
            id : `IntIdGenerator`
                Generator used to transform wv_edge_id to id.
        :rtype: `IOTissue`
        :return: Conversion result (cropped).
        """
        r = IOTissue()

        cell_walls = IOTissueProperty(0)
        wall_edges = IOTissueProperty(1)
        edge_empty = IOTissueProperty(2)
        geometry = IOTissueProperty(2)
        for i in wt.cells():
            cell_walls[ i ] = map( lambda x : id.id( wt.wv_edge_id(x)) , wt.cell2wvs_edges( i ) )
        #print "cw", cell_walls, id._object2id
        #raw_input()
        for i in wt.wv_edges():
            wall_edges[ id.id( i ) ] = [ i[ 0 ], i[ 1 ] ]
        #print wall_edges
        for i in wt.wvs():
            edge_empty[ i ] = []
        for i in wt.wvs():
            geometry[ i ] = Point( i )
        r.scale_relations.append(cell_walls)
        r.scale_relations.append(wall_edges)
        r.scale_relations.append(edge_empty)
        r.geometry=geometry
        return r


def WalledTissue2IOWallPropertyList( wt=None, id=None ):
	"""<Short description of the function functionality.>
	
	<Long description of the function functionality.>
	
	:parameters:
	    arg1 : `T`
		<Description of `arg1` meaning>
	:rtype: `T`
	:return: <Description of ``return_object`` meaning>
	:raise Exception: <Description of situation raising `Exception`>
	"""
	l ={}
	for i in wt.const.wv_edge_properties.keys(): 
		r = IOTissueProperty(1)
		r.description = i
		for j in wt.wv_edges():
			r[ id.id( j ) ] = wt.wv_edge_property( wv_edge=j, property=i )
		l[ i ] = r
	return l 


def WalledTissue2IOCellPropertyList( wt=None ):
	"""<Short description of the function functionality.>
	
	Note: we assume that 
	
	:parameters:
	    arg1 : `T`
		<Description of `arg1` meaning>
	:rtype: `T`
	:return: <Description of ``return_object`` meaning>
	:raise Exception: <Description of situation raising `Exception`>
	"""
	l = {}
	for i in wt.const.cell_properties.keys(): 
		r = IOTissueProperty(0)
		r.description = i
		for j in wt.cells():
			r[ j  ] = wt.cell_property( cell=j, property=i )
		l[ i ] = r 
	return l


def WalledTissue2IOEdgePropertyList( wt=None ):
	"""<Short description of the function functionality.>
	
	<Long description of the function functionality.>
	
	:parameters:
	    arg1 : `T`
		<Description of `arg1` meaning>
	:rtype: `T`
	:return: <Description of ``return_object`` meaning>
	:raise Exception: <Description of situation raising `Exception`>
	"""
	l = {}
	for i in wt.const.wv_properties.keys(): 
		r = IOTissueProperty(2)
		r.description = i
		for j in wt.wvs():
			r[ j  ] = wt.wv_property( wv=j, property=i )
		l[ i ] = r
	r = IOTissueProperty( 2 )
	r.description = "_positions"
	for j in wt.wvs():
		p = wt.wv_pos( j )
		r[ j  ] = (p.x, p.y, p.z)
	l[ r.description ] = r 
	return l

def WalledTissue2IOTissueProperties( wt=None ):
	"""<Short description of the function functionality.>
	
	<Long description of the function functionality.>
	
	:parameters:
	    arg1 : `T`
		<Description of `arg1` meaning>
	:rtype: `T`
	:return: <Description of ``return_object`` meaning>
	:raise Exception: <Description of situation raising `Exception`>
	"""
	l = {}
	for i in wt.const.tissue_properties.keys(): 
		if wt.has_tissue_property( property=i ):
			r = IOTissueProperty(-1)
			r.description =  i
			r[ i  ] = wt.tissue_property( property=i )
			l[ i  ] = r
	return l

"""
"""
	
    
