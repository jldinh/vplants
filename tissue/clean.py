import os
from os import path
from shutil import rmtree
from glob import glob

def clean_directory (dir_name) :
	list_rep=[]
	for filename in os.listdir(dir_name) :
		filepath=path.join(dir_name,filename)
		if path.isdir(filepath) :
			list_rep.append(filepath)
		else :
			base,ext=path.splitext(filename)
			if ext=='.pyc' : 
				os.remove(filepath)
				print filepath
	
	for rep in list_rep : clean_directory(rep)

def clean_dist (dir_name) :
	build = path.join(dir_name,"build")
	dist = path.join(dir_name,"dist")
	egg1 = path.join(dir_name,"%s.egg-info" % dir_name)
	egg2 = path.join(dir_name,"src","VPlants.Tissue.%s.egg-info" % dir_name)
	dvlpt = path.join(dir_name,"src","openalea")
	for name in (build,dist,dvlpt,egg1,egg2) :
		try :
			rmtree(name)
		except OSError :
			print "%s not found" % name

def clean_gui_files (dir_name) :
	for filename in glob(path.join(dir_name,"*_rc.py")) :
		os.remove(filename)
	for filename in glob(path.join(dir_name,"*_ui.py")) :
		if path.basename(filename) != "compile_ui.py" :
			os.remove(filename)

def clean_simulation (dir_name) :
	#gui files
	clean_gui_files(dir_name)
	#tissue.zip file if needed
	if path.exists(path.join(dir_name,"create_tissue.py")) :
		try :
			os.remove(path.join(dir_name,"tissue.zip"))
		except OSError :
			print "tissue.zip not found"

if __name__=='__main__' :
	clean_directory(".")
	for name in ("celltissue",
	             "demo",
	             "genepattern",
	             "growth",
	             "root",
	             "tissuedb",
	             "tissueedit",
	             "tissue_meta",
	             "tissuepainter",
	             "tissueshape",
	             "tissueview",
	             "tuto",
	             "vmanalysis",
	             "wusmodel") :
#		clean_dist(name)
#		clean_gui_files(path.join(name,"src",name) )
		pass
	
#	for name in os.listdir("simulation") :
#		if not name.startswith(".") :
#			clean_simulation(path.join("simulation",name))

