from openalea.svgdraw import from_xml,to_xml
from openalea.celltissue import ConfigItem
from openalea.tissueshape import add_graph_layer

def func_action () :
	"""User defined function for an action.
	"""
	def func () :
		print "toto"
	
	return func,

def func_tool () :
	"""User defined function for a tool.
	"""
	def func (elmid) :
		if elmid is None :
			print "nothing selected"
		else :
			print "%d has been selected" % elmid
	
	return func,

def func_modify_tissue (tissuedb, wall_deg) :
	"""Add a graph between cells in the tissue.
	"""
	t = tissuedb.tissue()
	cfg = tissuedb.get_config("config")
	
	#add elms types in the tissue
	EDGE = t.add_type("EDGE")
	graph_id = t.add_relation("graph",(cfg.CELL,EDGE) )
	graph = t.relation(graph_id)
	
	#fill graph
	mesh = t.relation(cfg.mesh_id)
	for wid in mesh.wisps(wall_deg) :
		if mesh.nb_regions(wall_deg,wid) == 2 :
			cid1,cid2 = mesh.regions(wall_deg,wid)
			graph.add_edge(cid1,cid2)
			graph.add_edge(cid2,cid1)
	
	#fill config
	cfg.add_item(ConfigItem("EDGE",EDGE) )
	cfg.add_item(ConfigItem("graph_id",graph_id) )
	
	#fill properties
	
	#add info in visual descr
	try :
		data = tissuedb.get_external_data("visual_descr.svg")
		sc = from_xml(data)
		add_graph_layer(sc)
		data = to_xml(sc)
		tissuedb.set_external_data("visual_descr.svg",data)
	except KeyError :
		pass
	
	#return
	return tissuedb,

def func_diffusion (mesh, prop, dt) :
	"""Diffuse prop for dt.
	adhoc function for tutorial
	do not use outside of tuto13
	"""
	D = 0.01
	ini_value = dict(prop)
	for wid in mesh.wisps(1) :
		if mesh.nb_regions(1,wid) == 2 :
			cid1,cid2 = mesh.regions(1,wid)
			flux = (ini_value[cid1] - ini_value[cid2]) * D * dt
			prop[cid1] -= flux
			prop[cid2] += flux
	
	return prop,
