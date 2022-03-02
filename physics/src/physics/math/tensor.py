from scipy import array,tensordot,matrix,reshape,transpose
from scipy.sparse import csr_matrix
from scipy.linalg import solve as scipy_solve
from scipy.linalg import det

def coord_iterator (remaining_shape, ind=[]) :
	if len(remaining_shape)==0 :
		yield tuple(ind)
	else :
		dim=remaining_shape[0]
		shp=remaining_shape[1:]
		for i in xrange(dim) :
			for index in coord_iterator(shp,ind+[i]) :
				yield index

class Tensor (object) :
	def __init__ (self, data) :
		self._data=array(data)
	
	def copy (self) :
		return Tensor(self._data)
	###########################################################
	#
	#		wrapper for scipy array access
	#
	###########################################################
	def __str__ (self) :
		return str(self._data)
	
	def shape (self) :
		return self._data.shape
	
	def __getitem__ (self, ind) :
		return self._data[ind]
	
	def __setitem__ (self, ind, val) :
		self._data[ind]=val
	
	def trace (self) :
		return self._data.trace()
	
	def det (self) :
		return det(self._data)
	###########################################################
	#
	#		tensor operators
	#
	###########################################################
	def __rmul__ (self, val) :
		return Tensor(self._data*val)
	
	def __mul__ (self, tensor) :
		return Tensor(tensordot(self._data,tensor._data,axes=1))
	
	def __iadd__ (self, tensor) :
		self._data+=tensor._data
		return self
	
	def __isub__ (self, tensor) :
		self._data-=tensor._data
		return self
	
	def __sub__ (self, tensor) :
		pass
	############################################################
	#
	#		change of basis
	#
	############################################################
	def change_basis (self, trans_matrix) :
		"""
		change the basis in which the tensor is expressed
		trans_matrix is a list of matrix (one per order) that express
		the positions of old_vectors in new basis
		"""
		#parcours de tous les elements du nouveau tenseur
		T=zeros(self.shape())
		for ind in coord_iterator(T.shape()) :
			val=0.
			#sommation sur tous les elements du vieux tenseur
			for i in coord_iterator(self.shape()) :
				v=float(self[i])
				for order,coord in enumerate(i) :
					v*=float(trans_matrix[order][ind[order],coord])
				val+=v
			T[ind]=val
		return T
	
	############################################################
	#
	#		view as a matrix
	#
	############################################################
	def contract (self, tensor, order=1) :
		return Tensor(tensordot(self._data,tensor._data,axes=2))
	
	def transpose (self) :
		"""
		try to transpose the tensor
		"""
		return Tensor(transpose(self._data))
	
	def as_matrix (self) :
		"""
		return a matrix representation of this tensor
		"""
		shp=self._data.shape
		if len(shp)%2!=0 :
			raise UserWarning("I don't know how to matrixify a tensor with this shape %s" % str(shp))
		d1=1
		for d in shp[:(len(shp)/2)] :
			d1*=d
		d2=1
		for d in shp[(len(shp)/2):] :
			d2*=d
		return csr_matrix(reshape(self._data,(d1,d2)))
	
	def as_vector (self) :
		"""
		return a matrix (Nx1) representation
		of this tensor
		"""
		dim=1
		for d in self._data.shape :
			dim*=d
		return array(reshape(self._data,(dim,1)))

def zeros (shape) :
	shp=shape[::-1]
	dat=0.
	for dim in shp :
		dat=[dat]*dim
	return Tensor(dat)

def solve (A,B) :
	"""
	solve A X = B
	and return a tensor X with complementary
	shape of B according to A
	"""
	x=scipy_solve(A.as_matrix(),B.as_vector())
	shp=A.shape()[len(B.shape()):]
	return Tensor(reshape(x,shp))


