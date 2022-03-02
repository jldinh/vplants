# This file has been extracted from AMAPmod documentation (refermanual 18)

"""
Foreach
	Iterator.
Usage
	Foreach _x In set : apply(_x)
Arguments
	_x (tied variable). This variable denotes one element of the set object set.
	set (ARRAY(T) or SET(T)). T can be any type.
	apply() (FUNC). This is a function which is used by the iterator.
Returned Object
	If set has type ARRAY(T), the iterator returns an ARRAY. If set has type SET(T), the iterator returns a SET.
Description
	The iterator allows us to browse a set object and to apply to each object _x of the set a given function, apply. This is a very generic way of exploring data bases and computing samples of any things.
See Also
	
	Array, 
	List, 
	Pos, 
	At, 
	Append.
	

Examples
    AML>Foreach _x In [1:5] : _x+1
	<ARRAY(INT)> [2,3,4,5,6]
	AML> Foreach _x In [1:10] : Select(_x, _x/2==0)
	<ARRAY(INT)> [2,4,6,8,10]
	AML> Foreach _x In [1:10] : Select(_x+1,_x/2==0)
	<ARRAY(INT)> [3,5,7,9,11]
"""
