# This file has been extracted from AMAPmod documentation (refermanual 18)

"""
Comparison operators
	==, !=, <, <=, >, >=
Usage
	x == y
	x != y
	x <= y
Arguments
	x, y (ANY) for logical equality/difference operators == and !=. The arguments must have identical types.
	x, y (INT, REAL, DATE) for order comparison operators <, <=, >, >=
Returned Object
	The returned values are boolean values (type BOOL). Any of the argument may have value Undef.
Description
	The logical truth value of expressions x == y and x != y is defined by the type of object that are being compared (for the precise definition associated with a particular type of object, look at the constructor functions of that object).
See Also
	AML objects constructors, 
	Not, 
	And, 
	Or.
	

Examples
    AML>1 == (9 Mod 4)
	<BOOL> True
	AML> Not(1 == (9 Mod 4))
	<BOOL> False
	AML> Undef == 1
	<BOOL> False
	AML> Undef == Undef
	<BOOL> True
	AML> Date("04/01/97") < Date("05/01/97")
	<BOOL> True
"""
