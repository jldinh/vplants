from numpy import array,dot,tensordot
from numpy.random import uniform

from openalea.mechanics import triangle_frame,tetrahedron_frame
from common_func import comp

#############################################
#
#	creation functions
#
#############################################
def rvec () :
	v = uniform(-1,1,3)
	v[2] = 0
	return v

def rframe () :
	return triangle_frame(rvec(),rvec(),rvec() )

#############################################
#
#	simple analytical test for triangle frame
#
#############################################
def test_triangle_ana () :
	p0 = (1,1,0)
	p1 = (1,2,0)
	p2 = (0,1,0)
	
	fr = triangle_frame(p0,p1,p2)
	
	assert comp(fr.local_point( (0,2,0) ),(1,1,0) )
	assert comp(fr.global_point( (1,1,0) ),(0,2,0) )
	
	for i in xrange(10) :
		V = uniform(-1,1,3)
		assert comp(fr.global_point(fr.local_point(V) ),V)
		assert comp(fr.local_point(fr.global_point(V) ),V)
	
	assert comp(fr.local_vec( (1,1,0) ),(1,-1,0) )
	assert comp(fr.global_vec( (1,1,0) ),(-1,1,0) )
	
	for i in xrange(10) :
		V = uniform(-1,1,3)
		assert comp(fr.global_vec(fr.local_vec(V) ),V)
		assert comp(fr.local_vec(fr.global_vec(V) ),V)

#############################################
#
#	random test for triangle frame
#
#############################################
def test_triangle_random () :
	for i in xrange(10) :
		fr = triangle_frame(uniform(-1,1,3),
		                    uniform(-1,1,3),
		                    uniform(-1,1,3) )
		
		for j in xrange(10) :
			V = uniform(-1,1,3)
			assert comp(fr.global_point(fr.local_point(V) ),V)
			assert comp(fr.local_point(fr.global_point(V) ),V)
			
			assert comp(fr.global_vec(fr.local_vec(V) ),V)
			assert comp(fr.local_vec(fr.global_vec(V) ),V)

#############################################
#
#	simple analytical test for tetrahedron frame
#
#############################################
def test_tetra_ana () :
	p0 = (1,1,0)
	p1 = (1,2,0)
	p2 = (0,1,0)
	p3 = (0,0,1)
	
	fr = tetrahedron_frame(p0,p1,p2,p3)
	
	assert comp(fr.local_point( (0,2,0) ),(1,1,0) )
	assert comp(fr.global_point( (1,1,0) ),(0,2,0) )
	
	for i in xrange(10) :
		V = uniform(-1,1,3)
		assert comp(fr.global_point(fr.local_point(V) ),V)
		assert comp(fr.local_point(fr.global_point(V) ),V)
	
	assert comp(fr.local_vec( (1,1,0) ),(1,-1,0) )
	assert comp(fr.global_vec( (1,1,0) ),(-1,1,0) )
	
	for i in xrange(10) :
		V = uniform(-1,1,3)
		assert comp(fr.global_vec(fr.local_vec(V) ),V)
		assert comp(fr.local_vec(fr.global_vec(V) ),V)

#############################################
#
#	random test for change of referential of tensor or order 2
#
#############################################
def test_tensor2_random () :
	for i in xrange(10) :
		#create a frame
		fr = rframe()
		
		for j in xrange(10) :
			#create a tensor
			T = uniform(-1,1,(2,2) )
			lT = fr.local_tensor2(T)
			
			assert comp(T,fr.local_tensor2(fr.global_tensor2(T) ) )
			assert comp(T,fr.global_tensor2(fr.local_tensor2(T) ) )
			
			#test with different vectors
			for j in xrange(10) :
				V1 = rvec()
				lV1 = fr.local_vec(V1)
				V2 = rvec()
				lV2 = fr.local_vec(V2)
				
				assert comp(dot(dot(T,V2[:2]),V1[:2]),
				            dot(dot(lT,lV2[:2]),lV1[:2]) )

#############################################
#
#	random test for change of referential of tensor or order 4
#
#############################################
def test_tensor4_random () :
	for i in xrange(10) :
		#create a frame
		fr = rframe()
		
		for j in xrange(10) :
			#create a tensor of order 4
			T = uniform(-1,1,(2,2,2,2) )
			lT = fr.local_tensor2(T)
			
			assert comp(T,fr.local_tensor2(fr.global_tensor2(T) ) )
			assert comp(T,fr.global_tensor2(fr.local_tensor2(T) ) )
			
			#test with different order 2 tensors
			for j in xrange(10) :
				T1 = uniform(-1,1,(2,2) )
				lT1 = fr.local_tensor2(T1)
				
				p1 = tensordot(T,T1,2)
				lp1 = tensordot(lT,lT1,2)
				
				assert comp(p1,fr.global_tensor2(lp1) )


