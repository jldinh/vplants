# -*- python -*-
#
#       tissuedb: package to manage database of scripted files
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

__doc__="""
functions to modify files in the database
"""

__license__= "Cecill-C"
__revision__=" $Id: $ "

try :
	from config import user,dbname
except ImportError :
	print "you must first create a database using admin.create"

from os import remove
from shutil import copy
from pickle import dumps,loads
from time import strftime
import database as db
from aleanode import create_process_node,remove_process_node,set_process_editable,\
					execute_process

def current_date () :
	"""
	return the current date as a string
	'Y/m/d H:M:S'
	"""
	return strftime("%Y/%m/%d %H:%M:%S")
######################################
#
#	edition
#
######################################
def add_file (name, author = None, date = None, path = None, cursor = None) :
	"""
	add a file in the database
	and copy it into the right directory
	"""
	if author is None :
		author = user
	if date is None :
		date = current_date()
	#database
	if cursor is None :
		cursor = db.connect()
	db.add_file(cursor,name,author,date)
	#copy the file
	if path is not None :
		copy(path,db.get_filename(name))

def remove_file (name, cursor = None) :
	"""
	remove a file from the database
	and from the file directory
	"""
	#database
	if cursor is None :
		cursor = db.connect()
	#test wether the file is used
	#as an original by another file
	if db.is_file_used(cursor,name) :
		raise UserWarning("File '%s' is used, unable to remove" % name)
	db.remove_file(cursor,name)
	#remove the file
	try :
		remove(db.get_filename(name))
	except OSError :
		pass

def add_process (name, author = None, date = None, cursor = None) :#TODO gestion gui
	"""
	add a process in the database
	and create the corresponding openalea node
	"""
	if author is None :
		author = user
	if date is None :
		date = current_date()
	#database
	if cursor is None :
		cursor = db.connect()
	db.add_process(cursor,name,author,date)
	#openalea
	create_process_node(name,author)

def remove_process (name, cursor = None) :
	"""
	remove a process from the database
	and remove the corresponding openalea node
	"""
	#database
	if cursor is None :
		cursor = db.connect()
	#test wether the process is still used
	if db.is_process_used (cursor,name) :
		raise UserWarning("process '%s' still used, unable to remove" % name)
	db.remove_process(cursor,name)
	#openalea
	remove_process_node(name)

def associate_process (name, original, procname, args, cursor = None) :
	"""
	associate a process to generate this file
	"""
	if cursor is None :
		cursor = db.connect()
	args_str = dumps(args)
	db.associate_process(cursor,name,original,procname,args_str)
	set_process_editable(procname,False)

def add_zone (name, author = None, date = None, path = None, cursor = None) :
	"""
	add a new zone definition file
	"""
	if author is None :
		author = user
	if date is None :
		date = current_date()
	#database
	if cursor is None :
		cursor = db.connect()
	db.add_zone(cursor,name,author,date)
	#copy the file
	if path is not None :
		copy(path,db.get_zone_filename("%s.py" % name))

def remove_zone (name, cursor = None) :
	"""
	remove a zone from the database
	"""
	#database
	if cursor is None :
		cursor = db.connect()
	#test wether the zone is used
	#as a reference by a pattern
	if db.is_zone_used(cursor,name) :
		raise UserWarning("Zone '%s' is used, unable to remove" % name)
	db.remove_zone(cursor,name)
	#remove the file
	try :
		remove(db.get_zone_filename(name))
	except OSError :
		pass

def add_pattern (name, zone, author = None, date = None, path = None, cursor = None) :
	"""
	add a new pattern definition file
	related to a given zone definition
	"""
	if author is None :
		author = user
	if date is None :
		date = current_date()
	#database
	if cursor is None :
		cursor = db.connect()
	db.add_pattern(cursor,name,zone,author,date)
	#copy the file
	if path is not None :
		copy(path,db.get_pattern_filename("%s.py" % name))

def remove_pattern (name, cursor = None) :
	"""
	remove a pattern from the database
	"""
	#database
	if cursor is None :
		cursor = db.connect()
	db.remove_pattern(cursor,name)
	#remove the file
	try :
		remove(db.get_pattern_filename(name))
	except OSError :
		pass
######################################
#
#	play processes
#
######################################
def format_arguments (args_str) :
	"""
	format argument string into a python dict
	"""
	if args_str == "" :
		return {}
	else :
		return loads(args_str)

def process (input_file, output_file, procname, args, gui = False) :
	"""
	execute the given procname with the given arguments
	on the given files
	procname: the alea name of the given process tissue.process:procname
	args: a dict of {k:val}
	gui: tells wether you want to use the associated gui or not
	"""
	args['input_file'] = input_file
	args['output_file'] = output_file
	execute_process(procname,args,gui)

def replay (name, cursor = None) :
	"""
	replay the process that leaded to this file
	"""
	if cursor is None :
		cursor = db.connect()
	#retrieve information on the process
	original,procname,args_str = db.associated_process(cursor,name)
	if original is None or procname is None :
		raise UserWarning("no process associated with file '%s'" % name)
	#format arguments
	args = format_arguments(args_str)
	#perform process
	process(db.get_filename(original),db.get_filename(name),procname,args,db.has_gui(cursor,procname))
	#change registered time stamp of the original
	#for further info if original is modified
	db.register_timestamp(cursor,name)

######################################
#
#	informations
#
######################################
def associated_process (name, cursor = None) :
	"""
	retrieve the process that created this file
	with the arguments used by this process
	"""
	#database
	if cursor is None :
		cursor = db.connect()
	original,procname,args_str = db.associated_process(cursor,name)
	args = format_arguments(args_str)
	return original,procname,args
	
def is_uptodate (name, cursor = None) :
	"""
	test wether a file is up to date
	by comparing the registered timestamp
	for its original with the real one
	"""
	if cursor is None :
		cursor = db.connect()
	return db.is_uptodate(cursor,name)

def associated_patterns (zone, cursor = None) :
	"""
	retrieve all the patterns that use
	this zone as a reference
	"""
	if cursor is None :
		cursor = db.connect()
	return db.associated_patterns(cursor,zone)

