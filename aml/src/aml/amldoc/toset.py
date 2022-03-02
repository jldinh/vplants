# This file has been extracted from AMAPmod documentation (refermanual 18)

"""
ToSet
	Cast type to SET.
Usage
	ToSet(x)
Arguments
	x (ARRAY or SET or LIST)
Returned Object
	The value returned by ToSet has type SET. If x is Undef, returns Undef.
Description
	Transforms any set type (ARRAY, SET or LIST) to a SET whenever possible. It is always possible to cast an ARRAY to a set, but a LIST can only be cast to a set if all its element have identical type.
Note
	This function may be useful to remove duplicated elements from an array (cf. examples)
See Also
	ToArray, 
	ToList, 
	ToString.

Examples
	AML>a = [1,2,2,2,3,2,4,4,4,2,3,2]
	<ARRAY(INT)> [1,2,2,2,3,2,4,4,4,2,3,2]
	AML> b = ToSet(a)
	<SET(INT)>[1,2,3,4]
	AML> # c corresponds to arraya where duplicated element shave
      been removed
	AML> c = ToArray(b)
	<ARRAY(INT)>[1,2,3,4]
"""
