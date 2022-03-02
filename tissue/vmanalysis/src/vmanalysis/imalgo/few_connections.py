class ChangeGraph (object) :
	"""A structure to keep track of changes.
	"""
	def __init__ (self, g = None) :
		self._used = {}
		if g is not None :
			for vox,colors in g._used.iteritems() :
				self._used[vox] = list(colors)
	
	def __add__ (self, tup) :
		ret = ChangeGraph(self)
		try :
			ret._used[tup[0]].append(tup[1])
		except KeyError :
			ret._used[tup[0]] = [tup[1]]
		
		return ret
	
	def colors (self, vox) :
		return self._used.get(vox,[])

def box27 (mat, vox) :
	imax,jmax,kmax = mat.shape
	i, j, k = vox
	for li in (-1,0,1) :
		for lj in (-1,0,1) :
			for lk in (-1,0,1) :
				ni = i + li
				nj = j + lj
				nk = k + lk
				if (0 <= ni < imax) \
				   and (0 <= nj < jmax) \
				   and (0 <= nk < kmax) :
					yield ni,nj,nk

def color6histo (mat, vox) :
	"""Find relative abundance of colors
	in the 6 neighborhood of a voxel.
	"""
	imax,jmax,kmax = mat.shape
	i,j,k = vox
	col = mat[i,j,k]
	
	col_number = {col:0}
	#X
	if i == 0 :
		ncol = 0
	else :
		ncol = mat[i - 1,j,k]
	col_number[ncol] = col_number.get(ncol,0) + 1
	if i == (imax - 1) :
		ncol = 1
	else :
		ncol = mat[i + 1,j,k]
	col_number[ncol] = col_number.get(ncol,0) + 1
	#Y
	if j == 0 :
		ncol = 2
	else :
		ncol = mat[i,j - 1,k]
	col_number[ncol] = col_number.get(ncol,0) + 1
	if j == (jmax - 1) :
		ncol = 3
	else :
		ncol = mat[i,j + 1,k]
	col_number[ncol] = col_number.get(ncol,0) + 1
	#Z
	if k == 0 :
		ncol = 4
	else :
		ncol = mat[i - 1,j,k]
	col_number[ncol] = col_number.get(ncol,0) + 1
	if i == (imax - 1) :
		ncol = 5
	else :
		ncol = mat[i + 1,j,k]
	col_number[ncol] = col_number.get(ncol,0) + 1
	
	#return
	return col_number

def color21histo (mat, vox) :
	"""Find relative abundance of colors
	in the 6 neighborhood of a voxel.
	"""
	imax,jmax,kmax = mat.shape
	i,j,k = vox
	col = mat[i,j,k]
	
	col_number = {col:0}
	for li in (-1,0,1) :
		for lj in (-1,0,1) :
			for lk in (-1,0,1) :
				ni = i + li
				nj = j + lj
				nk = k + lk
				if ni == -1 :
					ncol = 0
				elif ni == imax :
					ncol = 1
				elif nj == -1 :
					ncol = 2
				elif nj == jmax :
					ncol = 3
				elif nk == -1 :
					ncol = 4
				elif nk == kmax :
					ncol = 5
				else :
					ncol = mat[ni,nj,nk]
				col_number[ncol] = col_number.get(ncol,0) + 1
	
	#return
	return col_number

def safe_change_color (mat, vox, previous_modifs, logout) :
	"""Change the color of a pixel, taking
	into account the previous modifs
	"""
	i,j,k = vox
	old_col = mat[i,j,k]
	if previous_modifs is None :
		previous_modifs = ChangeGraph()
	
	#create color histogram
	col_number = color21histo(mat,vox)
	#remove already used color
	col_number.pop(old_col,None)
	for col in previous_modifs.colors(vox) :
		col_number.pop(col,None)
	
	if len(col_number) == 0 :
		return False
	
	#find most abundant color
	col_number = [(nb,col) for col,nb in col_number.iteritems()]
	col_number.sort(reverse = True)
	
	new_col = col_number[0][1]
	
	#change color
	mat[i,j,k] = new_col
	
	#test for modifications
	modifs = previous_modifs + (vox,old_col)
	
	for nei in box27(mat,vox) :
		if not test_few_connected(mat,nei,modifs,logout) :
			#try another color
			logout.write("another try\n")
			logout.flush()
			if not safe_change_color(mat,vox,modifs,logout) :
				#restore state
				mat[i,j,k] = old_col
				return False
	
	#return
	return True

def test_few_connected(mat, vox, previous_modifs, logout) :
	imax,jmax,kmax = mat.shape
	#voxel info
	i,j,k = vox
	####################################
	#
	#	test 6 faces connections
	#
	####################################
	#find color of 6 neighbors
	col_number = color6histo(mat,vox)
	#test connectivity
	if col_number[mat[i,j,k] ] == 0 :
		logout.write("face: (%d,%d,%d)\n" % vox)
		logout.flush()
		#need to change the color of the pixel
		if not safe_change_color(mat,vox,previous_modifs,logout) :
			return False		
	
	####################################
	#
	#	test 12 edges connections
	#
	####################################
	col = mat[i,j,k]
	for axis in xrange(3) :
		for d1,d2 in [(1,1),(-1,1),(-1,-1),(1,-1)] :
			disp = [d1,d2]
			disp.insert(axis,0)
			ni = i + disp[0]
			nj = j + disp[1]
			nk = k + disp[2]
			if (0 <= ni < imax) and (0 <= nj < jmax) and (0 <= nk < kmax) :
				if mat[ni,nj,nk] == col :
					disp1 = [d1,0]
					disp1.insert(axis,0)
					n1i = i + disp1[0]
					n1j = j + disp1[1]
					n1k = k + disp1[2]
					disp2 = [0,d2]
					disp2.insert(axis,0)
					n2i = i + disp2[0]
					n2j = j + disp2[1]
					n2k = k + disp2[2]
					if (mat[n1i,n1j,n1k] != col) \
					   and (mat[n2i,n2j,n2k] != col) :
						#need to change color
						logout.write("edge: (%d,%d,%d)\n" % vox)
						logout.flush()
						if not safe_change_color(mat,(n1i,n1j,n1k),previous_modifs,logout) :
							logout.write("try other side of the edge\n")
							logout.flush()
							if not safe_change_color(mat,(n2i,n2j,n2k),previous_modifs,logout) :
								return False
			
	return True

def filter_few_connected (mat, logout) :
	"""Filter to change the color of possibly
	troublesome voxels.
	"""
	imax,jmax,kmax = mat.shape
	
	logout.write("nb slices: %d\n" % kmax)
	for k in xrange(kmax) :
		logout.write("%d," % k)
		logout.flush()
		for i in xrange(imax) :
			for j in xrange(jmax) :
				if not test_few_connected(mat,(i,j,k),None,logout) :
					raise UserWarning("voxel (%d,%d,%d) cannot be modified" % (i,j,k) )
	logout.write("\n")

