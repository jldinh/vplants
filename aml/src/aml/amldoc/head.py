# This file has been extracted from AMAPmod documentation (refermanual 18)

"""
Head
	First element of an array or a list.
Usage
	Head(array)
Arguments
	array (ARRAY(T) or LIST(...)). T is any type. If the argument is Undef, returns Undef
Returned Object
	If array has type ARRAY(T), the function returns an element of type T. If array has type LIST(T1,...), the function returns an element of type T1. If the argument is Undef, returns Undef
Description
	Returns the first element of an array or a list. This is equivalent to the expression array@1.
See Also
	
	Array, 
	List, 
	Pos, 
	At, 
	Tail.
	

Examples
    AML>Head([10,11,12,13,14,15])
	<INT> 10
	AML> Head([[1,2],[3,4,5],Undef,[7],[8,9,10]])
	<ARRAY(INT)>[1,2]
	AML> Head(List([3,4,5],"alpha",5.9))
	<ARRAY(INT)>[3,4,5]
"""
