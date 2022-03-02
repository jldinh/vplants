from interface.chemistry import IChemistry

class FixedConcentration (IChemistry) :
	def __init__ (self, concentration_values) :
		self._fixed=concentration_values
	
	def react (self, substance, dt) :
		for cid,conc in self._fixed.iteritems() :
			substance[cid]=conc

class FixedFlux (dict) :
	pass
