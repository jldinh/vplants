import numpy
from numpy import array,empty
from zipfile import ZipFile

def find_volumes (mat, logout) :
	V = [0] * (mat.max() + 1)
	imax,jmax,kmax = mat.shape
	logout.write("nb slices: %d\n" % kmax)
	for k in xrange(kmax) :
		logout.write("%d," % k)
		logout.flush()
		for i in xrange(imax) :
			for j in xrange(jmax) :
				V[mat[i,j,k]] += 1
	logout.write("\n")
	return V

def find_surfaces (mat, logout) :
	S = {}
	imax,jmax,kmax = mat.shape
	logout.write("nb slices: %d\n" % kmax)
	for k in xrange(kmax-1) :
		logout.write("%d," % k)
		logout.flush()
		for i in xrange(imax-1) :
			for j in xrange(jmax-1) :
				rcol = mat[i,j,k]
				for oi,oj,ok in [(1,0,0),(0,1,0),(0,0,1)] :
					col = mat[i+oi,j+oj,k+ok]
					if col != rcol :
						key = (min(rcol,col),max(rcol,col))
						S[key] = S.get(key,0) + 1
	logout.write("\n")
	return S

def find_SV (mat, logout) :
	S = {}
	V = [0] * (mat.max() + 1)
	imax,jmax,kmax = mat.shape
	logout.write("nb slices: %d\n" % kmax)
	for k in xrange(kmax-1) :
		logout.write("%d," % k)
		logout.flush()
		for i in xrange(imax-1) :
			for j in xrange(jmax-1) :
				rcol = mat[i,j,k]
				V[rcol] += 1
				for oi,oj,ok in [(1,0,0),(0,1,0),(0,0,1)] :
					col = mat[i+oi,j+oj,k+ok]
					if col != rcol :
						key = (min(rcol,col),max(rcol,col))
						S[key] = S.get(key,0) + 1
	logout.write("\n")
	return S,V

