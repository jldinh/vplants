from os import mkdir,path,rename,system
from shutil import copytree,rmtree
from math import sin,cos
import numpy
from numpy import array,empty

def crop (mat, bb) :
	"""
	crop a 3D image according to bb
	"""
	bi_min,bi_max,bj_min,bj_max,bk_min,bk_max = bb
	imax,jmax,kmax = mat.shape
	bi_min = max(0,bi_min)
	bj_min = max(0,bj_min)
	bk_min = max(0,bk_min)
	bi_max = min(imax - 1,bi_max)
	bj_max = min(jmax - 1,bj_max)
	bk_max = min(kmax - 1,bk_max)
	#create local matrix to store output
	nbi = bi_max - bi_min +1
	nbj = bj_max - bj_min +1
	nbk = bk_max - bk_min +1
	cmat = empty( (nbi,nbj,nbk), numpy.int )
	#fill output_mat
	for li in xrange(nbi) :
		i = bi_min + li
		for lj in xrange(nbj) :
			j = bj_min + lj
			for lk in xrange(nbk) :
				k = bk_min + lk
				cmat[li,lj,lk] = mat[i,j,k]
	#return
	return cmat

def structural_element_coordinates (radius) :
	from vplants.plantgl.math import norm
	
	coords = []
	for i in xrange(-radius,radius+1) :
		for j in xrange(-radius,radius+1) :
			for k in xrange(-radius,radius+1) :
				if norm( (i,j,k) ) <= radius :
					coords.append( (i,j,k) )
	return coords

def find_bounding_box (mat, col, logout) :
	imax,jmax,kmax = mat.shape
	bi_min = imax
	bi_max = 0
	bj_min = jmax
	bj_max = 0
	bk_min = kmax
	bk_max = 0
	logout.write("nb slices: %d\n" % kmax )
	for k in xrange(kmax) :
		logout.write("%d," % k )
		logout.flush()
		for i in xrange(imax) :
			for j in xrange(jmax) :
				if mat[i,j,k] == col :
					bi_min = min(bi_min,i)
					bi_max = max(bi_max,i)
					bj_min = min(bj_min,j)
					bj_max = max(bj_max,j)
					bk_min = min(bk_min,k)
					bk_max = max(bk_max,k)
	logout.write("\n")
	return bi_min,bi_max,bj_min,bj_max,bk_min,bk_max

def cell_points (mat, cid, bb) :
	"""
	iterate on all points inside the cell
	"""
	bi_min,bi_max,bj_min,bj_max,bk_min,bk_max = bb
	for i in xrange(bi_min,bi_max+1) :
		for j in xrange(bj_min,bj_max+1) :
			for k in xrange(bk_min,bk_max+1) :
				if mat[i,j,k] == cid :
					yield (i,j,k)

def apply_structural_element (mat, cid, struct_elm, bb) :
	"""
	modify elements of mat with color cid according to struct_elm
	"""
	w,h,d = mat.shape
	bi_min,bi_max,bj_min,bj_max,bk_min,bk_max = bb
	#create local matrix to store output
	nbi = bi_max - bi_min +1
	nbj = bj_max - bj_min +1
	nbk = bk_max - bk_min +1
	output_mat = empty( (nbi,nbj,nbk), numpy.int )
	#fill output_mat
	for li in xrange(nbi) :
		i = bi_min + li
		for lj in xrange(nbj) :
			j = bj_min + lj
			for lk in xrange(nbk) :
				k = bk_min + lk
				col = mat[i,j,k]
				if col == cid : #apply structural element
					hist = {}
					for ic,jc,kc in struct_elm :
						ti = i + ic
						tj = j + jc
						tk = k + kc
						if (0 <= ti < w) and (0 <= tj < h) and (0 <= tk < d) :
							col = mat[ti,tj,tk]
							hist[col] = hist.get(col,0) + 1
					hist = [ (nb,col) for col,nb in hist.iteritems() ]
					hist.sort(reverse=True)
					col = hist[0][1]
				#write col
				output_mat[li,lj,lk] = col
	#copy back into mat
	for li in xrange(nbi) :
		i = bi_min + li
		for lj in xrange(nbj) :
			j = bj_min + lj
			for lk in xrange(nbk) :
				k = bk_min + lk
				mat[i,j,k] = output_mat[li,lj,lk]

def cell_volume (mat, cid, bb) :
	"""
	compute the volume of cell cid
	"""
	bi_min,bi_max,bj_min,bj_max,bk_min,bk_max = bb
	V = 0
	for i in xrange(bi_min,bi_max+1) :
		for j in xrange(bj_min,bj_max+1) :
			for k in xrange(bk_min,bk_max+1) :
				if mat[i,j,k] == cid :
					V += 1
	return V

def sphere_filter (input_dir, output_dir, radius) :
	if path.exists("data/stack_out/") :
		rmtree("data/stack_out")
	mkdir("data/stack_out")
	if path.exists("data/stack_in/") :
		rmtree("data/stack_in")
	rename(input_dir,"data/stack_in")
	system("C++/cconvex %d" % radius)
	if path.exists(output_dir) :
		rmtree(output_dir)
	rename("data/stack_in",input_dir)
	rename("data/stack_out",output_dir)

def delete_cell (mat, cid, logout, bb = None) :
	"""
	remove a cell by recursively applying
	sphere filter on it
	"""
	if bb is None :
		bb = find_bounding_box(mat,cid)
	for r in xrange(3,300) :
		struct_elm = structural_element_coordinates(r)
		logout.write("radius %d\n" % r)
		logout.flush()
		for i in xrange(r) :
			logout.write("pass number %d\n" % i)
			logout.flush()
			apply_structural_element (mat,cid,struct_elm,bb)
			V = cell_volume(mat,cid,bb)
			logout.write("V: %d\n" % V)
			logout.flush()
			if V == 0 :
				return
	raise UserWarning("unable to delete cell %d" % cid)

def main_axis (pts) :
	"""
	compute main axis of a cell
	"""
	from scipy.optimize import fmin
	from vplants.plantgl.math import Vector3
	
	bary=sum(pts,Vector3())/len(pts)
	pts=[vec-bary for vec in pts]
	def err (args) :
		alpha, beta = args
		axis=Vector3(cos(alpha)*sin(beta),sin(alpha)*sin(beta),cos(beta))
		e=[abs(axis*vec) for vec in pts]
		return -sum(e)
	op=fmin(err,(0.,0.),disp=0)
	alpha,beta=op
	return bary,Vector3(cos(alpha)*sin(beta),sin(alpha)*sin(beta),cos(beta))

def divide_cell (mat, cid, did1, did2, point, axis, bb) :
	"""
	divide a cell according to point and axis
	"""
	bi_min,bi_max,bj_min,bj_max,bk_min,bk_max = bb
	#create local matrix to store output
	nbi = bi_max - bi_min +1
	nbj = bj_max - bj_min +1
	nbk = bk_max - bk_min +1
	output_mat = empty( (nbi,nbj,nbk), numpy.int )

