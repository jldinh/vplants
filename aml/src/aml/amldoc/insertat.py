# This file has been extracted from AMAPmod documentation (refermanual 18)

"""
InsertAt
	Inserts an element at a given position in an array or a list.
Usage
	InsertAt(array, elem, i)
Arguments
	array (ARRAY(T) or LIST(...)). T is any type
	elem (T). Element to be inserted. If array is of type ARRAY(T), elem must be of type T.
	i (INT). Position at which the element must be inserted. It can have either a positive or a negative value, such that 0 < Abs(i) &pound; Size(array).
Returned Object
	If array is of type ARRAY(T), the function returns an element of type ARRAY(T). If array has type LIST(T1,T2,...,TN), the function returns an element of type LIST(T1,T2,...,TI-1,T,TI...,TN).
Description
	Inserts an element at the ith position in an array or a list, i.e. after the insertion, element elem is at position i in array. If i has a negative value, the function inserts the element at position i with respect to the end of array, i.e. if n is the size of array, it corresponds to position n- i + 1 of array.
Side Effect
	Important: contrary to most functions in AML which leave their argument unchanged, this fonction modifies its array argument. The value returned is the modified argument.
See Also
	
	Array, 
	List, 
	Pos, 
	At, 
	Append.
	

Examples
	AML>a = [10,11,12,13,14,15]
	<ARRAY(INT)>[10,11,12,13,14,15]
	AML> InsertAt(a,9,1)
	<ARRAY(INT)>[9,10,11,12,13,14,15]
	AML> a
	<ARRAY(INT)>[9,10,11,12,13,14,15]
	AML> InsertAt([10,11,12,13,14,15],9,-1)
	<ARRAY(INT)>[10,11,12,13,14,15,9]
	AML> InsertAt([10,11,12,13,14,15],9,5)
	<ARRAY(INT)>[10,11,12,13,9,14,15]
	AML> InsertAt([10,11,12,13,14,15],9,-5)
	<ARRAY(INT)>[10,11,9,12,13,14,15]
	AML> InsertAt(List("alpha",5,True),[1,2,3],3)
	<LIST(STRING,INT,ARRAY(INT),BOOL> [alpha,5,[1,2,3],True]
"""
