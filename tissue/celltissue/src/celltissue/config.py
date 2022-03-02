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
This module defines a Config object to store informations in a nice way
"""

__license__ = "Cecill-C"
__revision__ = " $Id: $ "

from xml.dom.minidom import parseString,Document

class ConfigItem (object) :
	"""Associate a value with a unit
	"""
	def __init__ (self, name, value, unit = "", info = "") :
		"""Constructor
		
		:Parameters:
		 - `name` (str) - name of this item
		 - `value` (any) - actual value
		 - `unit` (str) - string description
		    of the unit (e.g. m, m.s-1,...)
		 - `info` (str) - description of this
		    item
		"""
		self.name = name
		self.value = value
		self.unit = unit
		self.__doc__ = info

class Config (object) :
	"""Simple class to manage config files
	
	Allow to access all properties defined into a python
	file using the dot operator.
	"""
	def __init__ (self, name, items = [], info = "") :
		"""Constructor
		
		:Parameters:
		 - `name` (str) - name of this config
		 - `items` (list of :class:`ConfigItem`) - 
		    items stored in this configuration
		 - `info` (str) - description of this
		    configuration
		"""
		self.name = name
		self.elms = list(items)
		self.__doc__ = info
	
	def add_section (self, section) :
		"""Add a new section
		
		Section help to group items
		into logical entities.
		
		:Parameters:
		 - `section` (:class:`Section`) - the
		     section to add
		
		:Return: index of the section
		:Returns Type: int
		"""
		self.elms.append(section)
		return len(self.elms)-1
	
	def add_item (self, item, section = None) :
		"""Add a new item to this configuration
		
		:Parameters:
		 - `item` (:class:`ConfigItem`) - item to add
		 - `section` (int) - index of section in which
		    to add the item. Default is None, the item
		    is stored in the root of this configuration
		"""
		if section is None :#add item into the list
			self.elms.append(item)
		else :              #assume the section refers to a section
		                    #and add element to it
			self.elms[section].add_item(item)
		
		#add item into the local dict to access
		#it using the dot operator
		setattr(self,item.name,item.value)
	
	def __setattr__ (self, name, value) :
		object.__setattr__(self,name,value)
		if name not in ("name","elms","__doc__") :
			#update value in the tree too
			for elm in self.elms :
				if isinstance(elm,ConfigItem) :
					if elm.name == name :
						elm.value = value
						return
				else :
					elm.__setattr__(name,value)
	
	def __getitem__ (self, name) :
		"""Access using dict interface
		
		:Parameters:
		 - `name` (str) - name of the item to retrieve
		"""
		if name not in ("name","elms","__doc__") :
			return getattr(self,name)
	
	def __iter__ (self) :
		"""Emulation of list interface
		
		Iterate on all stored items.
		"""
		return iter(self.elms)

class ConfigFormat (object) :
	"""Simple class to help creating configuration files
	"""
	def __init__ (self, context, config = None) :
		"""Constructor
		
		:Parameters:
		 - `context` (dict) - local python env
		 - `config` (:class:`Config`) - configuration
		    in which to store elements. Default is
		    None, config will be created.
		"""
		self.context = context
		if config is None :
			self.cfg = Config("main")
		else :
			self.cfg = config
		self.current_section = None
	
	def add_section (self, title, info = "") :
		"""Add a section to the configuration
		
		The newly created section will become
		the current section in which further
		items will be added.
		
		:Parameters:
		 - `title` (str) - name of the section
		 - `info` ((str) - description of the
		                   section
		
		.. seealso:: :func:`Config.add_section`
		"""
		section = Config(title,[],info)
		self.current_section = self.cfg.add_section(section)
	
	def add_item (self, item) :
		"""Add an item to the current section
		
		:Parameters:
		 - `item` (:class:`ConfigItem`) - item to add
		
		.. seealso:: :func:`Config.add_item`
		"""
		self.cfg.add_item(item,self.current_section)
	
	def add (self, name, unit = "", info = "") :
		"""Add a new item in the current section
		
		Create the item using the provided infos
		and set the value of this item according
		to the value of the element with name `name`
		in the context provided in the constructor.
		
		:Parameters:
		 - `name` (str) - name of the item
		 - `unit` (str) - unit description
		 - `info` (str) - description of the item
		
		.. seealso:: :func:`Config.add_item`
		"""
		item = ConfigItem(name,self.context[name],unit,info)
		self.add_item(item)
	
	def config (self) :
		"""Retrieve the constructed configuration
		
		:Returns Type: :class:`Config`
		"""
		return self.cfg

class ConfigFile (object) :
	"""Read and write configuration files in xml
	"""
	def __init__ (self, config = None) :
		"""Constructor
		
		:Parameters:
		 - `config` (:class:`Config`) - configuration
		"""
		self.cfg = config
		self.current_section = None
	
	def _load_node (self, node) :
		"""Load a specific node
		"""
		if node.nodeType == Document.ELEMENT_NODE :
			name = node.nodeName
			if name == "section" :
				title = node.attributes["a_name"].value
				info = node.attributes["b_info"].value
				#save current section
				section_mem = self.current_section
				#add a new section
				self.current_section = self.cfg.add_section(Config(title,[],info))
				#fill section with all elements
				for child in node.childNodes :
					self._load_node(child)
				#pop the previous section id
				self.current_section = section_mem
			elif name == "item" :
				title = node.attributes["a_name"].value
				unit = node.attributes["b_unit"].value
				info = node.attributes["c_info"].value
				value_node, = (child for child in node.childNodes if child.nodeType == Document.ELEMENT_NODE)
				pyval = value_node.attributes["value"].value
				val = eval(pyval)
				#create item
				item = ConfigItem(title,val,unit,info)
				self.cfg.add_item(item,self.current_section)
			else :
				raise UserWarning("xml element %s not recognized" % name)
	
	def load (self, data) :
		"""Load a configuration object from
		its string representation.
		
		:Parameters:
		 - `data` (str) - xml representation
		                  of a configuration
		
		:Returns Type: None
		"""
		doc = parseString(data)
		main, = (child for child in doc.childNodes \
		         if child.nodeType == Document.ELEMENT_NODE)
		
		for node in main.childNodes :
			self._load_node(node)
	
	def read (self, data) :
		"""Create and return a configuration
		initialiased with the given xml
		representation.
		
		:Parameters:
		 - `data` (str) - xml representation
		                  of a configuration
		
		:Returns Type: :class:`Config`
		"""
		self.cfg = Config("main")
		self.load(data)
		return self.cfg
	
	def _save_node (self, obj, xmlparent) :
		"""Create and return an xmlnode
		that contains all information in item
		"""
		doc = xmlparent.ownerDocument
		if isinstance(obj,Config) :
			#section
			node = doc.createElement("section")
			node.setAttribute("a_name",obj.name)
			node.setAttribute("b_info",obj.__doc__)
			#list of items
			for item in obj :
				self._save_node(item,node)
			#add node to parent
			xmlparent.appendChild(node)
		elif isinstance(obj,ConfigItem) :
			#item
			node = doc.createElement("item")
			node.setAttribute("a_name",obj.name)
			node.setAttribute("b_unit",obj.unit)
			node.setAttribute("c_info",obj.__doc__)
			valnode = doc.createElement("value")
			if type(obj.value) == str :
				strval = "'%s'" % str(obj.value)
			else :
				strval = str(obj.value)
			valnode.setAttribute("value",strval)
			node.appendChild(valnode)
			#add node to parent
			xmlparent.appendChild(node)
		else :
			raise UserWarning ("item of type %s undefined" % str(type(obj)))
	
	def save (self) :
		"""Return a string representation
		of the configuration object.
		"""
		doc = Document()
		node = doc.createElement(self.cfg.name)
		for elm in self.cfg :
			self._save_node(elm,node)
		doc.appendChild(node)
		return doc.toprettyxml()

