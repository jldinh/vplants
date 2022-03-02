# This file has been extracted from AMAPmod documentation (refermanual 18)

"""
Var
	Computes the covariance of elements of twi arrays.
Usage
	Var(a1)
Arguments
	a1 (ARRAY(T) or SET(T)). Tis either INT or REAL. Arguments must have the same type.
Returned Object
	If a1 has type ARRAY(T) or SET(T), the function returns an element of type REAL . If the argument is Undef, returns Undef.
Description
	Returns the mean value of the elements of array. If a1 then Var(a1) is the real:
	If a1 contains Undef elements, these elements are considered as Null values.
	
See Also
	
	Array, 
	Set, 
	Series, 
	Size, 
	Edist,
	Angle,
	Norm,
	VProd,
	Plus,
	Times,
	Cov,
	Mean.
	

Examples
	AML>AML> Var([6.5,4.5,4.9,7.2,0.6,4.5])
	<REAL> 4.40333
"""
