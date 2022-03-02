# This file has been extracted from AMAPmod documentation (refermanual 18)

"""
Sum
	Sum up the elements of an array or a set.
Usage
	Sum(array)
Arguments
	array (ARRAY(T) or SET(T)). T is either INT or REAL. If the argument is Undef, returns Undef
Returned Object
	If array has type ARRAY(T) or SET(T), the function returns an element of type T. If the argument is Undef, returns Undef
Description
	Returns the sum of the elements of array. If array contains Undef elements, these elements are discarded during the Sum operation (they are considered as having Null value).
See Also
	
	Array, 
	Set, 
	Series, 
	Size.

Examples
	AML>Sum([10,11,12,13,14,15])
	<INT> 75
	AML> Sum([2,2,Undef,7,1])
	<INT> 12
	AML> Sum(Foreach _x In [1,10,100] : _x*2)
	<INT> 222
"""
