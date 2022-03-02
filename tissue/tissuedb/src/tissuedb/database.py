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
functions to directly access the database
"""

__license__= "Cecill-C"
__revision__=" $Id: $ "

try :
	from config import dbname,user,passwd,files_directory,processes_directory,zones_directory,patterns_directory
except ImportError :
	print "you must first create a database using admin.create"

from os import path
import MySQLdb as db

class DBWarning (UserWarning) :
	def __init__ (self, elm_type, elm_name) :
		UserWarning.__init__(self,"%s '%s' not registered in the database" % (elm_type,elm_name))

class DBIntegrityWarning (UserWarning) :
	def __init__ (self, elm_type, elm_name) :
		UserWarning.__init__(self,"%s '%s' already registered in the database" % (elm_type,elm_name))
###########################################
#
#	access functions
#
###########################################
def connect () :
	"""
	connect to the database and return a cursor
	"""
	con = db.connect(user = user, passwd = passwd, db = dbname)
	return con.cursor()

def get_filename (filename) :
	"""
	return the complete filename
	"""
	return path.join(files_directory,filename)

def get_process_filename (filename) :
	"""
	return the complete filename
	"""
	return path.join(processes_directory,filename)

def get_zone_filename (filename) :
	"""
	return the complete filename
	"""
	return path.join(zones_directory,filename)

def get_pattern_filename (filename) :
	"""
	return the complete filename
	"""
	return path.join(patterns_directory,filename)
###########################################
#
#	manage processes in the database
#
###########################################
def is_process_registered (cursor, name) :
	"""
	return wether the process is in the database
	"""
	query = "SELECT COUNT(*) FROM processes WHERE name='%s'" % name
	cursor.execute(query)
	(nb,), = cursor.fetchall()
	return nb == 1

def add_process (cursor, name, author, date) :
	"""
	add a new process in the database
	using the provided cursor (obtained with a connect method)
	"""
	query = "INSERT INTO processes (name,author,date) VALUES('%s','%s','%s')" % (name,author,date)
	try :
		cursor.execute(query)
	except db.IntegrityError :
		raise DBIntegrityWarning("Process",name)

def remove_process (cursor, name) :
	"""
	remove the given process from the database
	using the provided cursor (obtained with a connect method)
	"""
	query = "DELETE FROM processes WHERE name='%s'" % name
	cursor.execute(query)
	if cursor.rowcount == 0 :
		raise DBWarning("Process",name)

def is_process_used (cursor, name) :
	"""
	test wether a given process is used
	to generate a file of the database
	"""
	query = "SELECT COUNT(*) FROM files WHERE process='%s'" % name
	cursor.execute(query)
	(nb,), = cursor.fetchall()
	return nb > 0

def has_gui (cursor, name) :
	"""
	return wether the process requires a gui
	"""
	query = "SELECT gui FROM processes WHERE name='%s'" % name
	cursor.execute(query)
	if cursor.rowcount == 0 :
		raise DBWarning("Process",name)
	(gui,), = cursor.fetchall()
	return gui == 1
###########################################
#
#	manage files in the database
#
###########################################
def is_file_registered (cursor, name) :
	"""
	return wether the file is in the database
	"""
	query = "SELECT COUNT(*) FROM files WHERE name='%s'" % name
	cursor.execute(query)
	(nb,), = cursor.fetchall()
	return nb == 1

def is_file_used (cursor, name) :
	"""
	test wether the file is used
	as an original file by another file
	"""
	query = "SELECT COUNT(*) FROM files WHERE original='%s'" % name
	cursor.execute(query)
	(nb,), = cursor.fetchall()
	return nb > 0

def add_file (cursor, name, author, date) :
	"""
	add a new file in the database
	using the provided cursor (obtained with a connect method)
	by default this file is raw data
	"""
	query = "INSERT INTO files (name,author,date) VALUES('%s','%s','%s')" % (name,author,date)
	try :
		cursor.execute(query)
	except db.IntegrityError :
		raise DBIntegrityWarning("File",name)

def remove_file (cursor, name) :
	"""
	remove the given file from the database
	using the provided cursor (obtained with a connect method)
	"""
	query = "DELETE FROM files WHERE name='%s'" % name
	cursor.execute(query)
	if cursor.rowcount == 0 :
		raise DBWarning("File",name)
	
def associated_process (cursor, name) :
	"""
	retrieve information on the process
	associated with a file
	"""
	query = "SELECT original,process,args FROM files WHERE name='%s'" % name
	cursor.execute(query)
	if cursor.rowcount == 0 :
		raise DBWarning("File",name)
	(original,procname,args), = cursor.fetchall()
	return original,procname,args

def associate_process (cursor, name, original, procname, args) :
	"""
	associate a process to generate this file
	"""
	#test wether the file exist
	if not is_file_registered(cursor,name) :
		raise DBWarning("File",name)
	#test wether the original file exist
	if not is_file_registered(cursor,original) :
		raise DBWarning("File",original)
	#test wether the process exist
	if not is_process_registered(cursor,procname) :
		raise DBWarning("Process",procname)
	#register
	query = "UPDATE files SET original='%s', process='%s', args=\"%s\" WHERE name='%s'" % (original,procname,args,name)
	cursor.execute(query)

def register_timestamp (cursor, name) :
	"""
	register the current timestamp of the original
	file that leaded to filename
	in order to be able to check if a file needs to be replayed
	"""
	#find original filename
	query = "SELECT original FROM files WHERE name='%s'" % name
	cursor.execute(query)
	if cursor.rowcount == 0 :
		raise DBWarning("File",name)
	(original,), = cursor.fetchall()
	#set new timestamp
	if original is None :
		pass
	else :
		original = get_filename(original)
		time = int(max(path.getctime(original),path.getmtime(original)))
		query = "UPDATE files SET lastmodif=%d WHERE name='%s'" % (time,name)
		cursor.execute(query)

def is_uptodate (cursor, name) :
	"""
	test wether a file is up to date
	by comparing the registered timestamp
	with the real one
	"""
	#find infos on original
	query = "SELECT original,lastmodif FROM files WHERE name='%s'" % name
	cursor.execute(query)
	if cursor.rowcount == 0 :
		raise DBWarning("File",name)
	(original,lastmodif), = cursor.fetchall()
	if original is None : #raw data always up to date
		return True
	else : #compare stored time with modification time of original
		original = get_filename(original)
		time = int(max(path.getctime(original),path.getmtime(original)))
		return time <= lastmodif
###########################################
#
#	manage patterns in the database
#
###########################################
def is_zone_registered (cursor, name) :
	"""
	test wether a zone exist or not
	"""
	query = "SELECT COUNT(*) FROM zones WHERE name='%s'" % name
	cursor.execute(query)
	(nb,), = cursor.fetchall()
	return nb == 1

def is_zone_used (cursor, name) :
	"""
	test wether a given zone is used
	as a reference by any pattern
	"""
	query = "SELECT COUNT(*) FROM patterns WHERE zone='%s'" % name
	cursor.execute(query)
	(nb,), = cursor.fetchall()
	return nb > 0

def add_zone (cursor, name, author, date) :
	"""
	add a new zone definition in the database
	"""
	query = "INSERT INTO zones (name,author,date) VALUES('%s','%s','%s')" % (name,author,date)
	try :
		cursor.execute(query)
	except db.IntegrityError :
		raise DBIntegrityWarning("Zone",name)

def remove_zone (cursor, name) :
	"""
	remove the given zone from the database
	using the provided cursor (obtained with a connect method)
	"""
	query = "DELETE FROM zones WHERE name='%s'" % name
	cursor.execute(query)
	if cursor.rowcount == 0 :
		raise DBWarning("Zone",name)

def add_pattern (cursor, name, zone, author, date) :
	"""
	add a new pattern definition in the database
	"""
	if not is_zone_registered(cursor,zone) :
		raise DBWarning("Zone",zone)
	
	query = "INSERT INTO patterns (name,zone,author,date) VALUES('%s','%s','%s','%s')" % (name,zone,author,date)
	try :
		cursor.execute(query)
	except db.IntegrityError :
		raise DBIntegrityWarning("Pattern",name)

def remove_pattern (cursor, name) :
	"""
	remove the given pattern from the database
	using the provided cursor (obtained with a connect method)
	"""
	query = "DELETE FROM patterns WHERE name='%s'" % name
	cursor.execute(query)
	if cursor.rowcount == 0 :
		raise DBWarning("Pattern",name)

def associated_patterns (cursor, zone) :
	"""
	retrieve all the patterns that use
	this zone as a reference
	"""
	query = "SELECT name FROM patterns WHERE zone='%s'" % zone
	cursor.execute(query)
	patterns = [res[0] for res in cursor.fetchall()]
	return patterns
