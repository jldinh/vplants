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
"""
Defines a database to store tissue and properties
"""

__license__ = "Cecill-C"
__revision__ = " $Id: $ "

from openalea.container import Quantity
from serial import topen

class TissueDB (object) :
	"""A simple container to maintain a tissue with a set
	of properties.
	"""
	
	def __init__ (self) :
		"""Constructor
		
		Construct a new empty TissueDB
		
		:Parameters: None
		"""
		self._tissue = None
		self._property = {}
		self._descr = {}
		self._config = {}
		self._external = {}
	
	############################################
	#
	#	simple accessors
	#
	############################################
	def tissue (self) :
		"""Access to raw tissue structure
		
		:Returns Type: :class:`Tissue`
		"""
		return self._tissue
	
	def set_tissue (self, tissue) :
		"""Set the tissue in this db
		
		:Parameters:
		 - `tissue` (:class:`Tissue`)
		"""
		self._tissue = tissue
	
	def properties (self) :
		"""Iterate on all property name
		
		:Returns Type: iter of str
		"""
		return self._property.iterkeys()
	
	def get_property (self, propname) :
		"""Access to a given property
		
		:Parameters:
		 - `propname` (str) - name of the property
		                      to retrieve
		
		:Returns Type: dict
		"""
		return self._property[propname]
	
	def set_property (self, propname, prop) :
		"""Set the given property
		
		:Parameters:
		 - `propname` (str) - name used to store
		                      the property
		 - `prop` (dict) - property to store
		"""
		self._property[propname] = prop
	
	def description (self, propname) :
		"""Retrieve the description associated
		to a given property.
		
		:Parameters:
		 - `propname` (str) - name of the property
		             which description to retrieve
		
		:Returns Type: str
		"""
		return self._descr[propname]
	
	def set_description (self, propname, descr) :
		"""Set the description associated
		to a given property.
		
		:Parameters:
		 - `propname` (str) - name of the property
		 - `descr` (str) - textual description
		"""
		self._descr[propname] = descr

	def configurations (self) :
		"""Iterates on configs. 
		Finds cfgname from config_names and passes it to get_config.

		:Returns Type: :class:`Config`
		"""
		return self._config.iterkeys()
	
	def config_names (self) :
		"""Lists all configuration names
		
		:Returns Type: iter of str
		"""
		return self._config.keys()
	
	def get_config (self, cfgname) :
		"""Access to a given configuration
		
		:Parameters:
		 - `cfgname` (str) - name of the configuration
		
		:Returns Type: :class:`Config`
		"""
		return self._config[cfgname]
	
	def set_config (self, cfgname, cfg) :
		"""Store a configuration in this db
		
		:Parameters:
		 - `cfgname` (str) - name used to store
		                      the configuration
		 - `cfg` (:class:`Config`) - configuration
		                      to store
		"""
		self._config[cfgname] = cfg
	
	def get_external_data (self, name) :
		"""Access to data in external format
		
		:Parameters:
		 - `name` (str) - name used to store the data
		
		:Returns Type: any
		"""
		return self._external[name]
	
	def set_external_data (self, name, data) :
		"""Store any data in the tissue
		
		:Parameters:
		 - `name` (str) - name used to store the data
		 - `data` (any) - data to store
		"""
		self._external[name] = data
	############################################
	#
	#	topology accessors
	#
	############################################
	def get_topology (self, toponame, cfg = "config") :
		"""Access to a given topology
		
		:Parameters:
		 - `toponame` (str) -name of the topology
		     as defined in the configuration file
		 - `cfg` (str) - name of the configuration
		                 file to use
		
		:Returns Type: :class:Relation
		"""
		return self._tissue.relation(self._config[cfg][toponame])
	
	############################################
	#
	#	inout
	#
	############################################
	def read (self, filename) :
		"""Fill this db with info from filename
		
		:Parameters:
		 - `filename` (str) - path to the file
		      in which informations are stored
		"""
		f = topen(filename,'r')
		#tissue
		self._tissue,descr = f.read()
		#properties
		self._property.clear()
		for propname in f.properties() :
			self._property[propname],self._descr[propname] = f.read(propname)
		#configs
		self._config.clear()
		for cfgname in f.configs() :
			self._config[cfgname] = f.read_config(cfgname)
		#external data
		self._external.clear()
		for filename in f.external_files() :
			self._external[filename],descr = f.read_file(filename)
		#close
		f.close()
	
	def write (self, filename) :
		"""Write this db into a file.
		
		:Parameters:
		 - `filename` (str) - path to the file
		    in which informations will be stored
		"""
		f = topen(filename,'w')
		#tissue
		f.write(self._tissue)
		print 'properties',
		for propname,prop in self._property.iteritems() :
			print propname,
			f.write(prop,propname,self.description(propname) )
		print '\nconfigs',
		for cfgname,cfg in self._config.iteritems() :
			print cfgname
			f.write_config(cfg,cfgname)
		#external data
		for filename,data in self._external.iteritems() :
			f.write_file(data,filename)
		#close
		f.close()
	
	############################################
	#
	#	infos
	#
	############################################
	def _type_name (self, obj) :
		"""Internal function used to retrieve
		a nice type name for this obj.
		"""
		type_name = str(type(obj) )
		full_name = type_name.split("'")[1]
		name = full_name.split(".")[-1]
		return name
	
	def info (self) :
		"""Return infos on a this tissuedb
		
		:Returns Type: str
		"""
		msg =  "Tissue DB\n"
		
		#tissue existence
		if self.tissue() is None :
			msg += "no tissue\n"
		else :
			tissue = self.tissue()
			#tissue infos
			msg += "Tissue\n"
			msg += "------------------------------------------------------------\n"
			msg += "types:\n"
			for type_id in tissue.types() :
				msg += "    - %s (%d)\n" % (tissue.type_name(type_id),type_id)
			msg += "relations:\n"
			for relation_id in tissue.relations() :
				relation = tissue.relation(relation_id)
				rtype_name = self._type_name(relation)
				inv_elms = ",".join(tissue.type_name(type_id) 
					                for type_id in relation.involved_elements() )
				msg += "    - %s id %d involving elements (%s)\n" \
				       % (rtype_name,relation_id,inv_elms)
			#config infos
			msg += "------------------------------------------------------------\n"
			msg += "Config\n"
			msg += "------------------------------------------------------------\n"
			for name,cfg in self._config.iteritems() :
				msg += "%s" % name
				for i in dir(cfg) :
					if not i.startswith("_") \
					   and i not in ("elms","name","add_item","add_section") :
						msg += "\t%s = %s\n" % (i,str(cfg[i]) )
			#properties
			msg += "------------------------------------------------------------\n"
			msg += "Properties\n"
			msg += "------------------------------------------------------------\n"
			for name,prop in self._property.iteritems() :
				#defined on which elements
				try :
					elm_types = set(tissue.type(elmid) for elmid in prop)
					msg += "%s: %d elms defined on elements of type %s\n" % (name,
						                          len(prop),
						                          ",".join("%d(%s)" % (typ,\
						                               tissue.type_name(typ) )\
						                           for typ in elm_types) )
				except TypeError :
					msg += "%s: %d elms\n" % (name,len(prop) )
				
				#unit
				if isinstance(prop,Quantity) :
					msg += "    unit: %s\n" % prop.unit()
				
				#description
				try :
					descr = self.description(name)
					if descr == "" :
						msg += "    no description\n"
					else :
						msg += "    descr: %s\n" % descr
				except KeyError :
					msg += "    no description\n"
				msg += "\n"
		
			#properties
			msg += "------------------------------------------------------------\n"
			msg += "External data\n"
			msg += "------------------------------------------------------------\n"
			for name,data in self._external.iteritems() :
				msg += "%s with a length of %d\n" % (name,len(data) )
		
		return msg

