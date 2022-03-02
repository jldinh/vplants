# This file has been extracted from AMAPmod documentation (refermanual 18)

"""
Mean
	Computes the mean value of elements of an array.
Usage
	Mean(array)
Arguments
	array (ARRAY(T) or SET(T)). T is either INT or REAL. If the argument is Undef, returns Undef
Returned Object
	If array has type ARRAY(T) or SET(T), the function returns an element of type REAL. If the argument is Undef, returns Undef
Description
	Returns the mean value of the elements of array. If array then Mean(array) is  
	
See Also
	
	Array,
	Set,
	Series,
	Size,
	EDist,
	Angle, 
	Norm, 
	VProd, 
	Plus, 
	Time.
	

Examples
  AML>Mean([10,11,12,13,14,15])
	<REAL> 12.5
	AML> Mean([10,11,12,13,14,Undef,15])
	<REAL> 10.7143
"""
