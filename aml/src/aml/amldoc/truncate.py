# This file has been extracted from AMAPmod documentation (refermanual 18)

"""
Truncate
	Truncate to integer.
Usage
	Truncate(x)
Arguments
	x (INT or REAL) : a numerical value
Returned Object
	The value returned by Truncate has the same type as x. If x is Undef, returns Undef.
Description
	Truncate x to integer.
Note
	This function is similar to the corresponding double function ''trunc'' of the host system (Unix, ...).
See Also
	Abs, 
	Ceil, 
	Rint, 
	Floor, 
	ToInt, 
	ToReal.

Examples
	AML> Truncate(3)
	<INT>3
	AML> Truncate(3.4)
	<REAL>3
	AML> Truncate(3.6)
	<REAL>3
	AML> Truncate(-2.9)
	<REAL>-2
	AML> Truncate(-2.4)
	<REAL>-2
"""
