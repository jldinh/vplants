# This file has been extracted from AMAPmod documentation (refermanual 18)

"""
Trigonometric functions
	Sin, Cos, Tan, Acos, Asin, Atan.
Usage
	Cos(x)
	Tan(x)
	Asin(x)
Arguments
	x (INT or REAL)
	Tan argument must be different from  for any positive or negative n.
	Arguments of Acos and Asin must be in the REAL interval [0,1].
Returned Object
	The returned values are REAL values. If the above conditions are not met, Undef is returned. If the argument is Undef, returns Undef.
Description
	These functions are similar to the corresponding double function of the host system (Unix, ...). Type ''man math'' on the host system for more details.
See Also
	Mathematical functions.

Examples
	AML>Cos(Pi/2)
	<REAL>1
	AML> Atan(1)
	<REAL> 0.785398
"""
