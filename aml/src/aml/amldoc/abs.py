# This file has been extracted from AMAPmod documentation (refermanual 18)

"""
Abs
	Absolute value.
  Usage
	Abs(x)
  Arguments
	x (INT or REAL) : a numerical value
  Returned Object
	The value returned by Abs has the same type as x. If x is Undef, returns Undef.
  Description
	Returns the absolute value of x.
  Note
	This function is similar to the corresponding double function of the host system (Unix, ...).
  See Also
	
	Ceil, 
	Floor, 
	Truncate, 
	Rint, 
	ToInt, 
	ToReal.
	
  
  Examples
	AML>Abs(3)
	<INT>3
	AML> Abs(-3)
	<INT>3
	AML> Abs(-3.1)
	<REAL>3.1
"""
