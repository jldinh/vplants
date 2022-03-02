def multiply_prop(prop, factor):
	'''Multiply values in a given property by chosen factor.
	
	return a function to be used in a tool.
	'''	
	def func (elmid) :
		before = prop[elmid]
		if before :			prop[elmid] *= factor
		elif (factor>1):
			prop[elmid] += 0.01
		print "elm",elmid,":",before,"->",prop[elmid]
	
	return func,
