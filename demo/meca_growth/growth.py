from celltissue.simulation import Process

class Growth (Process) :
	def __init__ (self, pos, growth_algo, prop_list) :
		Process.__init__(self,"growth")
		self._pos=pos
		self._growth=growth_algo
		self._prop_list=prop_list
	
	def __call__ (self, dt, *args) :
		algo=self._growth.get_algo(dt)
		algo.deform(self._pos)
		for prop in self._prop_list :
			prop.positional_update(algo)
