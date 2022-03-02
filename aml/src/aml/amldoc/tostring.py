# This file has been extracted from AMAPmod documentation (refermanual 18)

"""
ToString
	Cast type to STRING.
Usage
	ToString(x)
Arguments
	x (INT, REAL, VTX, DATE, CHAR)
Returned Object
	The value returned by ToString has type STRING. If x is Undef, returns Undef.
Description
	Transforms simple types to ASCII strings.
See Also
	
	ToInt, 
	ToReal.

Examples
	AML>ToString(3)
	<STRING>3
	AML> "AMAPmodv" + ToString(1)
	<STRING> AMAPmod v1
"""
