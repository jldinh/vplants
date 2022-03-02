# This file has been extracted from AMAPmod documentation (refermanual 18)

"""
Plus
	Addition of two arrays.
Usage
	Plus(a1, a2)
Arguments
	a1, a2 (ARRAY(REAL)). These two arrays must have the same dimension.
Returned Object
	The result is an ARRAY(REAL) with the same dimension as a1 and a2. If one of the arguments is Undef, returns Undef
Description
	The function returns the vectorial difference of two arrays of dimension n. If  a1 and a2 then a== Plus(a1, a2) =  
	
Note
	There is no limit on the dimension of the arguments.
See Also
	
	EDist,
	Angle, 
	Norm, 
	VProd, 
	Array.
	

Examples
  AML>Plus([1.2,0.,0.,8.5][0.2,1.,0.,-9.2])
	<ARRAY(REAL)> [1.4,1.,0.,-0.7]
"""
