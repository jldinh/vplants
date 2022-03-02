from numpy import zeros
from scipy.linalg import solve

def apply_strain (E, ref_coords, dN) :
	"""Compute new positions according to strain.
	
	assert r0, s0, s1 = 0
	"""
	R1,R2,S2 = ref_coords
	#create matrices
	A = zeros( (3,3) )
	B = zeros( (3,1) )
	
	#fill matrices
	A[0,0] = dN[1,0]
	A[0,1] = dN[2,0]
	A[1,2] = dN[2,1]
	A[2,0] = dN[1,1]
	A[2,1] = dN[2,1]
	A[2,2] = dN[2,0]
	
	B[0,0] = E[0,0] + R1 * dN[1,0] + R2 * dN[2,0]
	B[1,0] = E[1,1] + S2 * dN[2,1]
	B[2,0] = E[1,0] + E[0,1] + R1 * dN[1,1] + R2 * dN[2,1] + S2 * dN[2,0]
	
	#solve
	res = solve(A,B)
	
	#return
	return res[0,0],res[1,0],res[2,0]
