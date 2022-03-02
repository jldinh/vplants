# This file has been extracted from AMAPmod documentation (refermanual 18)

"""
Mathematical functions
	Sqrt, Power (^), Log, Log10, Exp
Usage
	Sqrt(x)
	Exp(x)
	a ^ y
Arguments
	x, a, y (INT or REAL)
	Sqrt (square root) takes a non-negative argument.
	a ^ y is not defined for a < 0 and y not an integer.
	Arguments of Log and Log10 must be positive.
Returned Object
	The returned values are REAL values. If the above conditions on the argument are not met, Undef is returned. If either argument is Undef, returns Undef.
Description
	These functions are similar to the corresponding double function of the host system (Unix, ...). Type ''man math'' on the host system for more details.
See Also
	Trigonometric functions.

Examples
	AML>Sqrt(81)
	<REAL> 9
	AML> (-34)^5
	<REAL> -4.54354e+07
	AML> (-34)^-5
	<REAL> -2.20093e-08
"""
