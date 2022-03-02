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
This module defines functions to serialize a tissue
"""

__license__ = "Cecill-C"
__revision__ = " $Id: $ "

from os.path import splitext
from zipfile import ZipFile,ZipInfo,ZIP_DEFLATED
import pickle
from time import localtime
from openalea.celltissue.tissue import Tissue
from config import ConfigFile

class TissueFile (object) :
	"""Object used to serialize a tissue
	"""
	def __init__ (self, filename, mode = 'r') :
		"""Constructor
		
		Create a tissue file that will be stored in a file called filename.
		
		:Parameters:
		 - `filename` (str) - name of the file in which to store or read
		                      informations
		 - `mode` (str) - either 'r' to read or 'w' to write.
		
		.. note:: Do not create this object directly, use :func:`topen` instead.
		"""
		self._filename = filename
		self._mode = mode
		self._elms = {}
		if mode in ('r','a') :
			f = ZipFile(filename,'r')
			for name in f.namelist() :
				info = f.getinfo(name)
				data = f.read(name)
				self._elms[name] = (info,data)
			f.close()
	
	def close (self) :
		"""Write everything inside the file and close it
		"""
		if self._mode in ('w','a') :
			f = ZipFile(self._filename,'w')
			for name,(info,data) in self._elms.iteritems() :
				f.writestr(info,data)
			f.close()
	
	def filenames (self) :
		"""Name of all files currently in the archive
		
		Iterator on all name of files actually stored in this tissuefile object
		"""
		return self._elms.iterkeys()
	
	def read_file (self, filename) :
		"""Read a file in the archive
		
		:Parameters:
		 - `filename` (str) - name of the file to read
		
		:Return: a tuple:
		    - data contained in the file
		    - textual description of the data
		
		:Returns Type: str,str
		"""
		info,data = self._elms[filename]
		return data,info.comment
	
	def write_file (self, data, filename, description = "") :
		"""Write a file into the archive
		
		:Parameters:
		 - `data` (str) - data to write
		 - `filename` (str) - name of the file in which to store data
		 - `description` (str) - textual description of the data
		"""
		info = ZipInfo(filename)
		info.comment = description
		info.date_time = localtime()[:6]
		info.external_attr = 0644 << 16L
		info.compress_type = ZIP_DEFLATED
		self._elms[filename] = (info,data)
	
	def remove_file (self, filename) :
		"""Remove a file from the tissue archive
		
		:Parameters:
		 - `filename` (str) - name of the file to remove
		"""
		del self._elms[filename]
	
	def chmod (self, filename, mod = 0644) :
		"""Change file permissions
		
		:Parameters:
		 - `filename` (str) - name of the file whose permissions have to be
		                      modified
		 - `mod` (int) - numerical description of the permission (linux type)
		"""
		info = self._elms[filename][0]
		info.external_attr = mod << 16L
	
	def set_time (self, filename, datetime = None) :
		"""Change the time of a stored file
		
		:Parameters:
		 - `filename` (str) - name of the file whose date has to be modified
		 - `datetime` (int,int,int,int,int,int) - new associated time
		    in the form (year,month,day,hour,min,sec). Default is None,
		    the function will then use the actual localtime.
		"""
		if datetime is None :
			datetime = localtime()[:6]
		info = self._elms[filename][0]
		info.date_time = datetime
	
	def set_compression (self, filename, comp = ZIP_DEFLATED) :
		"""Set the type of compression of a file in the archive
		
		Default is ZIP_DEFLATED. Use this function if you need to change it.
		"""
		info = self._elms[filename][0]
		info.compress_type = comp
	
	########################################
	#
	#	read methods
	#
	########################################
	def read_dict (self, filename) :
		"""Read previously stored dict
		
		:Parameters:
		 - `filename` (str) - file to read
		
		:Returns: data and description
		:Returns Type: dict,str
		"""
		data,descr = self.read_file(filename)
		d = pickle.loads(data)
		return d,descr
	
	def read_property (self, property_name) :
		"""Read a previously stored property
		
		:Parameters:
		 - `property_name` (str) - name of the property to read
		
		:Returns: property and description
		:Returns Type: dict,str
		"""
		return self.read_dict("%s.tip" % property_name)
	
	def properties (self) :
		"""Iterator on the name of all properties stored in this archive.
		
		:Returns Type: iter of str
		"""
		for filename in self.filenames() :
			propname,ext = splitext(filename)
			if ext == ".tip" :
				yield propname

	def read_tissue (self) :
		"""Read the tissue structure stored in the archive
		
		:Returns: tissue and description
		:Returns Type: :class:`Tissue`,str
		"""
		t = Tissue()
		#add types
		types,descr = self.read_dict("_types.tis")
		for type_id,name in types.iteritems() :
			t.add_type(name,type_id)
		#add elements
		elements,descr = self.read_dict("_elements.tis")
		for elm_id,type_id in elements.iteritems() :
			t.add_element(type_id,elm_id)
		#add relations
		relation_descr,d = self.read_dict("_relations.tis")
		for relation_id,(relation_args,link_files,prop_files) in relation_descr.iteritems() :
			relation = t.relation(t.add_relation(relation_args[0],
			                                     relation_args[1:],
			                                     relation_id) )
			#fill relation with elements
			relations = []
			for filename in link_files :
				link,descr = self.read_dict(filename)
				relations.append(link)
			properties = []
			for filename in prop_files :
				prop,descr = self.read_dict(filename)
				properties.append(prop)
			relation.fill(relations,properties)
		return t,descr
	
	def read (self, name=None) :
		"""Magic function to read either the tissue if name is None or a
		property if name is given
		
		:Parameters:
		 - `name` (str) - if None read the tissue else read property
		
		:Returns: tissue or property, description
		:Returns Type: :class:`Tissue` or dict,str
		
		.. seealso::
		   - :func:`TissueFile.read_tissue`
		   - :func:`TissueFile.read_property`
		"""
		if name is None :
			return self.read_tissue()
		else :
			return self.read_property(name)
		def configs (self) :
		"""Iterator on the name of all configurations stored in this archive
		
		:Returns Type: iter of str
		"""
		for filename in self.filenames() :
			propname,ext = splitext(filename)
			if ext == ".xml" :
				yield propname

	def read_config (self, config_name) :
		"""Read a configuration stored in this archive
		
		:Parameters:
		 - `config_name` (str) - name of the configuration to read
		
		:Returns Type: :class:`Config`
		"""
		filename = "%s.xml" % config_name
		data,descr = self.read_file(filename)
		cfg_file = ConfigFile()
		return cfg_file.read(data)
	
	def external_files (self) :
		"""Iterator on the name of all external files stored in this archive
		
		External file means that the file is:
		  - not a tissue,
		  - not a property,
		  - not a config file.
		
		:Returns Type: iter of str
		"""
		for filename in self.filenames() :
			propname,ext = splitext(filename)
			if ext not in (".tis",".tip",".xml") :
				yield filename
	
	########################################
	#
	#	write methods
	#
	########################################
	def write_dict (self, d, filename, description="") :
		"""Store a dictionary in the archive
		
		:Parameters:
		 - `d` (dict) - the dictionary that will be pickled
		 - `filename` (str) - name of the file to use to later retrieve this info
		 - `description` (str) - textual description of the data
		"""
		data = pickle.dumps(d)
		self.write_file(data,filename,description)
	
	def write_property (self, prop, property_name, description="") :
		"""Store a property in the archive
		
		:Parameters:
		 - `prop` (dict) - the property that will be pickled
		 - `property_name` (str) - name of the file to use to later retrieve this info
		 - `description` (str) - textual description of the property
		"""
		self.write_dict(prop,"%s.tip" % property_name,description)
	
	def write_tissue (self, tissue) :
		"""Store a tissue in the archive
		
		Only one tissue can be stored, so there is no need to provide a name to
		later retrieve the tissue.
		
		:Parameters:
		 - `tissue` (:class:`Tissue`) - tissue to store
		"""
		types = dict( (type_id,tissue.type_name(type_id)) for type_id in tissue.types() )
		self.write_dict(types,"_types.tis","name of element types")
		elements = dict( (elm_id,tissue.type(elm_id)) for elm_id in tissue.elements() )
		self.write_dict(elements,"_elements.tis","elements and their types")
		relation_descr = {}
		for relation_id in tissue.relations() :
			relation = tissue.relation(relation_id)
			relations,properties = relation.reduce()
			link_files = []
			for ind,rel in enumerate(relations) :
				filename = "_rel%d_link%d.tis" % (relation_id,ind)
				self.write_dict(rel,
				                filename,
				                "see file _relations.tis for a description of this relation")
				link_files.append(filename)
			prop_files = []
			for ind,prop in enumerate(properties) :
				filename = "_rel%d_prop%d.tis" % (relation_id,ind)
				self.write_dict(prop,
				                filename,
				                "see file _relations.tis for a description of this relation")
				prop_files.append(filename)
			relation_descr[relation_id]=(relation.description(),link_files,prop_files)
		self.write_dict(relation_descr,
		                "_relations.tis",
		                "description of the relations between elements")
	
	def write (self, obj, name=None, description="") :
		"""Magic function to store either a tissue or a property in the archive
		
		:Parameters:
		 - `obj` (:class:`Tissue` or dict) - object to store
		 - `name` (str) - name to use to store the object
		                if None, assume obj is a tissue
		                else assume obj is a property
		 - `description` (str) - textual description of the object
		
		.. seealso::
		  - :func:`TissueFile.write_tissue`
		  - :func:`TissueFile.write_property`
		"""
		if name is None :
			self.write_tissue(obj)
		else :
			self.write_property(obj,name,description)
	
	def write_config (self, config, config_name) :
		"""Store a configuration in the archive
		
		:Parameters:
		 - `config` (:class:Config) - configuration to store
		 - `config_name` (str) - name to use to retrieve the configuration later
		"""
		filename = "%s.xml" % config_name
		cfg_file = ConfigFile(config)
		self.write_file(cfg_file.save(),filename,"config file")

def topen (filename, mode='r') :
	"""Open a tissue file
	
	Store or read informations in a file depending on the mode.
	
	:Parameters:
	 - `filename` (str) - name of the file
	 - `mode` (str) - either 'r' to read 'w' to store informations or 'a' to
	                  append informations in an already existing tissue
	
	:Returns Type: :class:`TissueFile`
	
	.. note:: Rather use this instead of the constructor of :class:`TissueFile`
	"""
	return TissueFile(filename,mode)


