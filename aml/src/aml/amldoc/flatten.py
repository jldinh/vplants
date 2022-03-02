# This file has been extracted from AMAPmod documentation (refermanual 18)

"""
Flatten
	Flattens the structure of nested arrays or sets
Usage
	Flatten(array)
Arguments
	array (ARRAY(T) or SET(T)). T is any type.
Returned Object
	If array has type ARRAY(ARRAY(T)), the function returns an element of type ARRAY(T). If the argument is Undef, returns Undef.
Description
	This function is used to flatten the structure of nested arrays or sets. Let us assmue that array is a nested array: array has the form, where xi is an ARRAY: .
    	The array array can thus be written . Then, the flattened array obtained from array is the ARRAY: 
	
Note
	This function can be applied to any nesting combination of ARRAYs and SETs (cf. example)
See Also
	
	Array, 
	List, 
	Pos, 
	At, 
	Head.
	

Examples
	AML> Flatten([[10,11],[12],[],[13,14,15]])
	<ARRAY(INT)> [10,11,12,13,14,15]
	AML> Flatten(Set([10,11],[12],[],[11,11,12])
	<SET(INT)> [10,11,12]
"""
