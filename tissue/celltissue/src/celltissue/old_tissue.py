# -*- python -*-
#
#       celltissue: compatibility module
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
This module defines functions to read old tissue files
and convert them to the new tissue objects
"""

__license__ = "Cecill-C"
__revision__ = " $Id: $ "

__all__ = ["read_old", "convert_old_tissue"]


from os.path import splitext
from pickle import loads
from zipfile import ZipFile, ZipInfo, ZIP_DEFLATED
from openalea.container import InvalidDart
from tissue import Tissue
from serial import topen


def read_data (f, name) :
	info = f.getinfo(name)
	return loads(f.read(name) ), info.comment

def read_old_mesh (f, t, descr, lfiles) :
	m = t.geometry()
	
	#create dart
	for deg, tid in enumerate(descr[1:]) :
		for eid in t.elements(tid) :
			m.add_dart(deg, eid)
	
	#make links
	for i,name in enumerate(lfiles) :
		link, descr = read_data(f, name)
		for lid, (rid, bid) in link.iteritems() :
			m.link(rid, bid)#assert unique ids in old tissues


def read_old_graph (f, t, descr, lfiles) :
	raise NotImplementedError


def read_old_relation (f, t, descr, lfiles) :
	raise NotImplementedError


def read_old (filename) :
	"""Read previous file format and retrieve tissue
	and properties
	"""
	t = Tissue()
	
	f = ZipFile(filename, 'r')
	
	#read element types
	types, descr = read_data(f, "_types.tis")
	for tid, name in types.iteritems() :
		t.add_type(name, tid)
		print tid, name
	
	#read elements
	ents, descr = read_data(f, "_elements.tis")
	for eid, tid in ents.iteritems() :
		t.add_element(tid, eid)

	#read topological relations (and hopefully geometry as well)
	rel_descr, dmy = read_data(f, "_relations.tis")

	mesh_descr = None
	for rid, (descr, lfiles, pfiles) in rel_descr.iteritems() :
		if descr[0] == 'mesh' :#store for later
			read_old_mesh(f, t, descr, lfiles)
		elif descr[0] == 'relation' :
			read_old_relation(f, t, descr, lfiles)
		elif descr[0] == 'graph' :
			read_old_graph(f, t, descr, lfiles)

	#read stored properties
	props = {}
	for fname in f.namelist() :
		name, ext = splitext(fname)
		if ext == ".tip" :
			if name == "position" :#special treatment
				pos, descr = read_data(f, fname)
				m = t.geometry()
				for pid, vec in pos.iteritems() :
					try :
						m.set_position(pid, vec)
					except InvalidDart :
						pass #TODO I don't know why I stored old tissues
							 #with this problem
			
			else :
				props[name] = read_data(f, fname)
	
	f.close()
	
	#return
	return t, props


def convert_old_tissue (filename) :
	"""Try to convert old tissue file to new tissue file
	"""
	t, props = read_old(filename)

	#remove unused types
	types = sorted(t.types() )
	for tid in types[:-2] : #keeps only wall and cell
	                        #, usually the two highest ones
		t.remove_type(tid)

	#write new tissue
	f = topen("new_%s" % filename, 'w')
	f.write(t)
	for name, (prop, descr) in props.iteritems() :
		f.write(prop, name, descr)
	
	f.close()













