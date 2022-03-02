def func_print_cell_info(prop):
	'''    Print selected information for clicked cell
	'''
	def func (elmid) :
		print "cell",elmid,":",prop[elmid]
		
	return func,
