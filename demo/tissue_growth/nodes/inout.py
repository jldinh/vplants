###################################################
#
#	read tissue and properties
#
###################################################
from openalea.celltissue import topen,Config
from openalea.tissueshape import topgl,totup

def create_param () :
	return Config("param"),

def read_tissue (name, param) :
	f = topen(name,'r')
	param.t,descr = f.read()
	param.cfg = f.read_config("config")
	pos,descr = f.read("position")
	#read properties
	propnames = set(name for name in dir(param) if not name.startswith("_"))
	propnames -= set( ("add_item","add_section","elms","name") )
	for propname in propnames :
		try :
			prop,descr = f.read(propname)
			eval("param.%s.clear()" % propname)
			eval("param.%s.update(prop)" % propname)
		except KeyError :
			print "%s undefined" % propname
	f.close()
	
	param.pos = topgl(pos)
	param.mesh = param.t.relation(param.cfg.mesh_id)
	param.graph = param.t.relation(param.cfg.graph_id)
	return param,

def write_tissue (name, param) : #TODO
	f = topen(name,'w')
	f.write(param.t)
	f.write_config(param.cfg,"config")
	f.write(totup(param.pos),"position","position of points in m")
	for propname in ("cell_age","morphogen","D","alpha","beta","K","l0","weight","turgor","gamma") :
		eval("f.write(param.%s,'%s')" % (propname,propname))
	f.close()


