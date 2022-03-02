# This file has been extracted from AMAPmod documentation (refermanual 18)

"""
Boolean operators
	True, False, And, Or, Not
Usage
	x And y
	Not(x != True)
	x Or y
Arguments
	True and False (BOOL) are boolean constants.
	x, y (BOOL or INT). If an INT is used, a non-zero value is consired as a True value and 0 is equivalent to False.
Returned Object
	The values by these functions are boolean (type BOOL). Any of the arguments may have value Undef. In this case, the result is always Undef.
Description
	These are classical boolean operators. They are commonly used to make up predicates, i.e. functions that return a boolean value.
See Also
	
	Comparison operators, 
	Select, 
	If-Then-Else, 
	Switch.
	

Examples
    AML>1 And True
	<BOOL> True
	AML> Not(Not(0 Or False))
	<BOOL> False
	AML> Undef And True
    Undef
	AML> # Definition of apredicate
	AML> pred(_x) = If_x > 3 And _x < 10 Then True Else False
	<FUNC> Function
	AML> pred(4)
	<BOOL> True
	AML> pred(11)
	<BOOL> False
"""
