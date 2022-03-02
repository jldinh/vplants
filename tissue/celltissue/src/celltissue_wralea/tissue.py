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

__doc__="""
node definition for celltissue package
"""

__license__= "Cecill-C"
__revision__=" $Id: $ "

from PyQt4.QtCore import Qt,SIGNAL,QByteArray
from PyQt4.QtGui import QMessageBox,QDialog,QVBoxLayout,\
                        QLabel,QDialogButtonBox,QGroupBox,\
                        QScrollArea,QWidget,QHBoxLayout,\
                        QFrame,QGridLayout,\
                        QPixmap,QPushButton,QPainter,QIcon,QColor,QPalette
from PyQt4.QtSvg import QSvgWidget,QSvgRenderer
from openalea.core import ScriptLibrary
from openalea.celltissue import TissueDB
from openalea.tissueshape import tovec,totup
from openalea.container import Quantity

#########################################
#
#	file
#
#########################################
def read (filename) :
	#read
	db = TissueDB()
	db.read(filename)
	#transform positions
	try :
		pos = db.get_property("position")
		db.set_property("position",tovec(pos) )
	except KeyError :
		pass
	#return
	return db,

def read_script (inputs, outputs) :
	lib = ScriptLibrary()
	filename, = inputs
	db, = outputs
	db = lib.register(db,"db")
	
	script = "from openalea.celltissue import TissueDB\n"
	script += "from openalea.tissueshape import tovec\n"
	script += "\n"
	script += "%s = TissueDB()\n" % db
	script += "%s.read('%s')\n" % (db,filename)
	script += "#transform positions\n"
	script += "try :\n"
	script += "	pos = db.get_property('position')\n"
	script += "	%s.set_property('position',tovec(pos) )\n" % db
	script += "except KeyError :\n"
	script += "	pass\n\n"
	
	return script

def write (db, filename) :
	try :
		#transform positions
		pos = db.get_property("position")
		db.set_property("position",totup(pos) )
		#write
		db.write(filename)
		#put back pos
		db.set_property("position",pos)
	except KeyError :
		#write
		db.write(filename)
	#return
	return db,

def write_script (db, filename) :
	lib = ScriptLibrary()
	db,filename = inputs
	db, = outputs
	
	db,script = lib.name(db,"s")
	
	script += "try :\n"
	script += "	#transform positions\n"
	script += "	pos = %s.get_property('position')\n" % db
	script += "	%s.set_property('position',totup(pos) )\n" % db
	script += "	#write\n"
	script += "	%s.write(%s)\n" % (db,filename)
	script += "	#put back pos\n"
	script += "	%s.set_property('position',pos)\n" % db
	script += "except KeyError :\n"
	script += "	#write\n"
	script += "	%s.write(%s)\n\n" % (db,filename)
	
	return script

def info_widget (db) :
	"""Display infos on a tissuedb in a dialog.
	"""
	dial = QDialog()
	dial.setWindowTitle("Tissue DB")
	dial_lay = QVBoxLayout(dial)
	
	scroll = QScrollArea(dial)
	dial_lay.addWidget(scroll)
	centering_widget = QFrame()
	centering_widget.setFrameShape(QFrame.Box)
	centering_lay = QHBoxLayout(centering_widget)
	centering_lay.addStretch(1)
	w = QWidget(centering_widget)
	centering_lay.addWidget(w)
	centering_lay.addStretch(1)
	lay = QVBoxLayout(w)
		
	#tissue infos
	tis_box = QGroupBox("Tissue",w)
	lay.addWidget(tis_box)
	tis_lay = QGridLayout(tis_box)
		
	tissue = db.tissue()
	if tissue is None :
		lab = QLabel("No tissue",tis_box)
		tis_lay.addWidget(lab,0,0)
	else :
		#types
		type_box = QGroupBox("Types:",tis_box)
		tis_lay.addWidget(type_box,0,0)
		type_lay = QVBoxLayout(type_box)
		for type_id in tissue.types() :
			txt = "    - %s (%d)" % (tissue.type_name(type_id),type_id)
			lab = QLabel(txt,type_box)
			type_lay.addWidget(lab)
		
		#relations
		rel_box = QGroupBox("Relations:",tis_box)
		tis_lay.addWidget(rel_box,1,0)
		rel_lay = QVBoxLayout(rel_box)
		for relation_id in tissue.relations() :
			relation = tissue.relation(relation_id)
			rtype_name = db._type_name(relation)
			inv_elms = ",".join(tissue.type_name(type_id) 
			                    for type_id in relation.involved_elements() )
			txt = "    - %s id %d involving elements (%s)" % (rtype_name,relation_id,inv_elms)
			lab = QLabel(txt,rel_box)
			rel_lay.addWidget(lab)
		
		#visual descr
		try :
			svg_data = db.get_external_data("visual_descr.svg")
			
			svg_dial = QDialog(dial)
			svg_dial.setWindowTitle("Tissue visual description")
			svg_dial.setPalette(QPalette(QColor(255,255,255) ) )
			svg_dial_lay = QVBoxLayout(svg_dial)
			
			svg_widget = QSvgWidget(svg_dial)
			svg_data = QByteArray(str(svg_data) )
			svg_widget.load(svg_data)
			
			svg_rend = svg_widget.renderer()
			svg_widget.setMinimumSize(svg_rend.defaultSize() )
			svg_dial_lay.addWidget(svg_widget)
			
			size = svg_rend.defaultSize()
			if size.width() < size.height() :
				pix = QPixmap(size.width() * 100 / size.height(),100)
			else :
				pix = QPixmap(100,size.height() * 100 / size.width() )
			pix.fill(QColor(255,255,255) )
			painter = QPainter(pix)
			svg_rend.render(painter)
			painter.end()
			
			svg_button = QPushButton(QIcon(pix),"",tis_box)
			svg_button.setCheckable(True)
			svg_button.setIconSize(pix.size() )
			tis_lay.addWidget(svg_button,0,1,2,1)
			
			svg_button.connect(svg_button,SIGNAL("toggled(bool)"),svg_dial.setVisible)
		except KeyError :
			pass
		
	#config infos
	cfg_box = QGroupBox("Config files:",w)
	lay.addWidget(cfg_box)
	cfg_lay = QVBoxLayout(cfg_box)
	for name,cfg in db._config.iteritems() :
		lab = QLabel("%s" % name,cfg_box)
		cfg_lay.addWidget(lab)
		for i in dir(cfg) :
			if not i.startswith("_") and i not in ("elms","name","add_item","add_section") :
				txt = "    - %s = %s" % (i,str(cfg[i]) )
				lab = QLabel(txt,cfg_box)
				cfg_lay.addWidget(lab)
	
	#properties
	prop_box = QGroupBox("Properties:",w)
	lay.addWidget(prop_box)
	prop_lay = QVBoxLayout(prop_box)
	for name,prop in db._property.iteritems() :
		#defined on which elements
		elm_types = set(tissue.type(elmid) for elmid in prop)
		txt = "%s: %d elms defined on elements of type %s\n" % (name,
		                              len(prop),
		                              ",".join("%d(%s)" % (typ,\
		                                 tissue.type_name(typ) )\
		                                 for typ in elm_types) )
		
		#unit
		if isinstance(prop,Quantity) :
			txt += "    unit: %s\n" % prop.unit()
		
		#description
		try :
			descr = db.description(name)
			if descr == "" :
				txt += "    no description"
			else :
				txt += "    descr: %s" % descr
		except KeyError :
			txt += "    no description"
		lab = QLabel(txt,prop_box)
		prop_lay.addWidget(lab)
	
	#external data
	ext_box = QGroupBox("External data:",w)
	lay.addWidget(ext_box)
	ext_lay = QVBoxLayout(ext_box)
	for name,data in db._external.iteritems() :
		txt = "%s with a length of %d" % (name,len(data) )
		lab = QLabel(txt,ext_box)
		ext_lay.addWidget(lab)
	
	#dialog properties
	dial.setModal(True)
	#w.setMinimumSize(400,300)
	buttons = QDialogButtonBox(QDialogButtonBox.Ok,Qt.Horizontal,dial)
	dial_lay.addWidget(buttons)
	dial.connect(buttons,SIGNAL("accepted()"),dial.accept)
	
	scroll.setWidget(centering_widget)
	dial.exec_()

def info (db, widget) :
	"""Print infos on a tissuedb.
	
	widget: bool, tells wether the info
	is printed as a string or in a dialog widget
	"""
	if widget :
		info_widget(db)
	else :
		print db.info()

def info_script (inputs, outputs) :
	return "#infos\n"

#########################################
#
#	access
#
#########################################
def tissue (db) :
	return db,db.tissue()

def tissue_script (inputs, outputs) :
	lib =ScriptLibrary()
	db, = inputs
	dummy,tissue = outputs
	tissue = lib.register(tissue,"tissue")
	
	db,script = lib.name(db,"")
	script += "%s = %s.tissue()\n" (tissue,db)
	
	return script

def get_property (db, name) :
	return db,db.get_property(name)

def get_property_script (inputs, outputs) :
	lib = ScriptLibrary()
	db,name = inputs
	db,script = lib.name(db,"")
	dummy,prop = outputs
	prop = lib.register(prop,"prop_%s" % name)
	
	script += "%s = %s.get_property('%s')\n" % (prop,
	                                            db,
	                                            name)
	
	return script

def get_config (db, name) :
	return db,db.get_config(name)

def get_config_script (inputs, outputs) :
	lib = ScriptLibrary()
	db,name = inputs
	db,script = lib.name(db,"")
	dummy,cfg = outputs
	cfg = lib.register(cfg,"cfg_%s" % name)
	
	script += "%s = %s.get_config('%s')\n" % (cfg,
	                                          db,
	                                          name)
	
	return script

def get_topology (db, name, cfg) :
	return db,db.get_topology(name,cfg)

def get_topology_script (inputs, outputs) :
	lib = ScriptLibrary()
	db,name,cfg = inputs
	db,script = lib.name(db,"")
	dummy,topo = outputs
	topo = lib.register(topo,"topo")
	
	script += "%s = %s.get_topology('%s','%s')\n" % (topo,
	                                                 db,
	                                                 name,
	                                                 cfg)
	
	return script

#########################################
#
#	edition
#
#########################################
def empty_property (db, name, descr) :
	prop = {}
	db.set_property(name,prop)
	db.set_description(name,descr)
	
	return db,prop

def empty_property_script (inputs, outputs) :
	lib = ScriptLibrary()
	db,name,descr = inputs
	name = str(name)
	descr = str(descr)
	db,script = lib.name(db,"")
	dummy,prop = outputs
	prop = lib.register(prop,"prop")
	
	script += "%s = {}\n" % prop
	script += "%s.set_property('%s',%s)\n" % (db,name,prop)
	script += "%s.set_description('%s','%s')\n" % (db,name,descr)
	
	return script

def def_property (db, name, val, elm_type, cfg, descr) :
	cfg = db.get_config(cfg)
	prop = {}
	
	if callable(val) :
		func = val
	else :
		def func (*args) :
			return val
	
	for elmid in db.tissue().elements(cfg[elm_type]) :
		prop[elmid] = func()
	
	db.set_property(name,prop)
	db.set_description(name,descr)
	
	return db,prop

def def_property_script (inputs, outputs) :
	lib = ScriptLibrary()
	db,name,val,elm_type,cfg,descr = inputs
	db,script = lib.name(db,"")
	dummy,prop = outputs
	prop = lib.register(prop,"prop")
	
	script += "cfg = %s.get_config('%s')\n" % (db,cfg)
	script += "%s = {}\n" % prop
	script += "for elmid in %s.tissue().elements(cfg.%s) :\n" % (db,elm_type)
	if callable(val) :
		func = lib.register(val,"func")
		script += "	%s[elmid] = %s()\n\n" % (prop,func)
	else :
		script += "	%s[elmid] = %s\n\n" % (prop,val)
	
	script += "%s.set_property('%s',%s)\n" % (db,name,prop)
	script += "%s.set_description('%s','%s')\n" % (db,name,descr)
	
	return script

def scaled_property (db, name, ref_prop, scale) :
	prop = {}
	
	for key,val in ref_prop.iteritems() :
		prop[key] = val * scale
	
	db.set_property(name,prop)
	
	return db,prop

def scaled_property_script (inputs, outputs) :
	lib = ScriptLibrary()
	db,name,ref_prop,scale = inputs
	db,script = lib.name(db,"")
	ref_prop,script = lib.name(ref_prop,script)
	dummy,prop = outputs
	prop = lib.register(prop,"prop")
	
	script += "%s = {}\n" % prop
	script += "for key,val in %s.iteritems() :\n" % ref_prop
	script += "	%s[key] = val * %s\n\n" % (prop,scale)
	script += "%s.set_property('%s',%s)\n" % (db,name,prop)
	
	return script

def merge_property (prop, ref_prop) :
	"""Update the content of prop with ref_prop.
	"""
	prop.update(ref_prop)
	
	return prop,

def merge_content_script (inputs, outputs) :
	lib = ScriptLibrary()
	prop,ref_prop = inputs
	prop,script = lib.name(prop,"")
	ref_prop,script = lib.name(ref_prop,script)
	
	script += "%s.update(%s)\n" % (prop,ref_prop)
	
	return script

