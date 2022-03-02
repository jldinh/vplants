# This file has been extracted from AMAPmod documentation (refermanual 18)

"""
Tail
	Tail of an array.
Usage
	Tail(array)
Arguments
	array (ARRAY(T) or LIST(...)). T is any type. If the argument is Undef, returns Undef
Returned Object
	If array has type ARRAY(T), the function returns an element of type ARRAY(T). If array has type LIST(T1,T2,...,TN), the function returns an element of type LIST(T2,...,TN). If the argument is Undef, returns Undef
Description
	Returns the an array or a list made of all the element of array except the first element. The elements of the resulting array are in the same order as in array. This is not equivalent to the expression SubArray(array,2,Size(array)) since Tail can take an argument that contains only one or zero elements (which is not the case of the SubArray expression).
See Also
	
	Array, 
	List, 
	Pos, 
	At, 
	Head.


Examples
	AML>Tail([10,11,12,13,14,15])
	<ARRAY(INT)> [11,12,13,14,15]
	AML> Tail([[1,2],[3,4,5],Undef,[7],[8,9,10]])
	<ARRAY(ARRAY(INT))>[[3,4,5],Undef,[7],[8,9,10]]
	AML> Tail([3])
	<ARRAY(ANY))>[]
	AML> Tail([])
	<ARRAY(ANY))>[]
"""
