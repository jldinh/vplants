# This file has been extracted from AMAPmod documentation (refermanual 18)

"""
Size
	Gives the number of elements of an array, a set or a list.
Usage
	Size(array)
Arguments
	array (ARRAY(T) or SET(T) or LIST(...)). T is either any type. If the argument is Undef, returns Undef
Returned Object
	If array has type ARRAY(T) or SET(T), the function returns an element of type T. If the argument is Undef, returns Undef
Description
	Returns the number of the elements of array.
See Also
	
	Array, 
	Set, 
	Series, 
	Size.

Examples
	AML>Size([10,11,12,13,14,15])
	<INT> 6
	AML> Size([2,2,Undef,7,1])
	<INT> 5
	AML> Size([2:100])
	<INT> 99
"""
