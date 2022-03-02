# This file has been extracted from AMAPmod documentation (refermanual 18)

"""
Floor
	Integer no greater than.
Usage
	Floor(x)
Arguments
	x (INT or REAL) : a numerical value
Returned Object
	The value returned by Floor has the same type as x. If x is Undef, returns Undef.
Description
	Returns the integer no greater than x.
Note
	This function is similar to the corresponding double function of the host system (Unix, ...).
See Also
	
	Abs, 
	Ceil, 
	Truncate, 
	Rint, 
	ToInt, 
	ToReal.

Examples
    AML> Floor(3)
	<INT>3
	AML> Floor(3.1)
	<REAL>3
	AML> Floor(-3)
	<INT>-3
	AML> Floor(-2.9)
	<REAL>-3
"""
