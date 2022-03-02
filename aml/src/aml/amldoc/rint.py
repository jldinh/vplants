# This file has been extracted from AMAPmod documentation (refermanual 18)

"""
Rint
	Round to nearest integer.
Usage
	Rint(x)
Arguments
	x (INT or REAL) : a numerical value
Returned Object
	The value returned by Rint has the same type as x. If x is Undef, returns Undef.
Description
	Returns the integer nearest to x.
Note
	This function is similar to the corresponding double function of the host system (Unix, ...).
See Also
	
	Abs, 
	Ceil, 
	Truncate, 
	Floor, 
	ToInt, 
	ToReal.

Examples
	AML>Rint(3)
	<INT>3
	AML> Rint(3.4)
	<REAL>3
	AML> Rint(3.5)
	<REAL>4
	AML> Rint(3.6)
	<REAL>4
	AML> Rint(-2.9)
	<REAL>-3
	AML> Rint(-2.5)
	<REAL>-2
	AML> Rint(-2.4)
	<REAL>-2
"""
