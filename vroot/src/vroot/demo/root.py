from celltissue.data import DensityProperty

class Root (object) :
	"""
	a simple container for root simulation
	"""
	def __init__ (self, tissue, pos) :
		self.tissue=tissue
		self.pos=pos
		self.auxin=DensityProperty(0,tissue,pos,0.)
