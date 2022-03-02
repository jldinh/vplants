# This file has been extracted from AMAPmod documentation (refermanual 18)

"""
ToInt
	Cast type to INT.
Usage
	ToInt(x)
Arguments
	x (INT or REAL or VTX or DATE) : a numerical value
Returned Object
	The value returned by ToInt has type INT. If x is Undef, returns Undef.
Description
	Cast a numerical value value to an integer. If x has type REAL or INT, ToInt is equivalent to Truncate. If x has type VTX or DATE, ToInt returns a value corresponding to a unique internal integer code representing the object x. No additional meaning is associated with this internal code.
See Also
	
	Abs, 
	Ceil, 
	Rint, 
	Floor, 
	Truncate, 
	ToInt, 
	ToReal.

Examples
	AML>ToInt(3)
	<INT>3
	AML> ToInt(3.4)
	<REAL>3
	AML> ToInt(3.6)
	<REAL>3
	AML> ToInt(-2.9)
	<REAL>-2
	AML> ToInt(-2.4)
	<REAL>-2
"""
