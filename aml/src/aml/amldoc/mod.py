# This file has been extracted from AMAPmod documentation (refermanual 18)

"""
Mod
	Modulo function
Usage
	x Mod y
Arguments
	x, y (INT) : integral value
Returned Object
	The value returned by Mod is an INT. If either x or y is Undef, returns Undef.
Description
	Returns the remainder of the integral division of x by y.
Note
	This function is similar to the corresponding double function of the host system (Unix, ...).
See Also
	/

Examples
	AML> 23Mod3
	<INT>2
	AML> -23Mod3
	<REAL> -2
	AML> 23Mod-3
	<REAL> 2
"""
