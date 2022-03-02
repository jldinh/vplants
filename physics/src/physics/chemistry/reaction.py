from interface.chemistry import IChemistry
import numpy as np
import scipy.sparse as spsp
import scipy as sp

class Reaction (IChemistry) :
	"""
	compute creation and decay of a substance
	use an implicit integration scheme
	don't hesitate to subclass to implement your own reaction schemes
	
	Ci(t+dt) = Ci(t) + dt*(A-B Ci)
	"""
	def __init__ (self, creation, decay) :
		"""
		constructor
		:Parameters:
			- `creation`: parameter of creation (A mol.[elm volume]-1.s-1) for reaction equation
			- `decay`: parameter of decay (B s-1) for reaction equation
		:Types:
			- `creation`: dict of {id:float}
			- `decay` : dict of {id:float}
		"""
		self._creation=creation
		self._decay=decay
		self.pve_feedback = {}	
		for _key,_val in creation.iteritems() :
			self.pve_feedback[_key] = 0.
		self.nve_feedback = {}	
		for _key,_val in decay.iteritems() :
			self.nve_feedback[_key] = 0.
	
	def react (self, substance, dt, _pve_feedback = None, _nve_feedback = None, nb_steps = 1) :
		"""
		compute physiological reactions inside elements
		"""
		creation = self._creation
		decay = self._decay

		if _pve_feedback != None :
			self.pve_feedback = _pve_feedback
		if _nve_feedback != None :
			self.nve_feedback = _nve_feedback
				
		for i in xrange(nb_steps) :
			for elm_id,A in creation.iteritems() :
				A += self.pve_feedback[elm_id]
				substance[elm_id] += A * dt
			for elm_id,B in decay.iteritems() :
				B += self.nve_feedback[elm_id]
				substance[elm_id] /= (1 + B * dt)


class Reaction_array (IChemistry) :
	"""
	compute creation and decay of a substance
	use an implicit integration scheme
	don't hesitate to subclass to implement your own reaction schemes
	
	Ci(t+dt) = Ci(t) + dt*(A-B Ci)
	"""
	def __init__ (self, creation, decay) :
		"""
		constructor
		:Parameters:
			- `creation`: parameter of creation (A mol.[elm volume]-1.s-1) for reaction equation
			- `decay`: parameter of decay (B s-1) for reaction equation
		:Types:
			- `creation`: numpy array of {id:float}
			- `decay` : numpy array of {id:float}
		"""
		self._creation=creation
		self._decay=decay
		self.pve_feedback = np.zeros_like(self._creation)
		self.nve_feedback = np.zeros_like(self._decay)
		
	def react (self, _substance, dt, _pve_feedback = None, _nve_feedback = None, nb_steps = 1) :
		"""
		compute physiological reactions inside elements

		"""
		creation = self._creation
		decay = self._decay
		substance = _substance

		if _pve_feedback != None :
			self.pve_feedback = _pve_feedback
		else :
			self.pve_feedback = 0 * substance
		if _nve_feedback != None :
			self.nve_feedback = _nve_feedback
		else :
			self.nve_feedback = 0 * substance
		for i in xrange(nb_steps) :
			A = creation + self.pve_feedback
			try :
				print 'generation from 1503 through face 3441 is',A[(1503-1024,3441-1985)]*dt
				print 'generation from 1534 through face 3441 is',A[(1534-1024,3441-1985)]*dt
			except: pass
			substance = substance + A * dt
			try :
				print 'substance from 1503 through face 3441 is',substance[(1503-1024,3441-1985)]
				print 'substance from 1534 through face 3441 is',substance[(1534-1024,3441-1985)]
			except: pass
			B = decay + self.nve_feedback
			_ones = np.divide(B,B)
#			_ones = np.ones_like(B)
			try :
				_substance03 =  substance[(1503-1024,3441-1985)]
				_substance34 =  substance[(1534-1024,3441-1985)]
			except : pass
			substance = np.divide(substance,(_ones + B * dt))
			try :
				print 'degrad',_substance03 - substance[(1503-1024,3441-1985)]
				print 'degrad',_substance34 - substance[(1534-1024,3441-1985)]
				print 'final substance from 1503 through face 3441 is',substance[(1503-1024,3441-1985)]
				print 'final substance from 1534 through face 3441 is',substance[(1534-1024,3441-1985)]
				print
			except: pass
		return substance

