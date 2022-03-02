# This file has been extracted from AMAPmod documentation (refermanual 18)

"""
Cov
	Computes the covairance of elements of two arrays
Usage
	Cov(a1, a2)
Arguments
	a1, a2 (ARRAY(T) or SET(T)). Tis either INT or REAL. Arguments must have the same type.
Returned Object
	If a1 and a2 have type ARRAY(T) or SET(T), the function returns an element of type REAL . If the argument is Undef, returns Undef.
Description
	Returns the mean value of the elements of array. If a1 and a2 then Cov(a1, a2) is the real:
	If a1 or  a2contain Undef elements, these elements are considered as Null values.
	
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
	Var,
	Mean.
	

Examples
	AML>AML> Cov([6.5,4.5,4.9,7.2,0.6,4.5],[7.1,3.9,9.5,18.4,6.7,6.7])
	<INT> 5.18167
"""
