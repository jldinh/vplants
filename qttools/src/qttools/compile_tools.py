import os
from os.path import splitext
from PyQt4 import uic

def make_menu (filename) :
	f=open(filename,'r')
	lines=f.readlines()
	f.close()
	f=open(filename,'w')
	for line in lines :
		if " MainWindow." not in line \
			and "centralwidget" not in line \
			and "        self.menubar" not in line \
			and "statusbar" not in line :
			if "self.menubar" in line :
				f.write(line.replace("self.menubar","MainWindow"))
			elif "QToolBar" in line :
				f.write(line.replace("MainWindow",""))
			else :
				f.write(line)
	f.close()

def change_object_type (filename, obj_name, new_type, module) :
	f=open(filename,'r')
	lines=f.readlines()
	f.close()
	f=open(filename,'w')
	stamp=" self.%s = " % obj_name
	for line in lines :
		if stamp in line :
			pos_equal=line.index("=")
			pos_parenthesis=line.index("(")
			new_line=line[:pos_equal+1]+" %s" % new_type + line[pos_parenthesis:]
			f.write(new_line)
		else :
			f.write(line)
	f.write("from %s import %s\n" % (module,new_type))
	f.close()

def compile_ui (filename) :
	name=splitext(filename)[0]
	uiname="%s_ui.py" % name
	f=open(uiname,'w')
	uic.compileUi(filename,f)
	f.close()
	return uiname

def compile_rc (filename) :
	name=splitext(filename)[0]
	rcname="%s_rc.py" % name
	os.system("pyrcc4 %s > %s " % (filename, rcname))
	return rcname

__all__=["make_menu","change_object_type","compile_ui","compile_rc"]
