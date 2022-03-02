# This file has been extracted from AMAPmod documentation (refermanual 18)

"""
ToArray
	Cast type to ARRAY.
Usage
	ToArray(x)
Arguments
	
	 x (ARRAY or SET or LIST or SEQUENCES or DISCRETE_SEQUENCES or MARKOV_DATA or SEMI-MARKOV_DATA)
	
Returned Object
	The value returned by ToArray has type ARRAY. If x is Undef, returns Undef.
Description
	Transforms any set type (ARRAY, SET or LIST or SEQUENCES) to ARRAY whenever possible. It is always possible to cast a SET to an ARRAY, but a LIST can only be cast to a set if all its element have identical type.
Note
	This function may be useful to remove duplicated elements from an array (cf. examples)
See Also
	
	ToSet, 
	ToList, 
	ToString,
	Sequences.


Examples
	AML>a = [1,2,2,2,3,2,4,4,4,2,3,2]
	<ARRAY(INT)> [1,2,2,2,3,2,4,4,4,2,3,2]
	AML> b = ToSet(a)
	<SET(INT)>[1,2,3,4]
	AML> # c corresponds to arraya where duplicated element shave
      been removed
	AML> c = ToArray(b)
	<ARRAY(INT)> [1,2,3,4]
	AML>s = Sequences([[1,2,3,4],[1,2,3]])
	<SEQUENCES> 1 VARIABLE  2 sequences  cumulative length: 7
	AML>c = ToArray(s)
	<ARRAY(ARRAY(INT))> [[1,2,3,4],[1,2,3]]
"""
