# This file has been extracted from AMAPmod documentation (refermanual 18)

"""
Prod
	Computes the product of the elements of an array or a set.
Usage
	Prod(array)
Arguments
	array (ARRAY(T)). T is either INT or REAL. If the argument is Undef, returns Undef
Returned Object
	If array has type ARRAY(T), the function returns an element of type T, with the same number of elements. If the argument is Undef, returns Undef
Description
	Returns the product of the elements of array. Let array=, then the result is .
	If array contains Undef elements, these elements are considered as having value 1 (they do not affect the overall product of other elements).
See Also
	
	Array, 
	Set, 
	Series, 
	Size.
	

Examples
	AML>Prod([1,2,3,4])
	<INT> 24
	AML> Prod([10,11,12,Undef,14,15])
	<INT> 277200
"""
