def func_set_inward_edges_property(prop, value, graph):
	'''    Set a uniform given value for given property on inward edges of selected cell
	'''	def func (elmid) :
		if elmid is not None :
			for eid in graph.in_edges(elmid) :
				prop[eid] = value
		print "in edge set", eid	
	return func,
