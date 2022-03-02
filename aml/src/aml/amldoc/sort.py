# This file has been extracted from AMAPmod documentation (refermanual 18)

"""
Sort
	Sorts the order of the elements of an array or a set.
Usage
	Sort(array)
Arguments
	array (ARRAY(T) or SET(...)). T is any type. If the argument is Undef, returns Undef. The elements of array must have a simple type, i.e. T = INT or VTX or REAL or DATE, or CHAR or STRING.
Returned Object
	If array has type ARRAY(T), the function returns an element of type ARRAY(T). If array has type SET(T), the function returns an element of type ARRAY(T). If the argument is Undef, returns Undef
Description
	Returns a sorted array made of all the element of array.
Note
	- If array is a SET, the object returned is not a SET. Rather, it is an ARRAY.
	- The comparison semantics of complex objects is undefined.
See Also
	
	Array, 
	List, 
	Pos, 
	At, 
	Head, 
	Invert.

Examples
	AML>Sort([12,14,12,15,11,13])
	<ARRAY(INT)> [11,12,12,13,14,15]
	AML> Sort([[1,2],[3,4,5],Undef,[7],[8,9,10]])
	<ARRAY(ARRAY(INT))>[[8,9,10],[7],Undef,[3,4,5],[1,2]]
"""
