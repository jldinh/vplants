# This file has been extracted from AMAPmod documentation (refermanual 18)

"""
Ceil
	Integer no less than.
Usage
	Ceil(x)
Arguments
	x (INT or REAL) : a numerical value
Returned Object
	The value returned by Ceil has the same type as x. If x is Undef, returns Undef.
Description
	Returns the integer no less than x.
Note
	This function is similar to the corresponding double function of the host system (Unix, ...).
See Also
	
	Abs, 
	Floor, 
	Truncate, 
	Rint, 
	ToInt, 
	ToReal.
	

Examples
    AML>Ceil(3)
	<INT>3
	AML> Ceil(3.1)
	<REAL>4
	AML> Ceil(-3)
	<INT>-3
	AML> Ceil(-2.9)
	<REAL>-2
"""
