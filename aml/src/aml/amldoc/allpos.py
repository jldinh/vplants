# This file has been extracted from AMAPmod documentation (refermanual 18)

"""
AllPos
	The set of all positions of an element in an array or a list.
Usage
	AllPos(array, element)
Arguments
	array (ARRAY(T) or LIST(T)). T is any type. If the argument is Undef, returns Undef
	element (T). element that is searched for in the array.
      
Returned Object
	The function returns an array of integers ARRAY(INT). If the argument is Undef, returns Undef.
Description
	AllPos returns the set of positions of all the occurences of element in array.
See Also
	
	Array constructor, 
	Tail, 
	At, 
	Head.
	

Examples
	AML>AllPos([10,11,10,13,10,15],10)
	<ARRAY(INT)>[1,3,5]
	AML> AllPos([1,2,3,2,2,3,4,Undef,3],Undef)
	<ARRAY(INT)>[8]
	AML> AllPos([1,2,3,2,2,3,4,Undef,3],7)
	<ARRAY(ANY)>[]
"""
