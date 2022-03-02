# This file has been extracted from AMAPmod documentation (refermanual 18)

"""
Series
	Computes the mathematical series associated with a given sequence of numerical values.
Usage
	Series(array)
Arguments
	array (ARRAY(T)). T is either INT or REAL. If the argument is Undef, returns Undef
Returned Object
	If array has type ARRAY(T), the function returns an element of type ARRAY(T), with the same number of elements. If the argument is Undef, returns Undef
Description
	Returns the mathematical series associated with the sequence of numerical values defined in array. Let array=, then the result is the array whose ith element is defined by . If array contains Undef elements, these elements are considered as having Null value.
See Also
	
	Array, 
	Set, 
	Series, 
	Size, 
	Prod,
	Cumulate.


Examples
	AML>Series([1,2,3,4])
	<ARRAY(INT)> [1,3,6,10]
	AML> Series([10,11,12,Undef,14,15])
	<ARRAY(INT)> [10,21,33,33,47,62]
"""
