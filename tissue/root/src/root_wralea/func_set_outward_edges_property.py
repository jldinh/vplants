def func_set_outward_edges_property(prop, value, graph):
	'''    Set a uniform given value for given property on outward edges of selected cell
	'''	def func (elmid) :
		if elmid is not None :
			for eid in graph.out_edges(elmid) :
				prop[eid] = value
		print "out edge set", eid	
	return func,
