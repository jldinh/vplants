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
functions to create the database
"""

__license__= "Cecill-C"
__revision__=" $Id: $ "

from os import getcwd,makedirs
from os.path import dirname,expanduser,isabs,isdir,join,normpath
from openalea.core.package import UserPackage
from openalea.core.pkgmanager import PackageManager,UnknownPackageError
import MySQLdb as db

def create_repository (repository_path) :
	"""
	create file repository
	"""
	#repository
	repository_path = expanduser(repository_path)
	if not isabs(repository_path) :
		repository_path = join(getcwd(),repository_path)
	repository_path = normpath(repository_path)
	try :
		makedirs(repository_path)
	except OSError :
		print "%s already exists" % repository_path
	#files
	files_directory = join(repository_path,"files")
	try :
		makedirs(files_directory)
	except OSError :
		print "%s already exists" % files_directory
	#processes
	processes_directory = join(repository_path,"processes")
	try :
		makedirs(processes_directory)
	except OSError :
		print "%s already exists" % processes_directory
	#zones
	zones_directory = join(repository_path,"zones")
	try :
		makedirs(zones_directory)
	except OSError :
		print "%s already exists" % zones_directory
	#patterns
	patterns_directory = join(repository_path,"patterns")
	try :
		makedirs(patterns_directory)
	except OSError :
		print "%s already exists" % patterns_directory
	#return
	return files_directory,processes_directory,zones_directory,patterns_directory 

def create_db (dbname, user, passwd, root = "root", rootpwd = "root") :
	"""
	create a database
	create the corresponding user with the given passwd
	store associated file in path/dbname
	"""
	#connection to database
	con = db.connect(user = root, passwd = rootpwd)
	cursor = con.cursor()
	#create user
	try :
		query = "create user '%s'@'localhost' identified by '%s'" % (user,passwd)
		cursor.execute(query)
	except db.OperationalError :
		print "already registered user"
	#create db
	try :
		query = "create database %s CHARACTER SET utf8" % dbname
		cursor.execute(query)
	except db.ProgrammingError :
		print "already existing database"
	#associate user to db
	query = "grant all on %s.* to '%s'@'localhost'" % (dbname,user)
	cursor.execute(query)
	#create tables
	cursor.execute("use %s" % dbname)
	try : #files
		query = """
		CREATE TABLE files (name VARCHAR(255) UNIQUE PRIMARY KEY,
				   author VARCHAR(255),
				   date DATETIME,
				   original VARCHAR(255),
				   lastmodif INT NOT NULL DEFAULT 0,
				   process VARCHAR(255),
				   args TEXT)"""
		cursor.execute(query)
	except db.OperationalError :
		print "table files already exist"
	
	try : #processes
		query = """
		CREATE TABLE processes (name VARCHAR(255) UNIQUE PRIMARY KEY,
				   author VARCHAR(255),
				   date DATETIME,
				   description TEXT,
				   gui BOOL DEFAULT FALSE)"""
		cursor.execute(query)
	except db.OperationalError :
		print "table processes already exist"
	
	try : #zones
		query = """
		CREATE TABLE zones (name VARCHAR(255) UNIQUE PRIMARY KEY,
				   author VARCHAR(255),
				   date DATETIME,
				   description TEXT)"""
		cursor.execute(query)
	except db.OperationalError :
		print "table zones already exist"
	
	try : #patterns
		query = """
		CREATE TABLE patterns (name VARCHAR(255) UNIQUE PRIMARY KEY,
				   author VARCHAR(255),
				   date DATETIME,
				   description TEXT,
				   zone VARCHAR(255))"""
		cursor.execute(query)
	except db.OperationalError :
		print "table patterns already exist"

def create_package (dbname, user, processes_directory) :
	"""
	create the tissue.process package
	"""
	pkgmanager = PackageManager()
	pkgmanager.init(processes_directory)
	try :
		pkg = pkgmanager[dbname]
		print "package already exist"
	except UnknownPackageError :
		metainfo = dict(
			version = '0.0.1',
			license = 'Cecill-C',
			authors = user,
			institutes = 'INRIA/CIRAD',
			description = 'pkg used to register processes',
			url = 'http://openalea.gforge.inria.fr',
			icon = '',
			alias = [],
			)
		pkg = UserPackage(dbname,metainfo,processes_directory)
		pkg.write()

def edit_config_file (dbname,user,passwd,files_directory,processes_directory,zones_directory,patterns_directory) :
	#edit config file
	rep = dirname(__file__)
	f = open(join(rep,"config.py"),'w')
	f.write("""# -*- python -*-
#
#       %s: package to manage database of scripted files
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

__doc__=\"\"\"
registered path for files
\"\"\"

__license__= "Cecill-C"
__revision__=" $Id: $ "

""" % dbname)
	f.write("dbname = '%s'\n" % dbname)
	f.write("user = '%s'\n" % user)
	f.write("passwd = '%s'\n" % passwd)
	f.write("files_directory = '%s'\n" % files_directory)
	f.write("processes_directory = '%s'\n" % processes_directory)
	f.write("zones_directory = '%s'\n" % zones_directory)
	f.write("patterns_directory = '%s'\n" % patterns_directory)
	f.close()

def create (dbname, user, passwd, repository_path, root = "root", rootpwd = "root") :
	files_directory,processes_directory,zones_directory,patterns_directory = create_repository(repository_path)
	create_db(dbname,user,passwd,root,rootpwd)
	create_package(dbname,user,processes_directory)
	edit_config_file(dbname,user,passwd,files_directory,processes_directory,zones_directory,patterns_directory)

