# This file has been extracted from AMAPmod documentation (refermanual 18)

"""
Min
	Computes the minimum value of the elements of an array or a set.
Usage
	Min(array)
Arguments
	array (ARRAY(T) or SET(T)). T is either INT or REAL. If the argument is Undef, returns Undef
Returned Object
	If array has type ARRAY(T) or SET(T), the function returns an element of type T. If the argument is Undef, returns Undef
Description
	Returns the element whose value is minimum over the set of elements of array. If array contains Undef elements, these elements are discarded.
See Also
	
	Array, 
	Set, 
	Series, 
	Size, 
	Sum, 
	Max.
	

Examples
    AML>Min([10,11,12,13,14,15])
	<INT> 10
	AML> Min([2,2,Undef,7,1])
	<INT> 1
	AML> Min(Foreach _x In [0:Pi:Pi/100] : Cos(_x))
	<REAL> 0
"""
