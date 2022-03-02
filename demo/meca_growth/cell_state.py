from celltissue.simulation import Process

class CellState (Process) :
	def __init__ (self, driving_prop, prop, threshold=0.4, factor=1.) :
		Process.__init__(self,"cell state")
		self._driving=driving_prop
		self._prop=prop
		self._threshold=threshold
		self._factor=factor
	
	def __call__ (self, *args) :
		prop=self._prop
		th=self._threshold
		fac=self._factor
		for wid,val in self._driving.iteritems() :
			if val>th :
				prop[wid]=(val-th)*fac
			else :
				prop[wid]=0.
