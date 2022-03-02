# This file has been extracted from AMAPmod documentation (refermanual 18)

"""
ToList
	Cast type to LIST.
Usage
	ToList(x)
Arguments
	x (ARRAY or SET or LIST)
Returned Object
	The value returned by ToList has type LIST. If x is Undef, returns Undef.
Description
	Transforms any set type (ARRAY, SET or LIST) to a LIST whenever possible. It is always possible to cast an ARRAY or a SET to a LIST.
See Also
	
	ToArray, 
	ToSet, 
	ToString.

Examples
	AML>a = [1,2,3,4]
	<ARRAY(INT)> [1,2,3,4]
	AML> b = ToList(a)
	<LIST(INT,INT,INT,INT)>[1,2,3,4]
"""
