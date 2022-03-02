from os import mkdir,path
from glob import glob
import numpy
from numpy import array,empty

def read_image (dirname, logout) :
	"""
	read slices and construct a 3D matrix
	"""
	#TODO find dimensions
	nb = len(glob(path.join(dirname,"slice*.txt")))
	f = open(path.join(dirname,"slice%.4d.txt" % 0),'r')
	data = f.read()
	lines = [line for line in data.split("\n") if len(line) > 0]
	f.close()
	nbi = len(lines)
	nbj = len([s for s in lines[0].split("\t") if len(s) > 0])
	#nb = 10
	mat = empty( (nbi,nbj,nb), numpy.int )
	logout.write("nb slices: %d\n" % nb)
	for ind in xrange(nb) :
		logout.write("%d," % ind)
		logout.flush()
		f = open(path.join(dirname,"slice%.4d.txt" % ind),'r')
		data = f.read()
		lines = [line for line in data.split("\n") if len(line) > 0]
		for i,line in enumerate(lines) :
			for j,val in enumerate(s for s in line.split("\t") if len(s) > 0) :
				mat[i,j,ind] = int(val)
		f.close()
	logout.write("\n")
	return mat

def write_image (mat, dirname, logout) :
	"""
	write set of slices into a directory
	"""
	if not path.exists(dirname) :
		mkdir(dirname)
	imax,jmax,kmax = mat.shape
	logout.write("nb slices: %d\n" % kmax)
	for k in xrange(kmax) :
		logout.write("%d," % k)
		logout.flush()
		f = open(path.join(dirname,"slice%.4d.txt" % k),'w')
		for i in xrange(imax) :
			for j in xrange(jmax) :
				f.write("%d\t" % mat[i,j,k])
			f.write("\n")
		f.close()
	logout.write("\n")
			
