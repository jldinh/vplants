# -*- python -*-
#
#       celltissue: main tissue object and functions to use it
#
#       Copyright 2006 INRIA - CIRAD - INRA  
#
#       File author(s): Jerome Chopard <jerome.chopard@sophia.inria.fr>
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
# 
#       OpenAlea WebSite : http://openalea.gforge.inria.fr
#

__doc__ = """
This module defines the main Tissue object
"""

__license__ = "Cecill-C"
__revision__ = " $Id: $ "

from openalea.container import IdDict
from relation import GraphRelation,RelationRelation,MeshRelation

relation_type_def={GraphRelation.name:GraphRelation,
                   RelationRelation.name:RelationRelation,
                   MeshRelation.name:MeshRelation}

class TissueError (Exception) :
	"""Base class of all tissue exceptions
	"""

class InvalidElement (TissueError,KeyError) :
	"""Raised when a wrong element id has been provided
	"""

class InvalidElementType (TissueError,KeyError) :
	"""Raised when a wrong element type id has been provided
	"""

class InvalidRelation (TissueError,KeyError) :
	"""Raised when a wrong relation id has been provided
	"""

class Tissue (object) :
	"""Base class for all tissues
	
	A tissue is a collection of elements
	and a set of links between these elements.
	
	:Examples:
	  >>> t = Tissue()
	  >>> CELL = t.add_type("cell")
	  >>> WALL = t.add_type("wall")
	  >>> gid = t.add_relation("graph",(CELL,WALL) )
	"""
	def __init__ (self, idgenerator = "max") :
		"""Constructor
		
		:Parameters:
		 - `idgenerator` (str) - specify the type of 
		    generator to use to later add new elements 
		    in the tissue:
		         - 'set' use a set of empty ids
		         - 'list' use a list of empty ids
		         - 'max' always increase the ids
		
		.. seealso:: :class:`openalea.container.IdDict`
		   to better understand `idgenerator`
		"""
		self._type_name = IdDict()
		self._element_type = IdDict(idgenerator = idgenerator)
		self._relation_object = IdDict()
		self._type_relation = {}
	#################################################
	#
	#		ITissue
	#
	#################################################
	def _elements (self, type_id) :
		for elm_id,elm_type in self._element_type.iteritems() :
			if elm_type == type_id :
				yield elm_id
	
	def elements (self, type_id=None) :
		"""Iterator on all elements of tissue
		with a given type.
		
		if type_id is None, iterate on all elements
		whatever their type.
		
		:Parameters:
		 - `type_id` (type_id) - type of elements
		                            to iterate on
		
		:Returns Type: iter of elm_id
		
		.. note:: `type_id` is of the same type
		   than returned by :func:`Tissue.add_type`
		"""
		if type_id is None :
			return iter(self._element_type)
		else :
			return self._elements(type_id)
	
	def nb_elements (self, type_id=None) :
		"""Number of elements of the given type
		
		Total number of elements in the tissue 
		if `type_id` is None.
		
		:Parameters:
		 - `type_id` (type_id) - type of elements
		                     to take into account
		
		:Returns Type: int
		
		.. note:: `type_id` is of the same type
		   than returned by :func:`Tissue.add_type`
		"""
		if type_id is None :
			return len(self._element_type)
		else :
			nb = 0
			for elm_id,elm_type in self._element_type.iteritems() :
				if elm_type == type_id :
					nb += 1
			return nb
	
	def type (self, elm_id) :
		"""Retrieve the type_id of the provided element
		
		:Parameters:
		 - `elm_id` (elm_id) - id of element whose type
		                       is unknown
		
		:Returns Type: type_id
		
		.. note:: `type_id` is of the same type
		   than returned by :func:`Tissue.add_type`
		"""
		try :
			return self._element_type[elm_id]
		except KeyError :
			raise InvalidElement(elm_id)
	
	def type_name (self, type_id) :
		"""Retrieve the provided name for this type
		
		:Parameters:
		 - `type_id` (type_id) - type of elements
		
		:Returns Type: str
		
		.. note:: `type_id` is of the same type
		   than returned by :func:`Tissue.add_type`
		"""
		try :
			return self._type_name[type_id]
		except KeyError :
			raise InvalidElementType(type_id)
	
	def set_type_name (self, type_id, name) :
		"""Modify the name of a given type
		
		:Parameters:
		 - `type_id` (type_id) - type of elements
		 - `name` (str) - new name for the type
		
		.. note:: `type_id` is of the same type
		   than returned by :func:`Tissue.add_type`
		"""
		try :
			self._type_name[type_id] = name
		except KeyError :
			raise InvalidElementType(type_id)
	
	def types (self) :
		"""Iterate on all types in this tissue
		
		:Returns Type : iter of type_id
		
		.. note:: `type_id` is of the same type
		   than returned by :func:`Tissue.add_type`
		"""
		return iter(self._type_name)
	
	def relation (self, relation_id) :
		"""Retrieve a relation maintained
		by this tissue
		
		:Parameters:
		 - `relation_id` (relation_id) - id of
		     the relation you want to retrieve
		     a reference on.
		
		:Returns Type: :class:`Relation`
		
		.. note:: `relation_id` is of the same type
		   than returned by :func:`Tissue.add_relation`
		"""
		try :
			return self._relation_object[relation_id]
		except KeyError :
			raise InvalidRelation(relation_id)
	
	def relations (self, type_id=None) :
		"""Iterate on all relations involving the given type
		
		if `type_id` is None, iterate on all
		relations maintained by the tissue.
		
		:Parameters:
		 - `type_id` (type_id) - type of elements
		    that must be involved in the relation
		
		:Returns Type: iter of relation_id
		
		.. note::
		 - `type_id` is of the same type
		   than returned by :func:`Tissue.add_type`
		 - `relation_id` is of the same type
		   than returned by :func:`Tissue.add_relation`
		"""
		if type_id is None :
			return iter(self._relation_object)
		else :
			try :
				return iter(self._type_relation[type_id])
			except KeyError :
				raise InvalidElementType(type_id)

	def nb_relations (self, type_id=None) :
		"""Number of relation involving the given type
		
		if `type_id` is None, return the total
		number of relations maintained by the tissue.
		
		:Parameters:
		 - `type_id` (type_id) - type of elements
		    that must be involved in the relation
		
		:Returns Type: int
		
		.. note:: `type_id` is of the same type
		   than returned by :func:`Tissue.add_type`
		"""
		if type_id is None :
			return len(self._relation_object)
		else  :
			try :
				return len(self._type_relation[type_id])
			except KeyError :
				raise InvalidElementType(type_id)
	###################################################
	#
	#		IMutableTissue
	#
	###################################################
	def add_type (self, name="elm", type_id=None) :
		"""Add a new type of elements in the tissue
		
		:Parameters:
		 - `name` (str) - provide a textual name
		             for this type (default is "elm")
		 - `type_id` (type_id) - use this id to store
		         the new type. If None (default), the
		         function will create a new id.
		
		:Return: id used to store the new type
		:Returns Type: type_id
		"""
		type_id = self._type_name.add(name,type_id)
		self._type_relation[type_id] = set()
		return type_id
	
	def add_relation (self, relation_type="graph",
	                        involved_types=[],
	                        relation_id=None) :
		"""Add a relation between different type of elements
		
		:Parameters:
		 - `relation_type` (str) - a textual description
		        of the relation:
		            - 'graph' for a directed graph
		            - 'mesh' for a topomesh
		            - 'relation' for a bipartite graph
		 - `involved_types` (list of type_id) - list the type
		      of elements that will be involved in the relation.
		      If the list contains None, a dummy type will be
		      created to be used in this relation.
		 - `relation_id` (relation_id) - provide an id to use
		      to store the relation. If None (default), an id
		      will be created by the function.
		
		:Return: id used to store the relation
		:Returns Type: relation_id
		
		:Examples:
		  >>> t = Tissue()
		  >>> CELL = t.add_type("cell")
		  >>> WALL = t.add_type("wall")
		  >>> gid = t.add_relation("graph",(CELL,WALL) )
		
		  >>> t = Tissue()
		  >>> CELL = t.add_type("cell")
		  >>> gid = t.add_relation("graph",(CELL,None) )
		"""
		#create new type if None is provided
		type_used = list(type_used)
		for ind,type_id in enumerate(type_used) :
			if type_id is None :
				type_used[ind] = self.add_type("unknown")
		
		#create relation object
		try :
			Relation = relation_type_def[relation_type]
		except KeyError :
			raise InvalidRelation("%s unkown, available relation are : %s" \
			       % (str(relation_type),
			          str(relation_type_def.keys() ) ) )
		relation = Relation(self,
		                    tuple(type_used),
		                    'max')
		
		#add it to the tissue
		relation_id = self._relation_object.add(relation,relation_id)
		for type_id in type_used :
			self._type_relation[type_id].add(relation_id)
			#update of the relation with elements
			#already in the tissue
			for elm_id in self.elements(type_id) :
				relation.add_element(type_id,elm_id)
		
		#return
		return relation_id
	
	def add_element (self, type_id, elm_id=None, safe=True) :
		"""Add a new element of the given type in the tissue
		
		:Parameters:
		 - `type_id` (type_id) - type of element to add
		 - `elm_id` (elm_id) - id to use to store the
		    element. If None (default), the function
		    will create a new id
		 - `safe` (bool) - if False, allow to overwrite
		          an existing element else raise an
		          InvalidElement if the provided elm_id
		          already exists.
		
		:Return: id used to store the element
		:Returns Type: elm_id
		
		.. note:: `type_id` is of the same type
		   than returned by :func:`Tissue.add_type`
		"""
		try :
			elm_id = self._element_type.add(type_id,elm_id)
		except KeyError :
			if safe :
				raise InvalidElement(elm_id)
			else :
				return elm_id
		for relation_id in self.relations(type_id) :
			self.relation(relation_id).add_element(type_id,elm_id)
		return elm_id
	
	def remove_element (self, elm_id) :
		"""Remove the given element and all links
		in all relations that points to this element
		
		:Parameters:
		 - `elm_id` (elm_id) - id of element to remove
		
		.. note:: `elm_id` is of the same type
		   than returned by :func:`Tissue.add_element`
		"""
		type_id = self.type(elm_id)
		#remove this element from all
		#relation it is involved in
		for relation_id in self.relations(type_id) :
			self.relation(relation_id).remove_element(type_id,elm_id)
		#remove the element
		del self._element_type[elm_id]
	
	def clear (self) :
		"""Clear all elements and relations in the tissue
		"""
		self._type_name.clear()
		self._element_type.clear()
		self._relation_object.clear()
		self._type_relation.clear()

