# This file has been extracted from AMAPmod documentation (refermanual 18)

"""
Pos
	Position of an element in an array.
Usage
	Pos(array, element)
Arguments
	array (ARRAY(T) or LIST(...)). T is any type. If the argument is Undef, returns Undef
	element (T). Element that is searched for in array.
Returned Object
	The function returns an integer (INT) if element is in array. It returns Undef if not. If the argument is Undef, returns Undef
Description
	Pos returns the position of the first occurence of element in array.
See Also
	
	Array, 
	List, 
	Tail, 
	At, 
	Head.

Examples
	AML>Pos([10,11,12,13,14,15],14)
	<INT>5
	AML> Pos([[1,2],[3,4,5],Undef,[7],[8,9,10]],[3,4,5])
	<INT>2
	AML> Pos([1,2,Undef,2],Undef)
	<INT>3
	AML> Pos([1,2,3],7)
	<UNDEF>Undef
	AML> Pos(List("alpha",True,[1,2,3],7)),True)
	<INT>2
"""
