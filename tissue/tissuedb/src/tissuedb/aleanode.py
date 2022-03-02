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
functions to directly access the elements in openalea
"""

__license__= "Cecill-C"
__revision__=" $Id: $ "

try :
	from config import dbname,user
except ImportError :
	print "you must first create a database using admin.create"

from PyQt4.QtGui import QApplication
from openalea.core.pkgmanager import PackageManager,UnknownPackageError
from openalea.core.compositenode import CompositeNode, CompositeNodeFactory
from openalea.core.interface import IFileStr
from openalea.core.alea import start_qt
from database import get_filename,get_process_filename

###########################################
#
#	manage processes as composite nodes in the openalea
#
###########################################
def get_package (local = True) :
	"""
	retrieve the openalea package
	"""
	#find tissue.process package
	pkgmanager = PackageManager()
	if local :
		pkgmanager.init(get_process_filename(""),verbose=False)
	else :
		pkgmanager.init(verbose=False)
	try :
		return pkgmanager[dbname]
	except UnknownPackageError :
		raise UserWarning("pkg not defined use admin.create first")

def create_process_node (procname, author) :
	"""
	create a new process script
	"""
	#enter process in openalea as a composite node
	pkg = get_package()
	if procname in pkg :
		raise KeyError("already existing procname : %s" % procname)
	#create process composite node
	inputs = (dict(name="input_file", interface=IFileStr,),
				dict(name="output_file", interface=IFileStr,),)
	fac = CompositeNodeFactory(procname, inputs = inputs)
	pkg.add_factory(fac)
	pkg.write()

def remove_process_node (procname) :
	"""
	remove a process script
	"""
	#remove process from openalea
	pkg = get_package()
	try :
		del pkg[procname]
	except KeyError :
		raise
	pkg.write()

def set_process_editable (procname, editable) :
	"""
	add a warning node to process that must not be
	modified since used inside the database
	"""
	pkg = get_package()
	try :
		node = pkg[procname]
	except KeyError :
		raise
	warning_ind = None
	for k,(pkgname,nodename) in node.elt_factory.items() :
		if nodename == "DBwarning" and pkgname == "tissuedb.script" :
			warning_ind = k
	if editable :
		if warning_ind is None :
			print "already editable"
		else :
			del node.elt_factory[k]
	else :
		if warning_ind is None :
			keys = node.elt_factory.keys()
			if len(keys) == 0 :
				k = 2
			else :
				keys.sort()
				k = keys[-1] + 1
			#register elt_factory
			node.elt_factory[k] = ("tissuedb.script","DBwarning")
			#register elt_data
			node.elt_data[k] =  {'lazy': True,
								'hide': True,
								'port_hide_changed': set([]),
								'priority': 0,
								'caption': 'DBWarning',
								'user_application': None,
								'posx': 10,
								'posy': 10,
								'block': False}
			#register elt_value
			node.elt_value[k] = []
		else :
			print "already protected"
	#write
	pkg.write()

###########################################
#
#	evaluate process
#
###########################################
def execute_process (procname, inputs, gui) :#TODO gestion gui
	"""
	execute the given procname with the given arguments
	procname: the alea name of the given process
	args: a dict of {k:val}
	gui: tells wether you want to use the associated gui or not
	"""
	pkg = get_package(local=False)
	factory = pkg[procname]
	node = factory.instantiate()
	if (inputs):
		for k, v in inputs.iteritems():
			try:
				node.set_input(k, v)
			except KeyError, e:
				print "Unknown input %s" % (k, )
				raise e
	print "node",procname,node
	print "inputs",inputs
	if gui :
		qapp = QApplication.instance()
		if qapp is None :
			qapp = QApplication([])
	node.eval()
	if gui :
		qapp.exec_()
	print node.outputs


