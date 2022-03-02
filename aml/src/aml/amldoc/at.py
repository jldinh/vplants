# This file has been extracted from AMAPmod documentation (refermanual 18)

"""
At
	ith element of an array, @.
Usage
	array@i
Arguments
	array (ARRAY(T) or LIST(...)). T is any type
	i (INT). It can have either a positive or a negative value. It cannot be 0.
Returned Object
	If array has type ARRAY(T), the function returns an element of type T. If array has type LIST(T1,T2,...,TN) the function returns an element of type TI.
Description
	Returns the ith element of an array or a list. If i has a negative value, @ returns the ith element with respect to the end of array, i.e. if n is the size of array, it corresponds to the n-i+1 the element of array.
See Also
	
	ARRAY constructor, 
	Pos.

Examples
    AML>i=[10,11,12,13,14,15]@5
	<INT> 14
	AML> i=[10,11,12,13,14,15]@1
	<INT> 10
	AML> i=[10,11,12,13,14,15]@-1
	<INT> 15
	AML> i=[10,11,12,13,14,15]@-5
	<INT> 11
	AML> l=List("A",3,[1,2,3],True,67,9.8)@3
	<ARRAY(INT)> [1,2,3]
"""
