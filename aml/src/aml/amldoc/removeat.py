# This file has been extracted from AMAPmod documentation (refermanual 18)

"""
RemoveAt
	Removes an element at a given position in an array or a list.
Usage
	RemoveAt(array, i)

Arguments
	array (ARRAY(T) or LIST(...)). T is any type
	i (INT). Position at which the element must be removed. 
        It can have either a positive or a negative value. 
        The argument, 0 < Abs(i) < Size(array).

Returned Object
	If array is of type ARRAY(T), the function returns an element of type ARRAY(T). 
        If array has type LIST, the function returns an element of type (T1,T2,...,TI-1,TI+1,...,TN).

Description
    Removes the element at the ith position in an array or a list. 
    If i has a negative value, the function removes the element at position 
    i with respect to the end of array, i.e. if n is the size of array, 
    it corresponds to position n - i + 1 of array.
Side Effect
    Important: contrary to most functions in AML which leave their argument unchanged, 
    this fonction modifies its array argument. The value returned is the modified argument.

See Also
	
	Array, 
	List, 
	Pos, 
	At, 
	Append, 
	InsertAt.
	

Examples
      AML>a=[10,11,12,13,14,15]
	<ARRAY(INT)>[10,12,13,14,15]
	AML> RemoveAt(a,2)
	<ARRAY(INT)>[10,12,13,14,15]
	AML> a
	<ARRAY(INT)>[10,12,13,14,15]
	AML> RemoveAt([[1,2,3],[10,15]],-1)
	<ARRAY(ARRAY((INT))> [[1,2,3]]
	AML> RemoveAt(List("alpha",[1,2,3],5,True),3)
	<LIST(STRING,ARRAY(INT),BOOL> [alpha,[1,2,3],True]
"""
