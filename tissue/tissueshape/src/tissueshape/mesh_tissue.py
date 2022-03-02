# -*- python -*-
#
#       tissueshape: function used to deal with tissue geometry
#
#       Copyright 2006 INRIA - CIRAD - INRA  
#
#       File author(s): Jerome Chopard <revesansparole@gmail.com>
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
# 
#       OpenAlea WebSite : http://openalea.gforge.inria.fr
#

__doc__ = """
This module defines functions to create predefined tissues
from geometrical meshes
"""

__license__ = "Cecill-C"
__revision__ = " $Id: $ "

__all__ = ["from_mesh"
         , "add_relation_from_mesh"
         , "add_graph_from_mesh"]

from openalea.celltissue import Tissue

def from_mesh (mesh, deg_names, id_gen = 'max') :
	"""Construct a tissue from the given mesh geometry

	:Parameters:
	 - `deg_names` (list of (int,str) ) - list of names
	                associated with relevant degree of darts
	
	:Returns: (Tissue, tuple of tid) - type ids are in the
	                   order declared in `deg_names`
	
	:Examples:
	  >>> t, (CELL, WALL) = from_mesh(mesh, [(3,"cell"), (2,"wall")] )
	  >>> t.add_relation("cell to cell", CELL, CELL, WALL)
	  
	  >>> cid = t.add_element(CELL)
	  >>> msh = t.geometry(cid)
	"""
	#create tissue
	t = Tissue(id_gen)
	
	#copy mesh
	tm = t.geometry()
	
	for did in mesh.darts() :
		tm.add_dart(mesh.degree(did), did)
	
	for did in mesh.darts() :
		for bid in mesh.borders(did) :
			tm.link(did, bid)
	
	for did in mesh.darts(0) :
		tm.set_position(did, mesh.position(did) )
	
	#set elements types
	tids = []
	for deg, name in deg_names :
		tid = t.add_type(name)
		tids.append(tid)
		for did in mesh.darts(deg) :
			t.set_type(did, tid)
	
	#return
	return t, tids


def add_relation_from_mesh (t, name, left_tid, right_tid, link_tid = None) :
	"""Add a relation in the tissue between element types
	
	If link_tid is None, create a new type for links
	
	:Returns: (tid) - id of type used for links
	"""
	m = t.geometry()
	
	link_tid = t.add_type(link_name)
	rel = t.add_relation(name, left_tid, right_tid, link_tid)
	
	try :
		left_did = t.elements(left_tid).next()
		right_did = t.elements(right_tid).next()
	except StopIteration :
		raise UserWarning("no elements defined in the tissue")
	
	assert abs(m.degree(left_did) - m.degree(right_did) ) == 1
	
	if m.degree(left_did) > m.degree(right_did) :
		for did in t.elements(left_did) :
			for bid in t.borders(did) :
				rel.link(did, bid)
	else :
		for did in t.elements(left_did) :
			for rid in t.regions(did) :
				rel.link(did, rid)
	
	return link_tid


def add_graph_from_mesh (t, name, vtx_tid) :
	"""Add a graph relation in the tissue between element
	of type vtx_tid.
	
	Edges are link beween vertices that share a common
	border in the mesh.
	
	:Warning: id of type used for edge must already be
	defined in the tissue
	
	:Warning: elements that will be edges must not have more
	than two regions surrounding them
	
	:Warning" orientation of edges is not relevant
	"""
	m = t.geometry()

	try :
		vtx_did = t.elements(vtx_tid).next()
	except StopIteration :
		raise UserWarning("no elements defined in the tissue")
	
	#find edges
	edges = []
	for eid in m.darts(m.degree(vtx_did) - 1) :
		tup = tuple(m.regions(eid) )
		if len(tup) == 2 :
			edges.append( (eid, tup) )
	
	#create relation
	edge_tid = t.type(eid)
	graph = t.add_relation(name, vtx_tid, vtx_tid, edge_tid)
	
	for eid, (sid, tid) in edges :
		graph.add_edge(sid, tid, eid)









