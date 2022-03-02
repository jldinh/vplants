from numpy import zeros,subtract
from numpy.linalg import norm

def comp (V1, V2) :
	return norm(subtract(V1,V2) ) < 1e-10

def bound (solver) :
	return

def empty (state) :
	return zeros( state.shape[1:])


