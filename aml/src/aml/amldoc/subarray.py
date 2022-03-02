# This file has been extracted from AMAPmod documentation (refermanual 18)

"""
SubArray
	Subarray of an array or a list.
Usage
	SubArray(array, i, j)
	SubArray(array, i)
Arguments
	array (ARRAY(T)). T is any type. If the argument is Undef, returns Undef
	i, j (INT). Define the bounds (minimum and maximum index in array) of the subarray. For syntax SubArray(array,i,j), i must be positive, non null and j must be greater than i. For syntax SubArray(array,i), i must be non null, but can have a negative value.
Returned Object
	If array has type ARRAY(T), the function returns an element of type ARRAY(T). If one of the arguments is Undef, returns Undef
Description
	 SubArray(array,i,j) returns the array made of the element of array that have a position between i and j. The elements of the resulting array are in the same order as in array. Let us denote array. Then syntax returns the subarray . If j >n then the result is the subarray .
	Syntax SubArray(array,i) returns the first i element of array if i>0 and the last i elements if i<0. If Abs(i)>n, then the entire array array is returned.
See Also
	
	Array, 
	List, 
	Pos, 
	At, 
	Head, 
	Tail,
	ValueSelect.


Examples
	AML>SubArray([10,11,12,13,14,15],2,4)
	<ARRAY(INT)> [11,12,13]
	AML> SubArray([10,11,12,13,14,15],2,18)
	<ARRAY(INT)> [11,12,13,14,15]
	AML> SubArray([[1,2],[3,4,5],Undef,[7],[8,9,10]],3)
	<ARRAY(ARRAY(INT))>[[1,2],[3,4,5],Undef]
	AML> SubArray([[1,2],[3,4,5],Undef,[7],[8,9,10]],-2)
	<ARRAY(ARRAY(INT))>[[7],[8,9,10]]
"""
