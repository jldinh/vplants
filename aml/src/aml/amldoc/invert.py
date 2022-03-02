# This file has been extracted from AMAPmod documentation (refermanual 18)

"""
AMAPmod Reference manual
	
	
	
/HEAD>



	
		
	


Invert
	Inverts the order of the elements of an array or a list.
Usage
	Invert(array)
Arguments
	array (ARRAY(T) or LIST(...)). T is any type. If the argument is Undef, returns Undef
Returned Object
	If array has type ARRAY(T), the function returns an element of type ARRAY(T). If array has type LIST(T1,T2,...,TN), the function returns an element of type LIST(TN,...,T2,T1). If the argument is Undef, returns Undef
Description
	Returns the an array or a list made of all the element of array in reverse order.
See Also
	
	Array, 
	List, 
	Pos, 
	At, 
	Head,
	Reverse.
	

Examples
    AML> Invert([10,11,12,13,14,15])
	<ARRAY(INT)> [15,14,13,12,11,10]
	AML> Invert([[1,2],[3,4,5],Undef,[7],[8,9,10]])
	<ARRAY(ARRAY(INT))>[[8,9,10],[7],Undef,[3,4,5],[1,2]]
"""
